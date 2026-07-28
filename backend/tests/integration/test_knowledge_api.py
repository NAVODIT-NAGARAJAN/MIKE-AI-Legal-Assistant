"""
Integration Tests — Knowledge Base API Endpoints
=================================================
Tests for GET /api/v1/knowledge/status and POST /api/v1/knowledge/search.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from app.knowledge.service import RetrievalResult

# Mock data for retrieval
MOCK_RESULTS = [
    RetrievalResult(
        chunk_id="chunk-1",
        text="Consumer has the right to safety.",
        score=0.85,
        source_file="act.txt",
        source_type="act",
        chunk_index=0
    ),
    RetrievalResult(
        chunk_id="chunk-2",
        text="E-commerce rules dictate 48 hour response.",
        score=0.75,
        source_file="rules.txt",
        source_type="rules",
        chunk_index=5
    )
]


async def _register_and_login(client: AsyncClient, email: str, password: str = "SecurePass1") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": email, "password": password},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return resp.json()["data"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestKnowledgeStatus:
    @pytest.mark.asyncio
    @patch("app.knowledge.router.KnowledgeBaseService")
    async def test_get_status_returns_200(self, mock_svc_class, app_client: AsyncClient):
        mock_svc = mock_svc_class.return_value
        mock_svc.get_status.return_value = {
            "status": "ready",
            "total_chunks": 100,
            "collection_name": "test_collection"
        }

        resp = await app_client.get("/api/v1/knowledge/status")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "ready"
        assert data["total_chunks"] == 100


class TestKnowledgeSearch:
    @pytest.mark.asyncio
    @patch("app.knowledge.router.KnowledgeBaseService")
    async def test_search_returns_results(self, mock_svc_class, app_client: AsyncClient):
        mock_svc = mock_svc_class.return_value
        mock_svc.retrieve.return_value = MOCK_RESULTS

        token = await _register_and_login(app_client, "kbsearch@example.com")
        
        payload = {"query": "consumer rights", "top_k": 2}
        resp = await app_client.post(
            "/api/v1/knowledge/search",
            headers=_auth(token),
            json=payload
        )
        
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["query"] == "consumer rights"
        assert data["total_results"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["chunk_id"] == "chunk-1"
        assert data["results"][1]["source_type"] == "rules"

    @pytest.mark.asyncio
    async def test_search_without_token_returns_401_or_403(self, app_client: AsyncClient):
        payload = {"query": "consumer rights"}
        resp = await app_client.post("/api/v1/knowledge/search", json=payload)
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_search_invalid_query_returns_422(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "invalidquery@example.com")
        
        # Query too short
        payload = {"query": "ab"}
        resp = await app_client.post(
            "/api/v1/knowledge/search",
            headers=_auth(token),
            json=payload
        )
        assert resp.status_code == 422
