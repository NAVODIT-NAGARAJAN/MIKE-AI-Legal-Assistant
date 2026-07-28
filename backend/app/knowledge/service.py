"""
LegalEase AI - Knowledge Base Service
========================================
Orchestrates ingestion and retrieval of legal knowledge.

Responsibilities:
    - Ingest documents: process → embed → store in ChromaDB.
    - Retrieve relevant chunks: embed query → semantic search.
    - Provide collection status information.

This is the only layer that knows about both ChromaDB and embeddings.
"""

import uuid
from typing import Optional

from app.knowledge.chroma_client import (
    get_chroma_collection,
    get_collection_count,
    reset_chroma_collection,
)
from app.knowledge.embedding_service import generate_embedding, generate_embeddings_batch
from app.knowledge.text_processor import TextChunk, process_all_documents, process_document
from app.utils.logger import get_logger
from pathlib import Path

log = get_logger(__name__)

# Maximum number of results returned by a single retrieval query
MAX_RETRIEVAL_RESULTS = 10


class RetrievalResult:
    """
    A single retrieval result from semantic search.

    Attributes:
        chunk_id    — ChromaDB document ID.
        text        — The chunk text content.
        score       — Similarity score (0.0 to 1.0, higher is more relevant).
        source_file — Name of the source legal document.
        source_type — 'act', 'rules', or 'guidance'.
        chunk_index — Position within source document.
    """

    def __init__(
        self,
        chunk_id: str,
        text: str,
        score: float,
        source_file: str,
        source_type: str,
        chunk_index: int,
    ) -> None:
        self.chunk_id = chunk_id
        self.text = text
        self.score = score
        self.source_file = source_file
        self.source_type = source_type
        self.chunk_index = chunk_index

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": self.score,
            "source_file": self.source_file,
            "source_type": self.source_type,
            "chunk_index": self.chunk_index,
        }


class KnowledgeBaseService:
    """
    Service layer for the legal knowledge base.
    All retrieval and ingestion operations go through this class.
    """

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_all_documents(
        self,
        legal_data_path: Optional[str] = None,
        reset: bool = False,
    ) -> dict:
        """
        Process and ingest all documents from the legal_data directory.

        Args:
            legal_data_path: Override directory path (default from settings).
            reset: If True, clears existing collection before ingesting.

        Returns:
            Summary dict with 'documents_processed', 'chunks_ingested', 'status'.
        """
        if reset:
            log.warning("Resetting ChromaDB collection before ingestion.")
            reset_chroma_collection()

        chunks = process_all_documents(legal_data_path)
        if not chunks:
            log.warning("No chunks to ingest.")
            return {"documents_processed": 0, "chunks_ingested": 0, "status": "no_data"}

        ingested = self._ingest_chunks(chunks)
        total_docs = len({c.source_file for c in chunks})

        log.info(f"Ingestion complete — {total_docs} docs, {ingested} chunks.")
        return {
            "documents_processed": total_docs,
            "chunks_ingested": ingested,
            "status": "success",
        }

    def ingest_single_document(self, file_path: str) -> dict:
        """
        Process and ingest a single document file.

        Args:
            file_path: Absolute path to the .txt or .pdf file.

        Returns:
            Summary dict with 'chunks_ingested', 'status'.
        """
        path = Path(file_path)
        chunks = process_document(path)
        if not chunks:
            return {"chunks_ingested": 0, "status": "no_data"}

        ingested = self._ingest_chunks(chunks)
        return {"chunks_ingested": ingested, "status": "success"}

    def _ingest_chunks(self, chunks: list[TextChunk]) -> int:
        """
        Embed and store chunks in ChromaDB in batches.

        Args:
            chunks: List of TextChunk objects to store.

        Returns:
            Number of chunks successfully ingested.
        """
        collection = get_chroma_collection()

        # Skip chunks already in collection (idempotent ingestion by chunk_id)
        existing_ids = set()
        try:
            existing = collection.get(ids=[c.chunk_id for c in chunks])
            existing_ids = set(existing.get("ids", []))
        except Exception:
            pass

        new_chunks = [c for c in chunks if c.chunk_id not in existing_ids]
        if not new_chunks:
            log.info("All chunks already exist in collection — skipping.")
            return 0

        batch_size = 50
        ingested = 0

        for i in range(0, len(new_chunks), batch_size):
            batch = new_chunks[i:i + batch_size]
            texts = [c.text for c in batch]

            try:
                embeddings = generate_embeddings_batch(texts)
                collection.add(
                    ids=[c.chunk_id for c in batch],
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=[c.metadata for c in batch],
                )
                ingested += len(batch)
                log.debug(f"Ingested batch {i // batch_size + 1} — {len(batch)} chunks.")
            except Exception as exc:
                log.error(f"Failed to ingest batch {i // batch_size + 1}: {exc}")

        log.info(f"Ingested {ingested}/{len(new_chunks)} new chunks.")
        return ingested

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        source_type_filter: Optional[str] = None,
    ) -> list[RetrievalResult]:
        """
        Perform semantic search against the knowledge base.

        Args:
            query: Natural language query from the consumer.
            top_k: Number of results to return (max MAX_RETRIEVAL_RESULTS).
            source_type_filter: Optional filter by 'act', 'rules', or 'guidance'.

        Returns:
            List of RetrievalResult ordered by relevance (highest score first).

        Raises:
            ValueError: If query is empty or top_k is invalid.
            RuntimeError: If collection is empty.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = min(top_k, MAX_RETRIEVAL_RESULTS)
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        count = get_collection_count()
        if count == 0:
            raise RuntimeError(
                "Knowledge base is empty. "
                "Run ingestion before performing retrieval."
            )

        # Clamp top_k to actual collection size
        top_k = min(top_k, count)

        query_embedding = generate_embedding(query)
        collection = get_chroma_collection()

        where_filter = None
        if source_type_filter and source_type_filter in ("act", "rules", "guidance"):
            where_filter = {"source_type": {"$eq": source_type_filter}}

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            log.error(f"ChromaDB query failed: {exc}")
            raise RuntimeError(f"Retrieval failed: {exc}")

        retrieval_results: list[RetrievalResult] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, doc_id in enumerate(ids):
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity score: 1 - (distance / 2)
            distance = distances[i] if i < len(distances) else 1.0
            score = round(max(0.0, 1.0 - (distance / 2.0)), 4)

            meta = metadatas[i] if i < len(metadatas) else {}
            retrieval_results.append(
                RetrievalResult(
                    chunk_id=doc_id,
                    text=documents[i] if i < len(documents) else "",
                    score=score,
                    source_file=meta.get("source_file", "unknown"),
                    source_type=meta.get("source_type", "unknown"),
                    chunk_index=meta.get("chunk_index", 0),
                )
            )

        log.info(
            f"Retrieved {len(retrieval_results)} results for query "
            f"'{query[:50]}...' (top_k={top_k})"
        )
        return retrieval_results

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return current knowledge base status."""
        try:
            count = get_collection_count()
            return {
                "status": "ready" if count > 0 else "empty",
                "total_chunks": count,
                "collection_name": __import__("app.config.settings", fromlist=["settings"]).settings.chroma_collection_name,
            }
        except Exception as exc:
            log.error(f"Failed to get KB status: {exc}")
            return {"status": "error", "detail": str(exc)}
