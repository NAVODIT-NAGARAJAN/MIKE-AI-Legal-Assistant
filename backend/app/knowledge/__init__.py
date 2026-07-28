"""LegalEase AI - Knowledge Base Package."""
from app.knowledge.service import KnowledgeBaseService, RetrievalResult
from app.knowledge.text_processor import TextChunk, process_all_documents

__all__ = ["KnowledgeBaseService", "RetrievalResult", "TextChunk", "process_all_documents"]
