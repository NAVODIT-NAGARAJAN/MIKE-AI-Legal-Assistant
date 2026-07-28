"""
LegalEase AI - ChromaDB Client
================================
Manages the persistent ChromaDB connection and collection lifecycle.

Design:
    - Singleton pattern via module-level cached client.
    - Persistent storage: chroma_db_path from settings.
    - Collection: legalease_knowledge (from settings).
    - Embedding function: sentence-transformers (all-MiniLM-L6-v2 by default).

Usage:
    from app.knowledge.chroma_client import get_chroma_collection
    collection = get_chroma_collection()
"""

from functools import lru_cache
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config.settings import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

# Module-level cached client instance
_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Return the singleton ChromaDB persistent client.
    Creates on first call; reuses on subsequent calls.
    """
    global _client
    if _client is None:
        log.info(f"Initializing ChromaDB client at path: {settings.chroma_db_path}")
        _client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        log.info("ChromaDB client initialized successfully.")
    return _client


def get_chroma_collection() -> chromadb.Collection:
    """
    Return (or create) the knowledge base collection.
    Uses cosine similarity for semantic search.

    Returns:
        ChromaDB Collection for the legal knowledge base.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    log.debug(
        f"Collection '{settings.chroma_collection_name}' ready — "
        f"{collection.count()} documents."
    )
    return collection


def reset_chroma_collection() -> None:
    """
    Delete and recreate the knowledge base collection.
    DESTRUCTIVE — used only for re-ingestion or testing.
    """
    client = get_chroma_client()
    try:
        client.delete_collection(name=settings.chroma_collection_name)
        log.warning(f"Collection '{settings.chroma_collection_name}' deleted.")
    except Exception:
        pass  # Collection may not exist yet
    client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    log.info(f"Collection '{settings.chroma_collection_name}' recreated.")


def get_collection_count() -> int:
    """Return number of documents in the collection."""
    return get_chroma_collection().count()
