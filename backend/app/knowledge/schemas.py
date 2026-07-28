"""
LegalEase AI - Knowledge Base Schemas
"""
from typing import Optional
from pydantic import BaseModel, Field


class RetrievalResultSchema(BaseModel):
    chunk_id: str
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    source_file: str
    source_type: str
    chunk_index: int


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Search query.")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of results.")
    source_type: Optional[str] = Field(
        default=None,
        description="Filter by source type: 'act', 'rules', or 'guidance'.",
    )


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[RetrievalResultSchema]
    total_results: int


class KnowledgeStatusResponse(BaseModel):
    status: str
    total_chunks: int
    collection_name: str
