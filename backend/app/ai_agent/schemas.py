"""
LegalEase AI - AI Agent Schemas
==================================
Pydantic schemas for the AI Agent API.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConversationMessageSchema(BaseModel):
    role: str = Field(..., description="'user' or 'ai'")
    content: str = Field(..., description="The message content")
    timestamp: str = Field(..., description="ISO format timestamp")


class StartConversationRequest(BaseModel):
    initial_message: str = Field(
        ...,
        min_length=1,
        description="The user's initial problem description."
    )
    case_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional associated case ID."
    )


class SendMessageRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="The user's message."
    )


class AgentReplySchema(BaseModel):
    conversation_id: uuid.UUID
    reply: str
    is_complete: bool


class ConversationListItemSchema(BaseModel):
    id: uuid.UUID
    case_id: Optional[uuid.UUID]
    is_complete: bool
    created_at: datetime

    # Title displayed in the Recent Chats sidebar
    title: str

    model_config = {"from_attributes": True}


class ConversationDetailSchema(BaseModel):
    id: uuid.UUID
    case_id: Optional[uuid.UUID]
    is_complete: bool
    messages: List[ConversationMessageSchema]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}