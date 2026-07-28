"""
Integration Tests — Reports API Endpoints
===========================================
"""

import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

async def _register_and_login(client: AsyncClient, email: str, password: str = "SecurePass1") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Report User", "email": email, "password": password},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return resp.json()["data"]["access_token"]

def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

class TestReportAPI:
    @pytest.mark.asyncio
    @patch("app.reports.service.AIFormatter")
    async def test_generate_and_get_report(self, mock_formatter, app_client: AsyncClient):
        # 1. Setup mock
        from unittest.mock import AsyncMock
        mock_formatter.format_conversation = AsyncMock(return_value={
            "case_summary": "Defective TV",
            "consumer_rights": [{"right": "Replacement", "description": "Within warranty", "legal_citation": "CPA 2019"}],
            "roadmap_steps": [{"step_number": 1, "title": "Contact Seller", "description": "Email support", "is_done": False}],
            "evidence_items": [{"item": "Invoice", "is_required": True, "description": "Proof of purchase"}],
            "next_steps": "Wait 48h",
            "recommended_authority": "National Consumer Helpline"
        })

        token = await _register_and_login(app_client, "report1@example.com")
        
        # 2. Create a Case
        resp_case = await app_client.post(
            "/api/v1/cases",
            headers=_auth(token),
            json={
                "title": "Broken TV",
                "description": "TV arrived completely broken with a smashed screen.",
                "category": "DEFECTIVE_PRODUCT",
                "product_or_service": "Samsung TV",
                "seller_name": "TechStore"
            }
        )
        assert resp_case.status_code == 201
        case_id = resp_case.json()["data"]["id"]
        
        # 3. Create a Conversation linked to the case and mark it complete manually via internal service mocking,
        # or we just create a conversation via API and patch the is_complete flag in DB.
        # It's easier to use the API, then manually run a query to update it for test.
        # But since we are testing endpoints, let's create a conversation.
        with patch("app.ai_agent.service.get_agent_executor") as mock_get_executor:
            mock_executor = AsyncMock()
            mock_msg = MagicMock()
            mock_msg.content = "Roadmap. [WORKFLOW_COMPLETE]"
            mock_executor.ainvoke.return_value = {"messages": [mock_msg]}
            mock_get_executor.return_value = mock_executor
            
            with patch("app.ai_agent.service.messages_to_dict", return_value=[]):
                resp_conv = await app_client.post(
                    "/api/v1/agent/conversations",
                    headers=_auth(token),
                    json={"initial_message": "My TV arrived completely broken.", "case_id": case_id}
                )
        conv_id = resp_conv.json()["data"]["conversation_id"]
        
        # 4. Generate Report
        resp_gen = await app_client.post(
            f"/api/v1/report/generate/{conv_id}",
            headers=_auth(token)
        )
        assert resp_gen.status_code == 201
        data = resp_gen.json()["data"]
        assert data["case_id"] == case_id
        assert data["case_summary"] == "Defective TV"

        # 5. Get Report
        resp_get = await app_client.get(
            f"/api/v1/report/{case_id}",
            headers=_auth(token)
        )
        assert resp_get.status_code == 200
        data_get = resp_get.json()["data"]
        assert data_get["case_summary"] == "Defective TV"
        assert len(data_get["consumer_rights"]) == 1
        
        # 6. Download PDF
        resp_pdf = await app_client.get(
            f"/api/v1/report/{case_id}/download",
            headers=_auth(token)
        )
        assert resp_pdf.status_code == 200
        assert resp_pdf.headers["content-type"] == "application/pdf"
        assert b"%PDF" in resp_pdf.content
