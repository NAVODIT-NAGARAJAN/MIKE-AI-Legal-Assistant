"""
LegalEase AI - AI Agent Router
=================================
API endpoints for starting and continuing AI conversations.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_agent.repository import ConversationRepository
from app.cases.repository import CaseRepository
from app.ai_agent.schemas import (
    AgentReplySchema,
    ConversationDetailSchema,
    ConversationListItemSchema,
    SendMessageRequest,
    StartConversationRequest,
)
from app.ai_agent.service import AIAgentService
from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


def get_agent_service(
    db: AsyncSession = Depends(get_db),
) -> AIAgentService:

    conversation_repo = ConversationRepository(db)
    case_repo = CaseRepository(db)

    return AIAgentService(
        conversation_repository=conversation_repo,
        case_repository=case_repo,
    )


@router.post(
    "/conversations",
    response_model=SuccessResponse[AgentReplySchema],
    status_code=status.HTTP_201_CREATED,
    summary="Start a new AI conversation",
)
async def start_conversation(
    payload: StartConversationRequest,
    current_user: User = Depends(get_current_active_user),
    service: AIAgentService = Depends(get_agent_service),
) -> SuccessResponse[AgentReplySchema]:
    """Start a new consultation session with the LegalEase AI agent."""
    try:
        result = await service.start_conversation(
            user_id=current_user.id,
            initial_message=payload.initial_message,
            case_id=payload.case_id,
        )

        log.info(f"START_CONVERSATION reply type: {type(result['reply'])}")
        log.info(f"START_CONVERSATION reply content: {repr(result['reply'])}")

        if not isinstance(result["reply"], str):
            result["reply"] = str(result["reply"])

        return SuccessResponse(
            message="Conversation started successfully.",
            data=AgentReplySchema(**result),
        )

    except Exception as exc:
        log.error(f"Failed to start conversation: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# ===========================
# NEW ENDPOINT
# ===========================
@router.get(
    "/conversations",
    response_model=SuccessResponse[list[ConversationListItemSchema]],
    status_code=status.HTTP_200_OK,
    summary="List all user conversations",
)
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    service: AIAgentService = Depends(get_agent_service),
) -> SuccessResponse[list[ConversationListItemSchema]]:
    """
    Return all conversations belonging to the logged-in user.
    """

    conversations = await service.list_conversations(current_user.id)

    response = []

    for conv in conversations:
        title = "New Conversation"

        if conv.messages:
            for msg in conv.messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "").strip()

                    if content:
                        title = (
                            content[:50] + "..."
                            if len(content) > 50
                            else content
                        )

                    break

        response.append(
            ConversationListItemSchema(
                id=conv.id,
                case_id=conv.case_id,
                is_complete=conv.is_complete,
                created_at=conv.created_at,
                title=title,
            )
        )

    return SuccessResponse(
        message="Conversations retrieved successfully.",
        data=response,
    )


@router.post(
    "/conversations/{conversation_id}/message",
    response_model=SuccessResponse[AgentReplySchema],
    status_code=status.HTTP_200_OK,
    summary="Send a message to an existing conversation",
)
async def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_active_user),
    service: AIAgentService = Depends(get_agent_service),
) -> SuccessResponse[AgentReplySchema]:
    """Send a follow-up message to the AI agent."""
    try:
        result = await service.send_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            message=payload.message,
        )

        log.info(f"SEND_MESSAGE reply type: {type(result['reply'])}")
        log.info(f"SEND_MESSAGE reply content: {repr(result['reply'])}")

        if not isinstance(result["reply"], str):
            result["reply"] = str(result["reply"])

        return SuccessResponse(
            message="Message processed successfully.",
            data=AgentReplySchema(**result),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        log.error(f"Failed to process message: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse[ConversationDetailSchema],
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: AIAgentService = Depends(get_agent_service),
) -> SuccessResponse[ConversationDetailSchema]:
    """Retrieve full history of a specific conversation."""
    try:
        conv = await service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )

        return SuccessResponse(
            message="Conversation retrieved successfully.",
            data=ConversationDetailSchema.model_validate(conv),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
@router.delete(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete conversation",
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: AIAgentService = Depends(get_agent_service),
) -> SuccessResponse[None]:

    await service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return SuccessResponse(
        message="Conversation deleted successfully.",
        data=None,
    )