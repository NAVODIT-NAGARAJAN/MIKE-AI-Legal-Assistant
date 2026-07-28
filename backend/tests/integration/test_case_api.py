"""
Integration Tests — Consumer Case API Endpoints
=================================================
Tests for POST/GET/PUT/DELETE /api/v1/cases.
Uses real FastAPI app with SQLite test database via conftest.py.
"""

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


_VALID_CASE = {
    "title": "Defective product received from online seller",
    "description": "I received a completely damaged product that does not work at all and is unusable.",
    "category": "DEFECTIVE_PRODUCT",
    "product_or_service": "Samsung Galaxy S24",
    "seller_name": "Amazon India",
}


async def _create_case(client: AsyncClient, token: str, data: dict = None) -> dict:
    resp = await client.post(
        "/api/v1/cases",
        headers=_auth(token),
        json=data or _VALID_CASE,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


# ---------------------------------------------------------------------------
# POST /api/v1/cases — Create
# ---------------------------------------------------------------------------

class TestCreateCase:

    @pytest.mark.asyncio
    async def test_create_case_returns_201(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "createcase@example.com")
        resp = await app_client.post("/api/v1/cases", headers=_auth(token), json=_VALID_CASE)
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["category"] == "DEFECTIVE_PRODUCT"
        assert body["data"]["status"] == "OPEN"
        assert "id" in body["data"]
        assert "password_hash" not in body["data"]

    @pytest.mark.asyncio
    async def test_create_case_without_token_returns_403_or_401(self, app_client: AsyncClient):
        resp = await app_client.post("/api/v1/cases", json=_VALID_CASE)
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_create_case_invalid_category_returns_422(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "badcat@example.com")
        payload = {**_VALID_CASE, "category": "INVALID_CAT"}
        resp = await app_client.post("/api/v1/cases", headers=_auth(token), json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_case_short_title_returns_422(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "shorttitle@example.com")
        payload = {**_VALID_CASE, "title": "Bad"}
        resp = await app_client.post("/api/v1/cases", headers=_auth(token), json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_case_short_description_returns_422(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "shortdesc@example.com")
        payload = {**_VALID_CASE, "description": "Too short."}
        resp = await app_client.post("/api/v1/cases", headers=_auth(token), json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_all_issue_categories_accepted(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "allcats@example.com")
        categories = [
            "DEFECTIVE_PRODUCT", "REFUND_ISSUE", "WARRANTY_CLAIM",
            "BILLING_DISPUTE", "DELIVERY_PROBLEM", "SERVICE_DEFICIENCY",
            "MISLEADING_ADVERTISEMENT", "ECOMMERCE_COMPLAINT",
        ]
        for cat in categories:
            resp = await app_client.post(
                "/api/v1/cases",
                headers=_auth(token),
                json={**_VALID_CASE, "category": cat},
            )
            assert resp.status_code == 201, f"Failed for category {cat}: {resp.text}"


# ---------------------------------------------------------------------------
# GET /api/v1/cases — List
# ---------------------------------------------------------------------------

class TestListCases:

    @pytest.mark.asyncio
    async def test_list_returns_200_empty_initially(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "emptylist@example.com")
        resp = await app_client.get("/api/v1/cases", headers=_auth(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["items"] == []
        assert body["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_list_shows_created_cases(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "listedcases@example.com")
        await _create_case(app_client, token)
        await _create_case(app_client, token)
        resp = await app_client.get("/api/v1/cases", headers=_auth(token))
        assert resp.json()["data"]["total"] == 2
        assert len(resp.json()["data"]["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_isolation_between_users(self, app_client: AsyncClient):
        """User A's cases must not appear in User B's list."""
        token_a = await _register_and_login(app_client, "usera_cases@example.com")
        token_b = await _register_and_login(app_client, "userb_cases@example.com")
        await _create_case(app_client, token_a)

        resp = await app_client.get("/api/v1/cases", headers=_auth(token_b))
        assert resp.json()["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_list_without_token_returns_401_or_403(self, app_client: AsyncClient):
        resp = await app_client.get("/api/v1/cases")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_list_pagination_limit(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "pagination@example.com")
        for _ in range(5):
            await _create_case(app_client, token)
        resp = await app_client.get("/api/v1/cases?limit=2&skip=0", headers=_auth(token))
        assert len(resp.json()["data"]["items"]) == 2
        assert resp.json()["data"]["total"] == 5


# ---------------------------------------------------------------------------
# GET /api/v1/cases/{case_id} — Single
# ---------------------------------------------------------------------------

class TestGetCase:

    @pytest.mark.asyncio
    async def test_get_own_case_returns_200(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "getsinglecase@example.com")
        case = await _create_case(app_client, token)
        resp = await app_client.get(f"/api/v1/cases/{case['id']}", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == case["id"]

    @pytest.mark.asyncio
    async def test_get_other_users_case_returns_404(self, app_client: AsyncClient):
        token_a = await _register_and_login(app_client, "owner_a@example.com")
        token_b = await _register_and_login(app_client, "other_b@example.com")
        case = await _create_case(app_client, token_a)

        resp = await app_client.get(f"/api/v1/cases/{case['id']}", headers=_auth(token_b))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_case_returns_404(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "nocase@example.com")
        resp = await app_client.get(
            "/api/v1/cases/00000000-0000-0000-0000-000000000000",
            headers=_auth(token),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/cases/{case_id} — Update
# ---------------------------------------------------------------------------

class TestUpdateCase:

    @pytest.mark.asyncio
    async def test_update_title_returns_200(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "updatecase@example.com")
        case = await _create_case(app_client, token)
        resp = await app_client.put(
            f"/api/v1/cases/{case['id']}",
            headers=_auth(token),
            json={"title": "Updated defective product complaint title"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Updated defective product complaint title"

    @pytest.mark.asyncio
    async def test_update_empty_body_returns_400(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "emptyupdate_case@example.com")
        case = await _create_case(app_client, token)
        resp = await app_client.put(
            f"/api/v1/cases/{case['id']}",
            headers=_auth(token),
            json={},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_update_other_users_case_returns_404(self, app_client: AsyncClient):
        token_a = await _register_and_login(app_client, "owner_update_a@example.com")
        token_b = await _register_and_login(app_client, "other_update_b@example.com")
        case = await _create_case(app_client, token_a)

        resp = await app_client.put(
            f"/api/v1/cases/{case['id']}",
            headers=_auth(token_b),
            json={"title": "Attempt to modify other users case"},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/cases/{case_id} — Delete
# ---------------------------------------------------------------------------

class TestDeleteCase:

    @pytest.mark.asyncio
    async def test_delete_own_case_returns_200(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "deletecase@example.com")
        case = await _create_case(app_client, token)
        resp = await app_client.delete(f"/api/v1/cases/{case['id']}", headers=_auth(token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_deleted_case_not_retrievable(self, app_client: AsyncClient):
        token = await _register_and_login(app_client, "deletedgone@example.com")
        case = await _create_case(app_client, token)
        await app_client.delete(f"/api/v1/cases/{case['id']}", headers=_auth(token))
        get_resp = await app_client.get(f"/api/v1/cases/{case['id']}", headers=_auth(token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_other_users_case_returns_404(self, app_client: AsyncClient):
        token_a = await _register_and_login(app_client, "owner_del_a@example.com")
        token_b = await _register_and_login(app_client, "other_del_b@example.com")
        case = await _create_case(app_client, token_a)

        resp = await app_client.delete(f"/api/v1/cases/{case['id']}", headers=_auth(token_b))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_without_token_returns_401_or_403(self, app_client: AsyncClient):
        resp = await app_client.delete("/api/v1/cases/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (401, 403)
