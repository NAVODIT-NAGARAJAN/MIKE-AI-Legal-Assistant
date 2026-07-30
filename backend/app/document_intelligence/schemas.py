"""
Document Intelligence API Schemas
"""

from pydantic import BaseModel


class DocumentAnalysisResponse(BaseModel):
    success: bool
    filename: str
    document_type: str
    confidence_score: float
    overall_risk_level: str
    analysis: dict