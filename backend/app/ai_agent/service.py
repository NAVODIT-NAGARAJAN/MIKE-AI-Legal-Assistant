"""
LegalEase AI - AI Agent Service
=================================
Service layer handling conversation state, history management,
and invoking the LangGraph agent asynchronously.
"""


import uuid
from datetime import datetime, timezone
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_core.messages import messages_from_dict, messages_to_dict

from app.ai_agent.core.agent_context import AgentContext
from app.ai_agent.orchestrator.orchestrator import Orchestrator
from app.ai_agent.core.registry import AgentRegistry
from app.ai_agent.orchestrator.router import OrchestratorRouter
from app.ai_agent.repository import ConversationRepository
from app.cases.repository import CaseRepository
from app.models.application_models import Conversation
from app.utils.logger import get_logger

log = get_logger(__name__)


class AIAgentService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        case_repository: CaseRepository,
    ):
        self.repo = conversation_repository
        self.case_repo = case_repository
        self.orchestrator = Orchestrator(
            registry=AgentRegistry(),
            router=OrchestratorRouter(),
        )

    async def start_conversation(
        self,
        user_id: uuid.UUID,
        initial_message: str,
        case_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """Create a new conversation and process the first message."""
        conv = await self.repo.create(user_id=user_id, case_id=case_id)
        return await self._process_turn(conv, initial_message)

    
    async def send_message(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        message: str,
    ) -> dict:
        """Process a follow-up message in an existing conversation."""
        conv = await self.repo.get_by_id(conversation_id, user_id)

        if not conv:
            raise ValueError("Conversation not found or access denied.")

        # ---------------------------------------------------------
        # Conversation remains available unless explicitly closed
        # by the user through the frontend.
        # ---------------------------------------------------------
        if conv.is_complete:
            raise ValueError(
                "This conversation has been closed by the user."
            )

        return await self._process_turn(conv, message)

    
    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Conversation:
        """Retrieve full conversation details."""
        conv = await self.repo.get_by_id(conversation_id, user_id)

        if not conv:
            raise ValueError("Conversation not found or access denied.")

        return conv

    async def list_conversations(
        self,
        user_id: uuid.UUID,
    ) -> list[Conversation]:
        """
        Retrieve all conversations for the current user.
        """
        return await self.repo.list_by_user(user_id)

    async def _process_turn(
        self,
        conv: Conversation,
        user_input: str,
    ) -> dict:
        """Internal logic: load state, run agent, save state."""
        log.info(f"Processing turn for conversation {conv.id}")

        ui_messages = list(conv.messages)
        ui_messages.append(
            {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        lc_messages = []

        if conv.agent_state and "messages" in conv.agent_state:
            lc_messages = messages_from_dict(conv.agent_state["messages"])

        enhanced_input = user_input

        # ---------------------------------------------------------
        # Load selected case and provide it as AI context
        # ---------------------------------------------------------

        if conv.case_id:

            case = await self.case_repo.get_by_id_and_user(
                conv.case_id,
                conv.user_id,
            )

            if case:

                enhanced_input = f"""
The user has already registered the following consumer complaint.

Case Title:
{case.title}

Issue Description:
{case.description}

Issue Category:
{case.category.value}

Product / Service:
{case.product_or_service}

Seller:
{case.seller_name or "Not Provided"}

Purchase Date:
{case.purchase_date or "Not Provided"}

--------------------------------------------------

User Question:

{user_input}

Answer using the above case details.
Do not ask the user to explain the complaint again unless additional information is required.
"""

        lc_messages.append(
            HumanMessage(content=enhanced_input)
        )

        log.info("========== AI DEBUG ==========")
        log.info(f"Conversation ID: {conv.id}")
        log.info(f"Case ID: {conv.case_id}")
        log.info("Sending prompt to Gemini...")
        log.info(enhanced_input)

        try:
            context = AgentContext(
                user_input=user_input,
                conversation_id=str(conv.id),
                user_id=str(conv.user_id),
                case_id=str(conv.case_id) if conv.case_id else None,
                conversation_history=ui_messages,
                langgraph_messages=lc_messages,
                metadata={
                    "service": "AIAgentService"
                },
                shared_memory={},
            )

            agent_result = await self.orchestrator.execute(context)

            if not agent_result.success or agent_result.payload is None:
                raise RuntimeError(
                    "AI Agent failed to process message."
                ) from (
                    agent_result.error
                    if agent_result.error
                    else None
                )

            result = agent_result.payload

            log.info("Gemini responded successfully.")

        except Exception as exc:
            log.exception("Agent execution failed")
            raise RuntimeError(
                "AI Agent failed to process message."
            ) from exc

        new_lc_messages = result["messages"]
        ai_msg = new_lc_messages[-1]
        reply_content = ai_msg.content

        def _extract_text(content) -> str:
            """Extract plain text from Gemini response."""
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                return "".join(_extract_text(c) for c in content)
            elif isinstance(content, dict):
                if "text" in content:
                    return str(content["text"])
                if "content" in content:
                    return _extract_text(content["content"])
                if "parts" in content:
                    return _extract_text(content["parts"])
                return str(content)
            elif hasattr(content, "text"):
                return str(content.text)
            elif hasattr(content, "content"):
                return str(content.content)
            elif hasattr(content, "parts"):
                return _extract_text(content.parts)
            else:
                return str(content)

        reply_content = _extract_text(reply_content)

        # ---------------------------------------------------------
        # Conversation Lifecycle
        # ---------------------------------------------------------
        # MIKE never closes conversations automatically.
        # Users can continue asking follow-up questions,
        # modify generated documents, request translations,
        # generate new complaint letters, or continue the
        # consultation without interruption.
        #
        # Conversations will only be closed through a future
        # frontend "Close Conversation" feature.
        # ---------------------------------------------------------


        ui_messages.append(
            {
                "role": "ai",
                "content": reply_content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        new_agent_state = {
            "messages": messages_to_dict(new_lc_messages)
        }

        await self.repo.update_state(
            conv=conv,
            new_messages=ui_messages,
            new_agent_state=new_agent_state,
            is_complete=conv.is_complete,
        )

        return {
            "conversation_id": str(conv.id),
            "reply": reply_content,
            "is_complete": conv.is_complete,
        }