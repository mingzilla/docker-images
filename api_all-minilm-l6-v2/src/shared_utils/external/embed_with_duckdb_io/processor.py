import duckdb
import pandas as pd
import os
import logging
from typing import Callable
from config import Config
from shared_utils.external.operation_logging.simple_timer import SimplerTimer


def process_duckdb(
    config: Config,
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

            # Get total count from input table
            total_input_rows = input_conn.execute(
                f"SELECT COUNT(*) FROM {config.input_table}"
            ).fetchone()[0]

            logger.info(f"Input table has {total_input_rows} total rows")
            logger.info(f"Will process up to {config.total_rows} rows")

            # Determine actual rows to process
            rows_to_process = min(total_input_rows, config.total_rows)

            # Check if output table exists and get last processed ID for resumeability
            last_processed_id = _get_last_processed_id(output_conn, config)

            if last_processed_id is None:
                # Create output table with VSS-compatible schema
                _create_output_table(output_conn, config)
                logger.info(f"Created output table: {config.output_table}")
                last_processed_id = 0
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

                timer.track(f"fetch_batch_{batch_number}")

                # Extract IDs and texts (maintain order from query)
                batch_ids = [row[0] for row in batch_data]
                batch_texts = [row[1] for row in batch_data]

                # Generate embeddings using the provided callback
                embeddings = embed_callback(batch_texts)

                timer.track(f"model_encode_{batch_number}")

                # Prepare DataFrame for bulk insert
                # Note: DuckDB will automatically convert list[list[float]] to FLOAT[]
                results_df = pd.DataFrame({
                    config.id_column: batch_ids,
                    config.text_column: batch_texts,
                    'embedding': embeddings
                })

                # Bulk insert using high-performance append() method (Rule #8)
                output_conn.append(config.output_table, results_df)

                timer.track(f"bulk_insert_{batch_number}")

                # Update progress tracking
                last_processed_id = batch_ids[-1]  # Last ID from batch (maintains DB order)
                processed_count += len(batch_data)

                # Report progress
                progress_pct = (processed_count / rows_to_process) * 100
                logger.info(
                    f"Batch {batch_number}: Processed {processed_count} / {rows_to_process} "
                    f"records ({progress_pct:.1f}%) | Last ID: {last_processed_id}"
                )

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
            total_time = sum(step['duration'] for step in timer.steps)
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


def _get_last_processed_id(conn: duckdb.DuckDBPyConnection, config: Config):
    """
    Get the last processed ID from output table for resumeability.
    Returns None if table doesn't exist, or the max ID value.
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

    return result[0] if result[0] is not None else 0


def _create_output_table(conn: duckdb.DuckDBPyConnection, config: Config) -> None:
    """
    Create output table with VSS-compatible schema.

    Schema: (id_column, text_column, embedding FLOAT[])
    The FLOAT[] type is compatible with DuckDB's VSS extension for cosine similarity search.
    """

    create_table_sql = f"""
        CREATE TABLE {config.output_table} (
            {config.id_column} INTEGER,
            {config.text_column} TEXT,
            embedding FLOAT[]
        )
    """

    conn.execute(create_table_sql)
