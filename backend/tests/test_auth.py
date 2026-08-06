"""
Integration Tests for Authentication API.
"""

import uuid
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_user_registration_and_login_flow(client: AsyncClient):
    """Tests registration, login, and profile fetching."""
    unique_email = f"testuser_{uuid.uuid4().hex[:6]}@jarvis.ai"

    # 1. Register User
    reg_payload = {
        "email": unique_email,
        "full_name": "Test User",
        "password": "Password123!",
        "is_active": True,
        "is_superuser": False
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == unique_email

    # 2. Login User
    login_data = {
        "username": unique_email,
        "password": "Password123!"
    }
    login_resp = await client.post("/api/v1/auth/login", data=login_data)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Get User Profile with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == unique_email

