"""
Embedding tool using sentence-transformers/all-MiniLM-L6-v2.
Provides vector embeddings for semantic search in the FAISS knowledge base.
"""

import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

_embedding_model = None


def get_embedding_model():
    """Load the sentence transformer model (singleton)."""
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model

    from config.settings import EMBEDDING_MODEL_NAME

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")

    from sentence_transformers import SentenceTransformer

    _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("Embedding model loaded successfully")
    return _embedding_model


def embed_text(text: str) -> np.ndarray:
    """
    Generate a vector embedding for a single text string.

    Args:
        text: Input text to embed

    Returns:
        numpy array of shape (embedding_dim,)
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts in batch.

    Args:
        texts: List of input strings

    Returns:
        numpy array of shape (n_texts, embedding_dim)
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    )
    return embeddings


def get_embedding_dimension() -> int:
    """Return the embedding dimension of the loaded model."""
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()
