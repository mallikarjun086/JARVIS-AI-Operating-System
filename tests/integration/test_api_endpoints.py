"""
Integration Tests for REST API Endpoints.
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """Tests GET /api/v1/health endpoint."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["app_name"] == "JARVIS AI Operating System"


@pytest.mark.asyncio
async def test_process_lifecycle_api(async_client: AsyncClient):
    """Tests POST, GET, and DELETE process endpoints."""
    # 1. Create process
    payload = {
        "agent_name": "TestAgent",
        "role": "Integration Test Agent",
        "goal": "Verify API lifecycle",
        "priority": 2,
        "max_steps": 5,
        "permissions": ["READ_ONLY"]
    }
    create_resp = await async_client.post("/api/v1/processes", json=payload)
    assert create_resp.status_code == 201
    proc_data = create_resp.json()
    proc_id = proc_data["process_id"]
    assert proc_data["agent_name"] == "TestAgent"

    # 2. Get process details
    get_resp = await async_client.get(f"/api/v1/processes/{proc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["process_id"] == proc_id

    # 3. List processes
    list_resp = await async_client.get("/api/v1/processes")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


@pytest.mark.asyncio
async def test_memory_api(async_client: AsyncClient):
    """Tests POST /api/v1/memory and POST /api/v1/memory/search."""
    # Add memory
    mem_payload = {
        "content": "JARVIS Kernel memory indexing test payload.",
        "memory_type": "EPISODIC",
        "importance": 0.9,
        "metadata": {"test": "integration"}
    }
    add_resp = await async_client.post("/api/v1/memory", json=mem_payload)
    assert add_resp.status_code == 201
    assert "id" in add_resp.json()

    # Search memory
    search_payload = {
        "query": "memory indexing test",
        "top_k": 3,
        "min_similarity": 0.1
    }
    search_resp = await async_client.post("/api/v1/memory/search", json=search_payload)
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1
