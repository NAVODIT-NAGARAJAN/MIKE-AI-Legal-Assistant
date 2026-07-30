"""
Schema definitions for the Document Intelligence Agent.

These Pydantic models represent the fully structured output of the
document intelligence pipeline, covering extraction, entity recognition,
clause detection, risk detection, and document summarization.
"""

from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Enumerations
# =============================================================================


class DocumentType(StrEnum):
    """
    Supported document types the agent can detect and process.
    """

    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"
    WARRANTY_CARD = "WARRANTY_CARD"
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION"
    PRODUCT_IMAGE = "PRODUCT_IMAGE"
    CONTRACT = "CONTRACT"
    LEGAL_NOTICE = "LEGAL_NOTICE"
    COMPLAINT = "COMPLAINT"
    AFFIDAVIT = "AFFIDAVIT"
    AGREEMENT = "AGREEMENT"
    OTHER = "OTHER"


class EntityType(StrEnum):
    """
    Named entity categories that can be extracted from a document.
    """

    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    COURT = "COURT"
    CASE_NUMBER = "CASE_NUMBER"
    DATE = "DATE"
    LEGAL_SECTION = "LEGAL_SECTION"
    ACT = "ACT"
    ADDRESS = "ADDRESS"
    MONEY = "MONEY"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    PRODUCT = "PRODUCT"
    ORDER_NUMBER = "ORDER_NUMBER"


class ClauseType(StrEnum):
    """
    Legal clause categories the agent can detect.
    """

    ARBITRATION = "ARBITRATION"
    CONFIDENTIALITY = "CONFIDENTIALITY"
    TERMINATION = "TERMINATION"
    PAYMENT = "PAYMENT"
    JURISDICTION = "JURISDICTION"
    LIABILITY = "LIABILITY"
    INDEMNITY = "INDEMNITY"
    FORCE_MAJEURE = "FORCE_MAJEURE"
    PENALTY = "PENALTY"
    REFUND = "REFUND"
    WARRANTY = "WARRANTY"
    LIMITATION = "LIMITATION"
    OTHER = "OTHER"


class RiskType(StrEnum):
    """
    Legal risk categories the agent can identify in a document.
    """

    MISSING_SIGNATURE = "MISSING_SIGNATURE"
    MISSING_PARTY = "MISSING_PARTY"
    EXPIRED_AGREEMENT = "EXPIRED_AGREEMENT"
    AMBIGUOUS_CLAUSE = "AMBIGUOUS_CLAUSE"
    HIGH_LIABILITY = "HIGH_LIABILITY"
    MISSING_DATE = "MISSING_DATE"
    UNENFORCEABLE_TERM = "UNENFORCEABLE_TERM"
    JURISDICTION_CONFLICT = "JURISDICTION_CONFLICT"
    OTHER = "OTHER"


class RiskSeverity(StrEnum):
    """
    Severity levels assigned to a detected legal risk.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# =============================================================================
# Sub-models: Document Metadata
# =============================================================================


class DocumentMetadata(BaseModel):
    """
    Low-level metadata about the parsed source document.
    """

    file_name: Optional[str] = Field(
        default=None,
        description="Original file name as provided by the caller.",
    )
    file_type: Optional[str] = Field(
        default=None,
        description="Detected MIME type or extension (e.g., 'application/pdf', 'image/jpeg').",
    )
    page_count: Optional[int] = Field(
        default=None,
        description="Total number of pages parsed. None for single-page images.",
    )
    character_count: Optional[int] = Field(
        default=None,
        description="Total character count of the cleaned extracted text.",
    )
    ocr_applied: bool = Field(
        default=False,
        description="True if OCR was applied to extract text from an image or scanned PDF.",
    )
    language: Optional[str] = Field(
        default=None,
        description="Detected primary language of the document (e.g., 'en', 'hi').",
    )


# =============================================================================
# Sub-models: Extracted Legal Entities
# =============================================================================


class ExtractedEntity(BaseModel):
    """
    A single extracted named entity found in the document.
    """

    entity_type: EntityType = Field(
        description="Entity category.",
    )
    value: str = Field(
        description="Raw extracted text of the entity.",
    )
    context: Optional[str] = Field(
        default=None,
        description="Surrounding sentence or clause in which the entity appears.",
    )


class EntityExtractionResult(BaseModel):
    """
    Aggregated entity extraction output.
    """

    persons: List[str] = Field(
        default_factory=list,
        description="Names of individuals mentioned in the document.",
    )
    organizations: List[str] = Field(
        default_factory=list,
        description="Names of companies, agencies, or bodies mentioned.",
    )
    courts: List[str] = Field(
        default_factory=list,
        description="Names of courts or tribunals referenced.",
    )
    case_numbers: List[str] = Field(
        default_factory=list,
        description="Case or complaint reference numbers.",
    )
    dates: List[str] = Field(
        default_factory=list,
        description="All dates mentioned in the document.",
    )
    legal_sections: List[str] = Field(
        default_factory=list,
        description="Legal section or provision references (e.g., 'Section 35 of CPA 2019').",
    )
    acts: List[str] = Field(
        default_factory=list,
        description="Legislation or statutory acts referenced.",
    )
    addresses: List[str] = Field(
        default_factory=list,
        description="Physical or postal addresses found.",
    )
    monetary_amounts: List[str] = Field(
        default_factory=list,
        description="Monetary values, prices, or compensation figures mentioned.",
    )
    raw_entities: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Flat list of every extracted entity with its context.",
    )


# =============================================================================
# Sub-models: Clause Detection
# =============================================================================


class DetectedClause(BaseModel):
    """
    A single important legal clause detected in the document.
    """

    clause_type: ClauseType = Field(
        description="Clause category.",
    )
    excerpt: str = Field(
        description="Verbatim or near-verbatim excerpt of the clause from the document.",
    )
    summary: str = Field(
        description="One-sentence plain-language summary of what the clause means.",
    )


class ClauseDetectionResult(BaseModel):
    """
    All important clauses detected across the document.
    """

    detected_clauses: List[DetectedClause] = Field(
        default_factory=list,
        description="List of all detected legal clauses.",
    )
    clause_count: int = Field(
        default=0,
        description="Total number of clauses detected.",
    )


# =============================================================================
# Sub-models: Risk Detection
# =============================================================================


class DetectedRisk(BaseModel):
    """
    A single legal risk identified in the document.
    """

    risk_type: RiskType = Field(
        description="Risk category.",
    )
    description: str = Field(
        description="Concise description of the identified risk.",
    )
    severity: RiskSeverity = Field(
        description="Risk severity level.",
    )
    recommendation: Optional[str] = Field(
        default=None,
        description="Suggested action to mitigate or address the risk.",
    )


class RiskDetectionResult(BaseModel):
    """
    Aggregated risk detection output.
    """

    risks: List[DetectedRisk] = Field(
        default_factory=list,
        description="All identified risks in the document.",
    )
    overall_risk_level: RiskSeverity = Field(
        default=RiskSeverity.LOW,
        description="Highest risk severity level across all detected risks.",
    )
    risk_count: int = Field(
        default=0,
        description="Total number of risks detected.",
    )


# =============================================================================
# Top-level Output Model
# =============================================================================


class DocumentIntelligenceResult(BaseModel):
    """
    Complete structured output of the Document Intelligence Agent.

    This model is the single source of truth for all document analysis
    produced by the pipeline, covering raw extraction through to risk
    assessment.
    """

    # -------------------------------------------------------------------------
    # Document Identity
    # -------------------------------------------------------------------------
    document_type: DocumentType = Field(
        description="Detected document type.",
    )
    metadata: DocumentMetadata = Field(
        description="Source document metadata (file type, page count, OCR flag, etc.).",
    )

    # -------------------------------------------------------------------------
    # Extracted Text
    # -------------------------------------------------------------------------
    raw_text: Optional[str] = Field(
        default=None,
        description="Full cleaned text extracted from the document. Omitted for large payloads.",
    )

    # -------------------------------------------------------------------------
    # Structured Extraction
    # -------------------------------------------------------------------------
    extracted_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Document-type-specific structured key-value pairs. "
            "For an Invoice: invoice_number, seller, buyer, total_amount, tax, due_date. "
            "For a Warranty Card: product_name, model_number, serial_number, purchase_date, warranty_period, covered_defects. "
            "For an Order Confirmation: order_id, platform, items, delivery_date, payment_method."
        ),
    )

    # -------------------------------------------------------------------------
    # Intelligence Results
    # -------------------------------------------------------------------------
    entities: EntityExtractionResult = Field(
        default_factory=EntityExtractionResult,
        description="All named entities extracted from the document.",
    )
    clauses: ClauseDetectionResult = Field(
        default_factory=ClauseDetectionResult,
        description="Important legal clauses detected in the document.",
    )
    risks: RiskDetectionResult = Field(
        default_factory=RiskDetectionResult,
        description="Legal risks identified in the document.",
    )

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    summary: str = Field(
        description="Concise plain-language summary of the document contents.",
    )
    missing_fields: List[str] = Field(
        default_factory=list,
        description="Standard fields expected for the detected document type that could not be found.",
    )

    # -------------------------------------------------------------------------
    # Confidence
    # -------------------------------------------------------------------------
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in the extraction accuracy, between 0.0 and 1.0.",
    )
