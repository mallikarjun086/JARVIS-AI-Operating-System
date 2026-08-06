"""
Plan Explainer — Generates human-readable plan reasoning, risk assessment, and dependency explanations.
"""

from typing import List
from app.planner.schemas import PlanExplanation, PlanTask, ResourceEstimate
from app.tools.schemas import PermissionLevel


class PlanExplainer:
    """Generates clear explanations and risk assessments for generated execution plans."""

    @classmethod
    def explain_plan(
        cls,
        goal: str,
        intent_summary: str,
        subtasks: List[PlanTask],
        estimate: ResourceEstimate
    ) -> PlanExplanation:
        """Computes human-readable reasoning summary and risk assessment."""
        task_order = [f"{t.task_id}: {t.title} ({t.tool_required})" for t in subtasks]
        
        dep_count = sum(len(t.dependencies) for t in subtasks)
        dep_summary = f"{len(subtasks)} tasks with {dep_count} explicit prerequisite dependency links."

        runtime_str = f"~{estimate.estimated_runtime_seconds} seconds across {estimate.parallel_batches} execution batch layers."

        perm_str = f"Highest permission required: {estimate.max_permission_level.name}."

        # Risk assessment
        if estimate.max_permission_level >= PermissionLevel.DANGEROUS:
            risk = "HIGH: Plan contains sensitive or administrative system tool operations requiring user authorization."
        elif estimate.max_permission_level >= PermissionLevel.SYSTEM:
            risk = "MEDIUM: Plan includes command execution and system process operations."
        else:
            risk = "LOW: Plan consists of safe read/write and data operations."

        return PlanExplanation(
            goal=goal,
            reasoning_summary=f"Plan constructed to fulfill '{goal}'. {intent_summary}",
            task_order=task_order,
            dependency_explanation=dep_summary,
            estimated_runtime=runtime_str,
            permission_requirements=perm_str,
            risk_assessment=risk,
            confidence_score=0.95
        )


plan_explainer = PlanExplainer()
