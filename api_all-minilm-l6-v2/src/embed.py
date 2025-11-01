"""
Batch Embedding Entry Point

This script loads the sentence-transformers model and processes a DuckDB file
to generate embeddings using GPU acceleration.

The core DuckDB I/O logic is delegated to the reusable processor module,
making this script a thin wrapper that only handles model-specific concerns.

Usage:
    python -m embed

Requirements:
    - config.json must exist in /app/data/ (mounted volume in Docker)
    - Input DuckDB file must exist at the path specified in config.json
"""

import os
import torch
import logging
from sentence_transformers import SentenceTransformer

from config import Config
from shared_utils.external.embed_with_duckdb_io.processor import process_duckdb


# Model configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    """Main entry point for batch embedding process."""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Starting Batch Embedding Process")
    logger.info("=" * 80)

    # Load configuration from environment variable
    config_path = os.getenv("CONFIG_PATH", "/app/data/config.json")
    logger.info(f"Loading configuration from: {config_path}")

    try:
        config = Config(config_path)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        logger.error("Please ensure config.json is in the mounted data directory")
        raise
    except ValueError as e:
        logger.error(f"Configuration validation error: {e}")
        raise

    # Prepend /app/data/ to relative paths (user shouldn't know about Docker internals)
    data_dir = "/app/data"
    if not os.path.isabs(config.input_db_path):
        config.input_db_path = os.path.join(data_dir, config.input_db_path)
    if not os.path.isabs(config.output_db_path):
        config.output_db_path = os.path.join(data_dir, config.output_db_path)

    logger.info(f"Configuration loaded successfully")
    logger.info(f"  Input DB: {config.input_db_path}")
    logger.info(f"  Output DB: {config.output_db_path}")
    logger.info(f"  Input Table: {config.input_table}")
    logger.info(f"  Output Table: {config.output_table}")
    logger.info(f"  Batch Size: {config.batch_size}")
    logger.info(f"  Total Rows Limit: {config.total_rows}")
    logger.info(f"  Embedding Dimension: {config.embedding_dimension}")

    # Detect device and load model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    if device == "cpu":
        logger.warning("CUDA not available! Running on CPU will be significantly slower.")

    logger.info(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, device=device)
    logger.info(f"Model loaded successfully on {device}")

    # Get and log the actual model embedding dimension
    model_dimension = model.get_sentence_embedding_dimension()
    logger.info(f"Model embedding dimension: {model_dimension}")

    if model_dimension != config.embedding_dimension:
        logger.warning(
            f"WARNING: Config embedding_dimension ({config.embedding_dimension}) "
            f"does not match model dimension ({model_dimension}). "
            f"This will cause an error during processing."
        )

    # Define embedding callback function
    # This encapsulates all model-specific logic
    def embed_texts_callback(texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        embeddings = model.encode(
            texts,
            convert_to_tensor=False,  # Return as numpy array
            normalize_embeddings=True,  # Normalize for cosine similarity
            show_progress_bar=False  # Disable per-batch progress bar
        )
        return embeddings.tolist()

    # Delegate to the reusable DuckDB processor
    logger.info("Starting DuckDB processing...")
    try:
        process_duckdb(config, embed_texts_callback)
        logger.info("Batch embedding process completed successfully!")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise


if __name__ == "__main__":
    main()
