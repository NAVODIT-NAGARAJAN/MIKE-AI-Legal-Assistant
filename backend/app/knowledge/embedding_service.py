"""
LegalEase AI - Embedding Service
===================================
Generates vector embeddings using local sentence-transformers models.

No external API calls — embeddings are computed locally.
Model: all-MiniLM-L6-v2 (default) — 384 dimensions, fast, high quality.

Design:
    - Lazy initialization: model loads on first use.
    - Batch processing for efficiency.
    - Model name configurable via settings.embedding_model.
"""

from functools import lru_cache
from typing import Optional

from app.config.settings import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

# Lazy-loaded model instance
_model = None


def _get_model():
    """Load and cache the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            log.info(f"Loading embedding model: {settings.embedding_model}")
            _model = SentenceTransformer(settings.embedding_model)
            log.info(f"Embedding model loaded — dim={_model.get_sentence_embedding_dimension()}")
        except Exception as exc:
            log.error(f"Failed to load embedding model: {exc}")
            raise RuntimeError(f"Cannot load embedding model '{settings.embedding_model}': {exc}")
    return _model


def generate_embedding(text: str) -> list[float]:
    """
    Generate a single embedding vector for a text string.

    Args:
        text: Input text to embed.

    Returns:
        List of floats representing the embedding vector.

    Raises:
        RuntimeError: If the embedding model cannot be loaded.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """
    Generate embeddings for a list of texts in batches.

    Args:
        texts: List of text strings to embed.
        batch_size: Number of texts per batch (default 32).

    Returns:
        List of embedding vectors, same order as input texts.

    Raises:
        ValueError: If texts list is empty.
        RuntimeError: If the embedding model cannot be loaded.
    """
    if not texts:
        raise ValueError("texts list cannot be empty.")

    model = _get_model()
    log.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}.")

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(
            batch,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        all_embeddings.extend(batch_embeddings.tolist())
        log.debug(f"Embedded batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")

    log.info(f"Generated {len(all_embeddings)} embeddings.")
    return all_embeddings


def get_embedding_dimension() -> int:
    """Return the dimension of the embedding vectors."""
    model = _get_model()
    return model.get_sentence_embedding_dimension()
