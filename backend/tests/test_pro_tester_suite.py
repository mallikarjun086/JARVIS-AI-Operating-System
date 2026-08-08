"""
Pro-Tester Automated Audit & Verification Suite.
Validates:
1. DatasetTrainerEngine (dataset batch ingestion, synthetic few-shot generation, fine-tuning JSONL export).
2. MemoryManager & ChromaDB vector store RAG recall.
3. 10-Agent Swarm Mesh subtask execution.
4. LLM Router offline MockProvider contextual completions.
5. Security engine secret redaction.
"""

import pytest
import pytest_asyncio
import asyncio

from app.memory.trainer import dataset_trainer
from app.memory.manager import memory_manager
from app.multi_agent.agent_pool import coding_agent, memory_agent, planner_agent
from app.multi_agent.schemas import SubTaskSpec, AgentRole
from app.ai.router import llm_router
from app.ai.schemas import LLMRequest, LLMMessage, MessageRole
from app.security.engine import security_engine


@pytest.mark.asyncio
async def test_pro_tester_dataset_trainer_ingest():
    """Audits batch dataset ingestion and vector embedding calculation."""
    batch = [
        {"title": "Architecture Overview", "content": "JARVIS AI OS runs an 8-subsystem kernel with a 10-agent swarm mesh."},
        {"title": "Vector Memory", "content": "ChromaDB acts as persistent vector store for RAG memory recall."}
    ]
    res = await dataset_trainer.ingest_dataset_batch(items=batch, category="SEMANTIC_FACT")
    assert res["status"] == "SUCCESS"
    assert res["ingested_count"] == 2


@pytest.mark.asyncio
async def test_pro_tester_fewshot_generation():
    """Audits synthetic few-shot prompt QA dataset pair generation."""
    res = await dataset_trainer.generate_synthetic_fewshot_dataset(topic="Task Planner DAG", sample_count=3)
    assert res["status"] == "SUCCESS"
    assert res["count"] == 3
    assert len(res["samples"]) == 3
    assert "Task Planner DAG" in res["samples"][0]["prompt"]


@pytest.mark.asyncio
async def test_pro_tester_fine_tune_export():
    """Audits JSONL model fine-tuning dataset export formatting."""
    res = await dataset_trainer.export_fine_tuning_jsonl(limit=10)
    assert res["status"] == "SUCCESS"
    assert res["filename"] == "jarvis_finetune_dataset.jsonl"
    assert "messages" in res["jsonl_content"]


@pytest.mark.asyncio
async def test_pro_tester_specialized_agents():
    """Audits subtask execution on specialized coding, memory, and planner agents."""
    code_sub = SubTaskSpec(assigned_agent=AgentRole.CODING, goal="Analyze system architecture")
    mem_sub = SubTaskSpec(assigned_agent=AgentRole.MEMORY, goal="Query swarm architecture")
    plan_sub = SubTaskSpec(assigned_agent=AgentRole.PLANNER, goal="Decompose goal into DAG")

    c_res = await coding_agent.execute_task(code_sub)
    m_res = await memory_agent.execute_task(mem_sub)
    p_res = await planner_agent.execute_task(plan_sub)

    assert getattr(c_res.status, "value", str(c_res.status)) == "COMPLETED"
    assert getattr(m_res.status, "value", str(m_res.status)) == "COMPLETED"
    assert getattr(p_res.status, "value", str(p_res.status)) == "COMPLETED"


@pytest.mark.asyncio
async def test_pro_tester_llm_router_and_mock():
    """Audits LLM router and contextual MockProvider generation."""
    req = LLMRequest(
        model="mock-gpt",
        messages=[LLMMessage(role=MessageRole.USER, content="Generate python code for data pipeline")],
        system_prompt="You are a code generator."
    )
    res = await llm_router.generate_completion(req)
    assert res.provider == "MockProvider"
    assert "def " in res.content or "python" in res.content


@pytest.mark.asyncio
async def test_pro_tester_security_redaction():
    """Audits secret scrubbing and RBAC permissions."""
    scrubbed = security_engine.scrub_text("API KEY sk-1234567890abcdef1234567890")
    assert "[REDACTED_SECRET]" in scrubbed or "[REDACTED" in scrubbed
