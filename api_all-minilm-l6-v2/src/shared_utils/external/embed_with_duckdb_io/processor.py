import duckdb
import pandas as pd
import os
import logging
from typing import Callable
from config import Config
from shared_utils.external.operation_logging.simple_timer import SimplerTimer
import json


class EmbedConfig:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        with open(self.config_path, 'r') as f:
            config_data = json.load(f)

        # Assign properties dynamically from config_data
        for key, value in config_data.items():
            setattr(self, key, value)

        # Validate essential fields
        required_fields = [
            "input_db_path",
            "output_db_path",
            "input_table",
            "id_column",
            "text_column",
            "output_table",
            "batch_size",
            "total_rows",
            "embedding_dimension"
        ]
        for field in required_fields:
            if not hasattr(self, field):
                raise ValueError(f"Missing required config field: {field}")

        # Ensure batch_size is a positive integer
        if not isinstance(self.batch_size, int) or self.batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

        # Ensure total_rows is a positive integer
        if not isinstance(self.total_rows, int) or self.total_rows <= 0:
            raise ValueError("total_rows must be a positive integer.")

        # Ensure embedding_dimension is a positive integer
        if not isinstance(self.embedding_dimension, int) or self.embedding_dimension <= 0:
            raise ValueError("embedding_dimension must be a positive integer.")


def process_duckdb(
        config: EmbedConfig,
        embed_callback: Callable[[list[str]], list[list[float]]]
) -> None:
    """
    Process a DuckDB file by reading text data, applying an embedding transformation,
    and writing results to an output DuckDB file.

    This function is model-agnostic and reusable across different embedding models.
    The actual embedding logic is provided via the embed_callback parameter.

    Features:
    - Resumeability: Automatically detects last processed ID and continues from there
    - Consistent ordering: Uses ORDER BY for all queries to ensure data integrity
    - High-performance bulk inserts: Uses DuckDB's append() method
    - Progress tracking: Reports progress and timing for each batch
    - Total rows limit: Respects config.total_rows to limit processing

    Args:
        config: Configuration object with database paths, table names, columns, and batch settings
        embed_callback: Function that takes list[str] and returns list[list[float]]
                       This encapsulates the embedding model logic

    Raises:
        FileNotFoundError: If input database file doesn't exist
        ValueError: If input table or columns don't exist
    """

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    with SimplerTimer("Batch Embedding Process") as timer:

        # Validate input database exists
        if not os.path.exists(config.input_db_path):
            raise FileNotFoundError(f"Input database not found: {config.input_db_path}")

        # Connect to databases
        input_conn = duckdb.connect(database=config.input_db_path, read_only=True)
        output_conn = duckdb.connect(database=config.output_db_path, read_only=False)

        timer.track("initialization")

        try:
            # Validate input table and columns exist
            _validate_input_table(input_conn, config)

            # Get the data type of the ID column
            id_column_type = _get_column_type(input_conn, config.input_table, config.id_column)
            logger.info(f"ID column '{config.id_column}' type: {id_column_type}")

            # Get total count from input table
            total_input_rows = input_conn.execute(
                f"SELECT COUNT(*) FROM {config.input_table}"
            ).fetchone()[0]

            logger.info(f"Input table has {total_input_rows} total rows")
            logger.info(f"Will process up to {config.total_rows} rows")

            # Determine actual rows to process
            rows_to_process = min(total_input_rows, config.total_rows)

            # Check if output table exists and get last processed ID for resumeability
            last_processed_id = _get_last_processed_id(output_conn, config, id_column_type)

            if last_processed_id is None:
                # Create output table with VSS-compatible schema
                _create_output_table(output_conn, config, id_column_type)
                logger.info(f"Created output table: {config.output_table}")
                # Set initial value based on column type
                last_processed_id = _get_initial_value_for_type(id_column_type)
                processed_count = 0
            else:
                # Get count of already processed rows
                processed_count = output_conn.execute(
                    f"SELECT COUNT(*) FROM {config.output_table}"
                ).fetchone()[0]
                logger.info(f"Resuming from ID {last_processed_id} ({processed_count} rows already processed)")

            timer.track("setup_and_validation")

            # Main processing loop
            batch_number = 0

            while processed_count < rows_to_process:
                batch_number += 1

                # Create a timer for this batch to track detailed timing
                with SimplerTimer() as batch_timer:
                    # Calculate how many rows to fetch in this batch
                    remaining_rows = rows_to_process - processed_count
                    current_batch_size = min(config.batch_size, remaining_rows)

                    # Fetch batch with ORDER BY for consistent ordering (critical for data integrity)
                    batch_query = f"""
                        SELECT {config.id_column}, {config.text_column}
                        FROM {config.input_table}
                        WHERE {config.id_column} > ?
                        ORDER BY {config.id_column} ASC
                        LIMIT ?
                    """

                    batch_data = input_conn.execute(
                        batch_query,
                        [last_processed_id, current_batch_size]
                    ).fetchall()

                    if not batch_data:
                        logger.info("No more data to process")
                        break

                    batch_timer.track("sql_read")

                    # Extract IDs and texts (maintain order from query)
                    batch_ids = [row[0] for row in batch_data]
                    batch_texts = [row[1] for row in batch_data]

                    batch_timer.track("processing")

                    # Generate embeddings using the provided callback
                    embeddings = embed_callback(batch_texts)

                    # Validate embedding dimension on first batch
                    if batch_number == 1 and len(embeddings) > 0:
                        actual_dimension = len(embeddings[0])
                        if actual_dimension != config.embedding_dimension:
                            raise ValueError(
                                f"Embedding dimension mismatch! "
                                f"Config specifies {config.embedding_dimension} but model returned {actual_dimension}. "
                                f"Please update embedding_dimension in config.json to {actual_dimension}."
                            )
                        logger.info(f"Embedding dimension validated: {actual_dimension}")

                    batch_timer.track("embedding")

                    # Prepare DataFrame for bulk insert
                    # Note: DuckDB will automatically convert list[list[float]] to FLOAT[dimension]
                    results_df = pd.DataFrame({
                        config.id_column: batch_ids,
                        config.text_column: batch_texts,
                        'embedding': embeddings
                    })

                    # Bulk insert using high-performance append() method (Rule #8)
                    output_conn.append(config.output_table, results_df)

                    batch_timer.track("db_write_bulk")

                    # Update progress tracking
                    last_processed_id = batch_ids[-1]  # Last ID from batch (maintains DB order)
                    processed_count += len(batch_data)

                    # Report progress
                    progress_pct = (processed_count / rows_to_process) * 100
                    logger.info(
                        f"Batch {batch_number}: Processed {processed_count} / {rows_to_process} "
                        f"records ({progress_pct:.1f}%) | Last ID: {last_processed_id}"
                    )

                    # Report detailed timing breakdown
                    timing_summary = batch_timer.get_timing_summary()
                    timing_str = ", ".join([
                        f"{step['step']}={step['duration_ms'] / 1000:.4f}"
                        for step in timing_summary
                    ])
                    logger.info(f"  {timing_str}")

            timer.track("processing_complete")

            # Final summary
            logger.info("=" * 80)
            logger.info(f"Processing complete!")
            logger.info(f"Total records processed: {processed_count}")
            logger.info(f"Output database: {config.output_db_path}")
            logger.info(f"Output table: {config.output_table}")

            # Get timing summary
            timing_summary = timer.get_timing_summary()
            logger.info("\nPerformance Summary:")
            logger.info(timing_summary)

            # Calculate throughput
            # Find the 'total' entry in timing_summary
            total_time_ms = next((step['duration_ms'] for step in timing_summary if step['step'] == 'total'), 0)
            total_time = total_time_ms / 1000  # Convert to seconds
            if total_time > 0:
                throughput = processed_count / total_time
                logger.info(f"\nThroughput: {throughput:.2f} items/second")

            logger.info("=" * 80)

        finally:
            input_conn.close()
            output_conn.close()


def _validate_input_table(conn: duckdb.DuckDBPyConnection, config: Config) -> None:
    """Validate that input table and required columns exist."""

    # Check if table exists
    tables = conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_name = ?",
        [config.input_table]
    ).fetchall()

    if not tables:
        raise ValueError(f"Input table '{config.input_table}' does not exist")

    # Check if required columns exist
    columns = conn.execute(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = ?",
        [config.input_table]
    ).fetchall()

    column_names = [col[0] for col in columns]

    if config.id_column not in column_names:
        raise ValueError(f"ID column '{config.id_column}' not found in table '{config.input_table}'")

    if config.text_column not in column_names:
        raise ValueError(f"Text column '{config.text_column}' not found in table '{config.input_table}'")


def _get_last_processed_id(conn: duckdb.DuckDBPyConnection, config: Config, id_column_type: str):
    """
    Get the last processed ID from output table for resumeability.
    Returns None if table doesn't exist, or the max ID value.
    If table exists but is empty, returns appropriate initial value for the type.
    """

    # Check if output table exists
    tables = conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_name = ?",
        [config.output_table]
    ).fetchall()

    if not tables:
        return None

    # Get max ID (using ORDER BY id_column for consistency)
    result = conn.execute(
        f"SELECT MAX({config.id_column}) FROM {config.output_table}"
    ).fetchone()

    return result[0] if result[0] is not None else _get_initial_value_for_type(id_column_type)


def _create_output_table(conn: duckdb.DuckDBPyConnection, config: Config, id_column_type: str) -> None:
    """
    Create output table with VSS-compatible schema.

    Schema: (id_column, text_column, embedding FLOAT[dimension])
    The FLOAT[dimension] type is compatible with DuckDB's VSS extension for cosine similarity search.
    The id_column type matches the source table's type.
    """

    create_table_sql = f"""
        CREATE TABLE {config.output_table} (
            {config.id_column} {id_column_type},
            {config.text_column} TEXT,
            embedding FLOAT[{config.embedding_dimension}]
        )
    """

    conn.execute(create_table_sql)


def _get_column_type(conn: duckdb.DuckDBPyConnection, table_name: str, column_name: str) -> str:
    """
    Get the data type of a column from the database schema.

    Args:
        conn: DuckDB connection
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        Data type as a string (e.g., 'INTEGER', 'VARCHAR', 'BIGINT')
    """
    result = conn.execute(
        """
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = ? AND column_name = ?
        """,
        [table_name, column_name]
    ).fetchone()

    if result is None:
        raise ValueError(f"Column '{column_name}' not found in table '{table_name}'")

    return result[0]


def _get_initial_value_for_type(data_type: str):
    """
    Get an appropriate initial value for comparison based on the column data type.

    For numeric types: returns 0
    For string types: returns '' (empty string)

    Args:
        data_type: The SQL data type (e.g., 'INTEGER', 'VARCHAR', 'BIGINT')

    Returns:
        Initial value compatible with the data type
    """
    # Normalize type to uppercase for comparison
    data_type_upper = data_type.upper()

    # Numeric types
    if any(numeric_type in data_type_upper for numeric_type in [
        'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
        'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL'
    ]):
        return 0

    # String types
    if any(string_type in data_type_upper for string_type in [
        'CHAR', 'VARCHAR', 'TEXT', 'STRING'
    ]):
        return ''

    # Default to empty string for unknown types (safe fallback)
    return ''
