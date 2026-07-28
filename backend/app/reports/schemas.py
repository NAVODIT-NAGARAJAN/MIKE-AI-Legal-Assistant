"""
LegalEase AI - Report Generation Schemas
========================================
Schemas for Report, Roadmap, and EvidenceChecklist.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RoadmapStepSchema(BaseModel):
    step_number: int = Field(..., description="Step order number")
    title: str = Field(..., description="Short title of the step")
    description: str = Field(..., description="Detailed explanation of the step")
    is_done: bool = Field(False, description="Whether the step is completed")


class ConsumerRightSchema(BaseModel):
    right: str = Field(..., description="The name of the consumer right")
    description: str = Field(..., description="Explanation of how the right applies")
    legal_citation: str = Field(..., description="Citation of the relevant law/act")


class EvidenceItemSchema(BaseModel):
    item: str = Field(..., description="Name of the document or evidence")
    is_required: bool = Field(..., description="True if mandatory, False if optional")
    description: str = Field(..., description="Explanation of why it is needed")


class ReportGenerationDataSchema(BaseModel):
    """Schema used by the AI to structure the generated report data."""
    case_summary: str = Field(..., description="Summary of the consumer's issue")
    consumer_rights: List[ConsumerRightSchema] = Field(..., description="Applicable consumer rights")
    roadmap_steps: List[RoadmapStepSchema] = Field(..., description="Step-by-step resolution roadmap")
    evidence_items: List[EvidenceItemSchema] = Field(..., description="Required and optional evidence")
    next_steps: str = Field(..., description="Immediate next actions to take")
    recommended_authority: str = Field(..., description="Suggested grievance authority to approach")


class ReportResponseSchema(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    case_summary: str
    consumer_rights: List[ConsumerRightSchema]
    roadmap_steps: List[RoadmapStepSchema]
    evidence_items: List[EvidenceItemSchema]
    next_steps: str
    recommended_authority: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateReportRequestSchema(BaseModel):
    case_id: uuid.UUID
