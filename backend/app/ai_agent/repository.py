"""
LegalEase AI - AI Agent Repository
=====================================
Database operations for AI Conversations.
"""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.application_models import Conversation
from app.utils.logger import get_logger

log = get_logger(__name__)


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        case_id: Optional[uuid.UUID] = None,
    ) -> Conversation:
        """Create a new conversation session."""
        conv = Conversation(
            user_id=user_id,
            case_id=case_id,
            messages=[],
            agent_state={},
            is_complete=False,
        )

        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)

        log.info(f"Created conversation {conv.id} for user {user_id}")
        return conv

    async def get_by_id(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Conversation]:
        """Get a conversation ensuring it belongs to the specified user."""
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Conversation]:
        """Return all conversations belonging to the user."""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_state(
        self,
        conv: Conversation,
        new_messages: list,
        new_agent_state: dict,
        is_complete: bool,
    ) -> Conversation:
        """Update conversation messages and agent state."""
        conv.messages = list(new_messages)
        conv.agent_state = dict(new_agent_state)
        conv.is_complete = is_complete

        await self.db.commit()
        await self.db.refresh(conv)

        return conv