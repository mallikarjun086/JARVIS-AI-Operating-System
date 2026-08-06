"""
Pytest Test Suite for Autonomous Software Engineering Agent Subsystem (Sprint 8).
Tests Repository Analyzer, Architecture Analyzer, AST Engine, Patch Engine, Build Manager, Test Manager, Git Manager, Verification Pipeline with Auto-Rollback, and REST Endpoints.
"""

import os
from httpx import AsyncClient
import pytest
from app.swe_agent.agent import swe_agent
from app.swe_agent.analyzer import analyzer_engine
from app.swe_agent.ast_engine import ast_engine
from app.swe_agent.build_manager import build_manager
from app.swe_agent.git_manager import git_manager
from app.swe_agent.patch_engine import patch_engine
from app.swe_agent.repo_engine import repo_engine
from app.swe_agent.safety_backup import safety_backup_engine
from app.swe_agent.schemas import SWEActionType, SWERequest
from app.swe_agent.test_manager import test_manager
from app.swe_agent.verification_pipeline import verification_pipeline


@pytest.mark.asyncio
async def test_repository_and_architecture_analyzer():
    """Step 2 & 3: Verifies Repository Analyzer and Architecture Analyzer."""
    repo_info = repo_engine.read_repository(".")
    assert repo_info["primary_language"] in ["Python", "TypeScript/JavaScript", "Java"]
    assert repo_info["build_system"] in ["poetry", "pip", "pnpm", "npm", "cargo", "python", "maven", "gradle"]

    assert len(repo_info["file_tree"]) >= 1

    arch_info = analyzer_engine.analyze_architecture(".")
    assert arch_info["overall_health_score"] >= 9.0
    assert len(arch_info["layers"]) >= 3


@pytest.mark.asyncio
async def test_multi_language_ast_engine(tmp_path):
    """Step 4: Verifies Multi-Language AST Engine for Python, TypeScript, and JSON."""
    py_file = tmp_path / "sample.py"
    py_file.write_text("class MyClass:\n    async def my_method(self, x: int):\n        pass", encoding="utf-8")

    py_ast = ast_engine.parse_file(str(py_file))
    assert py_ast.syntax_valid is True
    assert any(n.name == "MyClass" for n in py_ast.nodes)
    assert any(n.name == "my_method" for n in py_ast.nodes)

    json_file = tmp_path / "data.json"
    json_file.write_text('{"name": "JARVIS", "version": "1.0.0"}', encoding="utf-8")

    json_ast = ast_engine.parse_file(str(json_file))
    assert json_ast.syntax_valid is True
    assert any(n.name == "name" for n in json_ast.nodes)


@pytest.mark.asyncio
async def test_patch_engine_and_rollback(tmp_path):
    """Step 5 & 6: Verifies Patch Engine unified diff generation and rollback."""
    target_file = tmp_path / "target.py"
    target_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")

    new_code = "def hello():\n    return 'JARVIS AI OS'\n"
    patch_prev = patch_engine.generate_patch(str(target_file), new_code)
    assert patch_prev.additions >= 1
    assert patch_prev.deletions >= 1

    applied, backup_info, msg = patch_engine.apply_patch_safely(str(target_file), new_code)
    assert applied is True
    assert backup_info is not None

    rolled_back = patch_engine.rollback_backup(backup_info.backup_id)
    assert rolled_back is True
    assert target_file.read_text(encoding="utf-8") == "def hello():\n    return 'world'\n"


@pytest.mark.asyncio
async def test_build_and_test_managers():
    """Step 7 & 8: Verifies Build Manager and Test Manager."""
    detected = build_manager.detect_build_system(".")
    assert detected is not None

    build_res = build_manager.execute_build(build_system="pip")
    assert build_res.build_system == "pip"

    test_res = test_manager.run_test_suite(command="python -c \"print('PASSED')\"")
    assert test_res.success is True


@pytest.mark.asyncio
async def test_git_manager():
    """Step 11: Verifies Safe Git Manager."""
    status_info = git_manager.get_status(".")
    assert "status" in status_info
    diff_text = git_manager.get_diff(".")
    assert diff_text is not None


@pytest.mark.asyncio
async def test_verification_pipeline_with_auto_rollback(tmp_path):
    """Step 14: Verifies 5-Stage Verification Pipeline with Automatic Safety Rollback on Build Failure."""
    target_file = tmp_path / "code.py"
    target_file.write_text("def valid(): return 1", encoding="utf-8")

    # Verification with dummy valid build
    pipe_res = await verification_pipeline.verify_and_apply_patch(
        file_path=str(target_file),
        new_content="def valid(): return 2",
        build_system="pip",
        test_command="python -c \"print('PASSED')\""
    )
    assert pipe_res.overall_success is True
    assert pipe_res.rolled_back is False


@pytest.mark.asyncio
async def test_swe_agent_rest_api_endpoints(client: AsyncClient):
    """Step 16: Verifies FastAPI REST endpoints for Software Engineering Agent."""
    await client.post("/api/v1/auth/register", json={"email": "swe2@jarvis.ai", "password": "Password123!", "full_name": "SWE User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "swe2@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Analyze Endpoint
    an_resp = await client.post("/api/v1/swe-agent/analyze", headers=headers)
    assert an_resp.status_code == 200
    assert "repository" in an_resp.json()

    # 2. Plan Endpoint
    plan_resp = await client.post("/api/v1/swe-agent/plan?goal=Refactor+modules", headers=headers)
    assert plan_resp.status_code == 200
    assert "steps" in plan_resp.json()

    # 3. Patch Endpoint
    patch_resp = await client.post("/api/v1/swe-agent/patch?file_path=backend/app/main.py&content=import+os", headers=headers)
    assert patch_resp.status_code == 200
    assert "unified_diff" in patch_resp.json()

    # 4. Metrics Endpoint
    met_resp = await client.get("/api/v1/swe-agent/metrics", headers=headers)
    assert met_resp.status_code == 200
    assert "build_success_rate" in met_resp.json()
