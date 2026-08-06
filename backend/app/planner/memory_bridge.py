"""
Planner Memory Bridge — Integrates Enterprise Memory Engine (Sprint 3) into the planning & execution pipeline.
Pre-retrieves user context, preferences, and workflows before planning; stores execution outcomes post-execution.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.memory.manager import memory_manager
from app.memory.schemas import MemoryCategory, MemoryCreate, MemoryQuery, MemoryType
from app.planner.schemas import ExecutionPlan

logger = structlog.get_logger(__name__)


class PlannerMemoryBridge:
    """Interfaces Planner with Enterprise Memory Engine."""

    @classmethod
    async def retrieve_context_memories(
        cls,
        db: AsyncSession,
        goal: str,
        user_id: Optional[str] = None
    ) -> List[str]:
        """Retrieves relevant user preferences and past workflow memories before planning."""
        try:
            query = MemoryQuery(
                query=f"User preferences and workflow history for: {goal}",
                top_k=3,
                min_importance=0.3
            )
            results = await memory_manager.retrieve(db=db, query=query, user_id=user_id)
            context_strings = [r.entry.content for r in results]
            logger.info("Retrieved memory context for planning", count=len(context_strings))
            return context_strings
        except Exception as e:
            logger.warning("Planner memory pre-retrieval warning", error=str(e))
            return []

    @classmethod
    async def store_execution_outcome(
        cls,
        db: AsyncSession,
        plan: ExecutionPlan,
        success: bool,
        user_id: Optional[str] = None
    ) -> None:
        """Stores completed plan summary and execution outcome into Memory Engine."""
        try:
            status_str = "SUCCESS" if success else "FAILED"
            content = f"Workflow Plan '{plan.plan_id}' [{status_str}]: Goal '{plan.goal}'. Executed {len(plan.subtasks)} tasks with policy {plan.policy.value}."

            mem_create = MemoryCreate(
                content=content,
                category=MemoryCategory.LONG_TERM_EPISODIC,
                memory_type=MemoryType.WORKFLOW,
                importance_score=0.8 if success else 0.6,
                tags=["workflow", "execution_plan", plan.state.value.lower()],
                metadata={"plan_id": plan.plan_id, "state": plan.state.value, "success": success}
            )

            await memory_manager.store(db=db, memory_in=mem_create, user_id=user_id)
            logger.info("Stored execution outcome in Memory Engine", plan_id=plan.plan_id)
        except Exception as e:
            logger.warning("Planner memory post-storage warning", error=str(e))


memory_bridge = PlannerMemoryBridge()
