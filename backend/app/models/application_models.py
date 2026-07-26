"""
LegalEase AI - Conversation, Roadmap, Evidence & Report Models
===============================================================
Defines the remaining application tables in PostgreSQL.
All use JSONB columns for flexible structured data storage.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Conversation(Base):
    """
    Stores an AI agent conversation session and its full history.

    Table: conversations
    JSONB messages column stores the ordered list of user + AI messages.
    JSONB agent_state stores the current LangGraph state snapshot.
    """

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("consumer_cases.id", ondelete="SET NULL"), nullable=True, index=True)

    # Full conversation history: [{"role": "user"|"ai", "content": "...", "timestamp": "..."}]
    messages: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # LangGraph agent state snapshot for resuming conversations
    agent_state: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")  # noqa: F821
    consumer_case: Mapped["ConsumerCase | None"] = relationship("ConsumerCase", back_populates="conversations")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} complete={self.is_complete}>"


class Roadmap(Base):
    """
    Stores the personalized resolution roadmap for a consumer case.

    Table: roadmaps
    JSONB steps column: [{"step_number": 1, "title": "...", "description": "...", "is_done": false}]
    """

    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("consumer_cases.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ordered list of resolution steps
    steps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    consumer_case: Mapped["ConsumerCase"] = relationship("ConsumerCase", back_populates="roadmap")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Roadmap id={self.id} steps={len(self.steps)}>"


class EvidenceChecklist(Base):
    """
    Stores the personalized evidence checklist for a consumer case.

    Table: evidence_checklists
    JSONB columns: [{"item": "Invoice", "is_required": true, "description": "..."}]
    """

    __tablename__ = "evidence_checklists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("consumer_cases.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    required_documents: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    optional_documents: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    consumer_case: Mapped["ConsumerCase"] = relationship("ConsumerCase", back_populates="evidence_checklist")  # noqa: F821

    def __repr__(self) -> str:
        return f"<EvidenceChecklist id={self.id}>"


class Report(Base):
    """
    Stores the complete consumer guidance report for a consumer case.

    Table: reports
    Contains all report sections as structured JSON and plain text fields.
    """

    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("consumer_cases.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Case summary section
    case_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Applicable consumer rights with legal citations
    consumer_rights: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Personalized roadmap steps (denormalized copy for report)
    roadmap_steps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Evidence checklist (denormalized copy for report)
    evidence_items: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Free-text next steps recommendation
    next_steps: Mapped[str] = mapped_column(Text, nullable=False)

    # Suggested grievance authority
    recommended_authority: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    consumer_case: Mapped["ConsumerCase"] = relationship("ConsumerCase", back_populates="report")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Report id={self.id}>"


class ActivityLog(Base):
    """
    Audit trail for security-relevant events.

    Table: activity_logs
    Sensitive user data (passwords, tokens) is NEVER stored here.
    """

    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type: Mapped[str] = mapped_column(Text, nullable=False, index=True,
        comment="e.g. USER_LOGIN, CASE_CREATED, AI_CONVERSATION_STARTED, ERROR")

    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict,
        comment="Event-specific metadata. Never log passwords or tokens.")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<ActivityLog event={self.event_type} user={self.user_id}>"
