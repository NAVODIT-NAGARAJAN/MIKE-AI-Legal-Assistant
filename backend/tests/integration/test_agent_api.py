"""
Integration Tests — AI Agent API Endpoints
===========================================
"""

import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

async def _register_and_login(client: AsyncClient, email: str, password: str = "SecurePass1") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Agent User", "email": email, "password": password},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return resp.json()["data"]["access_token"]

def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

class TestAgentAPI:
    @pytest.mark.asyncio
    @patch("app.ai_agent.service.Orchestrator.execute")
    async def test_start_conversation(self, mock_execute, app_client: AsyncClient):
        # Mock executor
        from app.ai_agent.core.agent_result import AgentResult
        mock_msg = MagicMock()
        mock_msg.content = "How can I help you today?"
        mock_execute.return_value = AgentResult(success=True, payload={"messages": [mock_msg]})
        
        token = await _register_and_login(app_client, "agent1@example.com")
        
        with patch("app.ai_agent.service.messages_to_dict", return_value=[]):
            resp = await app_client.post(
                "/api/v1/agent/conversations",
                headers=_auth(token),
                json={"initial_message": "I bought a defective phone."}
            )
            
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert "conversation_id" in data
        assert data["reply"] == "How can I help you today?"
        assert data["is_complete"] is False

    @pytest.mark.asyncio
    @patch("app.ai_agent.service.Orchestrator.execute")
    async def test_send_message_and_get_conversation(self, mock_execute, app_client: AsyncClient):
        # Mock executor setup
        from app.ai_agent.core.agent_result import AgentResult
        mock_msg = MagicMock()
        mock_msg.content = "I understand. Do you have the invoice?"
        mock_execute.return_value = AgentResult(success=True, payload={"messages": [mock_msg]})
        
        token = await _register_and_login(app_client, "agent2@example.com")
        
        # Start conv
        with patch("app.ai_agent.service.messages_to_dict", return_value=[]):
            resp1 = await app_client.post(
                "/api/v1/agent/conversations",
                headers=_auth(token),
                json={"initial_message": "I bought a defective phone."}
            )
        conv_id = resp1.json()["data"]["conversation_id"]
        
        # Send follow up
        mock_msg.content = "Great, here is your roadmap. [WORKFLOW_COMPLETE]"
        with patch("app.ai_agent.service.messages_to_dict", return_value=[]), \
             patch("app.ai_agent.service.messages_from_dict", return_value=[]):
            resp2 = await app_client.post(
                f"/api/v1/agent/conversations/{conv_id}/message",
                headers=_auth(token),
                json={"message": "Yes I have it."}
            )
            
        assert resp2.status_code == 200
        data = resp2.json()["data"]
        assert data["is_complete"] is True
        assert data["reply"] == "Great, here is your roadmap."
        
        # Get history
        resp3 = await app_client.get(
            f"/api/v1/agent/conversations/{conv_id}",
            headers=_auth(token)
        )
        assert resp3.status_code == 200
        history = resp3.json()["data"]
        assert len(history["messages"]) == 4 # User1, AI1, User2, AI2
        assert history["messages"][-1]["role"] == "ai"
        assert history["messages"][-1]["content"] == "Great, here is your roadmap."
