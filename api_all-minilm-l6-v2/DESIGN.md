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
      "output_table": "embedded_texts",
      "batch_size": 15000
    }
    ```

#### `embed.py` (New Python Script - Thin Wrapper)
This script will be the entry point for the embedding process.

*   **Purpose:** Load the embedding model and configuration, then delegate the DuckDB processing to the shared utility.
*   **Dependencies:** `torch`, `sentence-transformers`, `json`, `os`, `src.config.Config`, and the new `src.shared_utils.external.duckdb_processor.duckdb_embed_processor` utility.

#### `src/shared_utils/external/duckdb_processor/duckdb_embed_processor.py` (New Python Utility Module)
This module will contain the core, reusable DuckDB processing logic.

*   **Purpose:** To handle all DuckDB I/O, batching, and orchestrate the transformation by invoking a provided callback function.
*   **Dependencies:** `duckdb`, `src.shared_utils.external.operation_logging.simple_timer.SimplerTimer`, `os`, `logging`, `typing.Callable`.
*   **Key Function:** `process_duckdb(config: src.config.Config, embed_callback: Callable[[list[str]], list[list[float]]])`

#### `embed.sh` (New Shell Script)
A wrapper script to simplify execution.

*   **Purpose:** To configure and run the Docker container and the `embed.py` script with the correct parameters.
*   **Logic:**
    1.  Uses `docker run` (or `docker-compose run`) to execute `embed.py` inside the container.
    2.  Crucially, it will mount the current directory into the container (e.g., `/app/`) so the script can access `config.json` and the DuckDB files.

#### `Dockerfile`
The existing Dockerfile will require minor modifications.

*   **Changes:**
    1.  Add `duckdb` to `requirements.txt`.
    2.  Add `COPY src/embed.py /app/src/` to include the new entry point script.
    3.  Add `COPY src/shared_utils/external/duckdb_processor/ /app/src/shared_utils/external/duckdb_processor/` to include the utility module.
    4.  Ensure `COPY src/config.py /app/src/` is present or added.

## 3. Execution Workflow

1.  The user places `input.duckdb` and `config.json` in the directory.
2.  The user executes `./embed.sh`.
3.  The script starts the Docker container, mounting the local directory.
4.  Inside the container, `embed.py` runs.
5.  `embed.py` loads `config.json` using `src.config.Config` and the embedding model.
6.  It defines a `callback function` that knows how to use the model to embed a list of texts.
7.  It then calls `src.shared_utils.external.duckdb_processor.duckdb_embed_processor.process_duckdb()` with the configuration object and the callback function.
8.  The utility handles all DuckDB I/O, batching, calls the callback for each batch, and writes the results.
9.  The script finishes, and the container stops. `output.duckdb` is available on the host machine.

## 4. Implementation Plan for `embed.py` (The "Glue" Script)

1.  **Setup:**
    *   Import necessary libraries (`json`, `os`, `torch`, `sentence_transformers`, `src.config.Config`, `src.shared_utils.external.duckdb_processor.duckdb_embed_processor`).
    *   Define `MODEL_NAME`.
    *   Load `config.json` using `config_obj = Config('config.json')`.

2.  **Model Loading:**
    *   Load the `sentence-transformers` model, explicitly placing it on the `cuda` device if available.

3.  **Callback Definition:**
    *   Define the callback function that will be passed to the utility. This function will close over the loaded `model`.
    ```python
    def embed_texts_callback(texts: list[str]) -> list[list[float]]:
        embeddings = model.encode(
            texts,
            convert_to_tensor=False,
            normalize_embeddings=True
        )
        return embeddings.tolist()
    ```

4.  **Delegate to Utility:**
    *   Call `src.shared_utils.external.duckdb_processor.duckdb_embed_processor.process_duckdb(config_obj, embed_texts_callback)`.

## 5. Implementation Plan for `duckdb_embed_processor.py` (Core Logic)

This module will contain the detailed steps for DuckDB I/O, batching, and invoking the provided callback.

1.  **Function Signature:**
    ```python
    from typing import Callable

    def process_duckdb(
        config: src.config.Config,
        embed_callback: Callable[[list[str]], list[list[float]]],
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
    *   Integrate `src.shared_utils.external.operation_logging.simple_timer.SimplerTimer` to track overall and batch processing times.
    *   Implement resumeability: Before starting the main loop, query `output.duckdb` to find the last successfully processed `id_column` value. Adjust the initial `OFFSET` for the input query.
    *   Use a `WHILE` or `FOR` loop with `OFFSET` and `LIMIT` clauses to pull data from the input table.
    *   **`SELECT {id_column}, {text_column} FROM {input_table} ORDER BY {id_column} LIMIT {config.batch_size} OFFSET {current_offset}`**
    *   In each loop iteration:
        a. Fetch the batch of data into a Pandas DataFrame or list of tuples.
        b. Extract the text column into a list.
        c. Call `embeddings = embed_callback(texts)` to generate the embeddings.
        d. Prepare the results for insertion, combining the IDs, original text, and the new embedding vectors.
        e. Use a high-performance bulk insert pattern (e.g., `connection.append()` with a Pandas DataFrame or the `register() + INSERT` pattern) to save the batch to the output table.
        f. Print a progress update (e.g., "Processed 15000 / 10000000 records...").

## 6. Reusability and Maintainability

*   The `duckdb_embed_processor.py` module is now truly model-agnostic. It only requires a callback function that transforms a list of strings into a list of vectors.
*   To use this utility with a different embedding model (e.g., one that calls an API), you would create a new `embed.py` script for that model, define a different callback function, and reuse the `duckdb_embed_processor` without any changes.
*   Updates to the core DuckDB processing logic only need to be made in this single utility module.