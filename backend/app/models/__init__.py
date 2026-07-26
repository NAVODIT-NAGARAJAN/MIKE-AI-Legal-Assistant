"""
LegalEase AI - Models Package
==============================
Imports all ORM models so they are registered with SQLAlchemy Base.
This file must be imported before any database migration or table creation.
"""

from app.models.user import User
from app.models.consumer_case import ConsumerCase, IssueCategory, CaseStatus
from app.models.application_models import (
    Conversation,
    Roadmap,
    EvidenceChecklist,
    Report,
    ActivityLog,
)

__all__ = [
    "User",
    "ConsumerCase",
    "IssueCategory",
    "CaseStatus",
    "Conversation",
    "Roadmap",
    "EvidenceChecklist",
    "Report",
    "ActivityLog",
]
