# Design Document: High-Throughput Batch Embedding (Shared Utility Approach)

This document outlines the design for a script-based workflow to perform large-scale batch embeddings efficiently, using a Docker container with GPU acceleration. This approach prioritizes high performance and reusability through a shared Python utility module.

## 1. Overview

The goal is to replace the API-based embedding process with a more performant, script-driven one. The core DuckDB processing logic will be encapsulated in a reusable Python utility module. A thin `embed.py` script will orchestrate the process, loading the embedding model and then calling this utility to read data from a DuckDB file, generate embeddings using the GPU, and write the results to a new DuckDB file.

This approach eliminates the primary performance bottleneck (JSON serialization/deserialization) while providing a clear separation of concerns through a well-defined utility interface.

## 2. Components

#### `config.json`
A JSON file to configure the input and output of the embedding process.

*   **Purpose:** To make the script adaptable without changing the code.
*   **Example Structure:**
    ```json
    {
      "input_db_path": "input.duckdb",
      "output_db_path": "output.duckdb",
      "input_table": "source_texts",
      "id_column": "document_id",
      "text_column": "content",
      "output_table": "embedded_texts"
    }
    ```

#### `embed.py` (New Python Script - Thin Wrapper)
This script will be the entry point for the embedding process.

*   **Purpose:** Load the embedding model and configuration, then delegate the DuckDB processing to the shared utility.
*   **Dependencies:** `torch`, `sentence-transformers`, `duckdb` (indirectly via utility), `json`, `os`, and the new `duckdb_embed_processor` utility.

#### `src/shared_utils/external/duckdb_processor/duckdb_embed_processor.py` (New Python Utility Module)
This module will contain the core, reusable DuckDB processing logic.

*   **Purpose:** To handle all DuckDB I/O, batching, and orchestrate the embedding calls using a provided model instance.
*   **Dependencies:** `duckdb`, `SimplerTimer` (from `src/shared_utils/external/operation_logging/simple_timer.py`), `os`, `logging`.
*   **Key Function:** `process_duckdb_for_embeddings(config: dict, model_instance: SentenceTransformer, batch_size: int)`

#### `embed.sh` (New Shell Script)
A wrapper script to simplify execution.

*   **Purpose:** To configure and run the Docker container and the `embed.py` script with the correct parameters.
*   **Logic:**
    1.  Reads a `BATCH_SIZE` environment variable, with a sensible default.
    2.  Prints the `BATCH_SIZE` being used and reminds the user about `check_benchmark.sh`.
    3.  Uses `docker run` (or `docker-compose run`) to execute `embed.py` inside the container.
    4.  Crucially, it will mount the current directory into the container (e.g., `/data`) so the script can access `config.json` and the DuckDB files.

#### `Dockerfile`
The existing Dockerfile will require minor modifications.

*   **Changes:**
    1.  Add `duckdb` to `requirements.txt`.
    2.  Add `COPY embed.py ./` to include the new entry point script.
    3.  Add `COPY src/shared_utils/external/duckdb_processor/ /app/src/shared_utils/external/duckdb_processor/` to include the utility module.

## 3. Execution Workflow

1.  The user places `input.duckdb` and `config.json` in the directory.
2.  The user executes `./embed.sh`.
3.  The script starts the Docker container, mounting the local directory.
4.  Inside the container, `embed.py` runs.
5.  `embed.py` loads `config.json` and the embedding model.
6.  It then calls `duckdb_embed_processor.process_duckdb_for_embeddings()` with the configuration, model instance, and batch size.
7.  The utility handles all DuckDB I/O, batching, embedding, and result insertion.
8.  The script finishes, and the container stops. `output.duckdb` is available on the host machine.

## 4. Implementation Plan for `embed.py` (Thin Wrapper)

1.  **Setup:**
    *   Import necessary libraries (`json`, `os`, `torch`, `sentence_transformers`, `duckdb_embed_processor`).
    *   Define `MODEL_NAME`.
    *   Get `BATCH_SIZE` from an environment variable (with a default).
    *   Load `config.json`.

2.  **Model Loading:**
    *   Load the `sentence-transformers` model, explicitly placing it on the `cuda` device if available.

3.  **Delegate to Utility:**
    *   Call `duckdb_embed_processor.process_duckdb_for_embeddings(config, model, BATCH_SIZE)`.

## 5. Implementation Plan for `duckdb_embed_processor.py` (Core Logic)

This module will contain the detailed steps for DuckDB I/O, batching, calling `model_instance.encode()`, and inserting results.

1.  **Function Signature:**
    ```python
    def process_duckdb_for_embeddings(
        config: dict,
        model_instance: SentenceTransformer,
        batch_size: int,
        logger: logging.Logger
    ):
        # ... implementation ...
    ```

2.  **Database Handling:**
    *   Connect to the input DuckDB file (read-only).
    *   Connect to the output DuckDB file (a new file will be created).
    *   Query the input table to get the total row count for progress tracking.
    *   Create the output table in the output database with the schema: `(id_column, text_column, vector_column FLOAT[])`.

3.  **Processing Loop:**
    *   Integrate `SimplerTimer` to track overall and batch processing times.
    *   Implement resumeability: Before starting the main loop, query `output.duckdb` to find the last successfully processed `id_column` value. Adjust the initial `OFFSET` for the input query.
    *   Use a `WHILE` or `FOR` loop with `OFFSET` and `LIMIT` clauses to pull data from the input table.
    *   **`SELECT {id_column}, {text_column} FROM {input_table} ORDER BY {id_column} LIMIT {BATCH_SIZE} OFFSET {current_offset}`**
    *   In each loop iteration:
        a. Fetch the batch of data into a Pandas DataFrame or list of tuples.
        b. Extract the text column into a list.
        c. Call `model_instance.encode(texts, convert_to_tensor=False, normalize_embeddings=True)` to generate the embeddings.
        d. Prepare the results for insertion, combining the IDs, original text, and the new embedding vectors.
        e. Use `duckdb_connection.executemany()` to perform a fast, bulk insert of the batch into the output table.
        f. Print a progress update (e.g., "Processed 15000 / 10000000 records...").

## 6. Reusability and Maintainability

*   The `duckdb_embed_processor.py` module is designed to be self-contained and model-agnostic. It accepts the `model_instance` as an argument, meaning it doesn't care *which* `SentenceTransformer` model is being used, only that it provides an `encode` method.
*   To use this utility with a different embedding model, simply copy the `duckdb_processor` directory into the new model's `src/shared_utils/external/` path. The `embed.py` script in that new model's project would then import and use it.
*   Updates to the core DuckDB processing logic only need to be made in this single utility module.