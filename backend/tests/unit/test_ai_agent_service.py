"""
Unit Tests — AI Agent Service and Repository
===============================================
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai_agent.repository import ConversationRepository
from app.ai_agent.service import AIAgentService
from app.models.application_models import Conversation

MOCK_USER_ID = uuid.uuid4()
MOCK_CONV_ID = uuid.uuid4()

class TestConversationRepository:
    @pytest.mark.asyncio
    async def test_create_conversation(self):
        mock_db = AsyncMock()
        repo = ConversationRepository(mock_db)
        
        conv = await repo.create(MOCK_USER_ID)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert conv.user_id == MOCK_USER_ID
        assert conv.is_complete is False
        assert conv.messages == []

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars().first.return_value = Conversation(id=MOCK_CONV_ID, user_id=MOCK_USER_ID)
        mock_db.execute.return_value = mock_result
        
        repo = ConversationRepository(mock_db)
        conv = await repo.get_by_id(MOCK_CONV_ID, MOCK_USER_ID)
        
        assert conv is not None
        assert conv.id == MOCK_CONV_ID

    @pytest.mark.asyncio
    async def test_update_state(self):
        mock_db = AsyncMock()
        repo = ConversationRepository(mock_db)
        conv = Conversation(id=MOCK_CONV_ID, messages=[], agent_state={})
        
        updated_conv = await repo.update_state(
            conv, 
            new_messages=[{"role": "user", "content": "hi"}],
            new_agent_state={"dummy": "state"},
            is_complete=True
        )
        
        mock_db.commit.assert_called_once()
        assert len(updated_conv.messages) == 1
        assert updated_conv.agent_state == {"dummy": "state"}
        assert updated_conv.is_complete is True


class TestAIAgentService:
    @pytest.mark.asyncio
    @patch("app.ai_agent.service.get_agent_executor")
    async def test_start_conversation(self, mock_get_executor):
        # Setup mock executor
        mock_executor = AsyncMock()
        mock_ai_message = MagicMock()
        mock_ai_message.content = "Hello from AI"
        mock_executor.ainvoke.return_value = {"messages": [mock_ai_message]}
        mock_get_executor.return_value = mock_executor
        
        # Setup mock repo
        mock_repo = AsyncMock()
        mock_conv = Conversation(id=MOCK_CONV_ID, messages=[])
        mock_repo.create.return_value = mock_conv
        
        service = AIAgentService(mock_repo)
        
        with patch("app.ai_agent.service.messages_to_dict", return_value=[]):
            result = await service.start_conversation(MOCK_USER_ID, "Initial message")
            
        assert result["conversation_id"] == str(MOCK_CONV_ID)
        assert result["reply"] == "Hello from AI"
        assert result["is_complete"] is False

    @pytest.mark.asyncio
    @patch("app.ai_agent.service.get_agent_executor")
    async def test_workflow_complete_marker(self, mock_get_executor):
        mock_executor = AsyncMock()
        mock_ai_message = MagicMock()
        mock_ai_message.content = "Here is your roadmap. [WORKFLOW_COMPLETE]"
        mock_executor.ainvoke.return_value = {"messages": [mock_ai_message]}
        mock_get_executor.return_value = mock_executor
        
        mock_repo = AsyncMock()
        mock_conv = Conversation(id=MOCK_CONV_ID, messages=[], agent_state={})
        mock_repo.get_by_id.return_value = mock_conv
        
        service = AIAgentService(mock_repo)
        
        with patch("app.ai_agent.service.messages_to_dict", return_value=[]), \
             patch("app.ai_agent.service.messages_from_dict", return_value=[]):
            result = await service.send_message(MOCK_CONV_ID, MOCK_USER_ID, "Follow up")
            
        assert result["is_complete"] is True
        assert "[WORKFLOW_COMPLETE]" not in result["reply"]
        assert result["reply"] == "Here is your roadmap."

    @pytest.mark.asyncio
    async def test_send_message_completed_conversation_raises(self):
        mock_repo = AsyncMock()
        mock_conv = Conversation(id=MOCK_CONV_ID, is_complete=True)
        mock_repo.get_by_id.return_value = mock_conv
        
        # we can pass None for get_agent_executor because it shouldn't be called
        with patch("app.ai_agent.service.get_agent_executor"):
            service = AIAgentService(mock_repo)
            with pytest.raises(ValueError, match="Conversation is already complete"):
                await service.send_message(MOCK_CONV_ID, MOCK_USER_ID, "hello")
