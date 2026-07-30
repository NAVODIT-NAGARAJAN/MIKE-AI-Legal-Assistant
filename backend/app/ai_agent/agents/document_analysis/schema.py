"""
Schema definitions for the Document Analysis Agent.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing import Dict


class DocumentAnalysisResult(BaseModel):
    """
    Structured Pydantic model for Document Analysis results.
    """
    document_type: str = Field(
        description="Detected type of the document (e.g., Invoice, Receipt, Warranty Card, Order Confirmation, Product Images, PDF)"
    )
    summary: str = Field(
        description="A concise summary of the document contents."
    )
    extracted_information: Dict[str, str] = Field(
        description="Structured key-value pairs extracted from the document."
    )
    confidence_score: float = Field(
        description="Confidence score of the extraction between 0.0 and 1.0."
    )
    missing_fields: List[str] = Field(
        default_factory=list,
        description="Any standard fields for this document type that are missing."
    )
