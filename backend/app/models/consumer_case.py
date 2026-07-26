"""
LegalEase AI - Consumer Case SQLAlchemy Model
===============================================
Defines the 'consumer_cases' table in PostgreSQL.
Maps to the ConsumerCase entity from database.md.
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class IssueCategory(str, enum.Enum):
    """Supported consumer issue categories (from project-requirements.md)."""
    DEFECTIVE_PRODUCT = "DEFECTIVE_PRODUCT"
    REFUND_ISSUE = "REFUND_ISSUE"
    WARRANTY_CLAIM = "WARRANTY_CLAIM"
    BILLING_DISPUTE = "BILLING_DISPUTE"
    DELIVERY_PROBLEM = "DELIVERY_PROBLEM"
    SERVICE_DEFICIENCY = "SERVICE_DEFICIENCY"
    MISLEADING_ADVERTISEMENT = "MISLEADING_ADVERTISEMENT"
    ECOMMERCE_COMPLAINT = "ECOMMERCE_COMPLAINT"


class CaseStatus(str, enum.Enum):
    """Lifecycle status of a consumer case."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    REPORT_GENERATED = "REPORT_GENERATED"
    CLOSED = "CLOSED"


class ConsumerCase(Base):
    """
    Represents a consumer issue filed by a user.

    Table: consumer_cases
    Relationships:
        - user (many-to-one)
        - conversations (one-to-many)
        - roadmap (one-to-one)
        - evidence_checklist (one-to-one)
        - report (one-to-one)
    """

    __tablename__ = "consumer_cases"

    # ---- Primary Key ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ---- Foreign Key ----
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ---- Case Details ----
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Brief title describing the consumer issue",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of the consumer issue",
    )

    category: Mapped[IssueCategory] = mapped_column(
        Enum(IssueCategory),
        nullable=False,
        index=True,
    )

    product_or_service: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of the product or service involved",
    )

    seller_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Name of the seller or service provider",
    )

    purchase_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Date of purchase or service commencement",
    )

    # ---- Status ----
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus),
        nullable=False,
        default=CaseStatus.OPEN,
        index=True,
    )

    # ---- Timestamps ----
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ---- Relationships ----
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="consumer_cases",
    )

    conversations: Mapped[list["Conversation"]] = relationship(  # noqa: F821
        "Conversation",
        back_populates="consumer_case",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    roadmap: Mapped["Roadmap | None"] = relationship(  # noqa: F821
        "Roadmap",
        back_populates="consumer_case",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    evidence_checklist: Mapped["EvidenceChecklist | None"] = relationship(  # noqa: F821
        "EvidenceChecklist",
        back_populates="consumer_case",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    report: Mapped["Report | None"] = relationship(  # noqa: F821
        "Report",
        back_populates="consumer_case",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ConsumerCase id={self.id} category={self.category} status={self.status}>"
