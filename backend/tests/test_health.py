"""
Integration Tests for Health and Readiness APIs.
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Tests GET /api/v1/health endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """Tests GET /api/v1/health/readiness endpoint."""
    response = await client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
