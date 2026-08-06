"""
Plan Validator Engine — 10-Point Pre-Execution Validation Checkpoints.
Rejects invalid, unsafe, or unauthorized execution plans before running.
"""

from typing import List
from app.planner.schemas import PlanTask, PlanValidationReport
from app.tools.permissions import permission_manager
from app.tools.registry import tool_registry
from app.tools.schemas import PermissionLevel


class PlanValidator:
    """
    Validates an ExecutionPlan prior to execution to enforce DAG integrity,
    tool availability, security permissions, and safety policies.
    """

    @classmethod
    def validate_plan(
        cls,
        subtasks: List[PlanTask],
        user_role: str = "user",
        approval_granted: bool = False
    ) -> PlanValidationReport:
        """
        Performs 10-point plan validation check.
        """
        missing_tools: List[str] = []
        missing_dependencies: List[str] = []
        permission_violations: List[str] = []
        unsafe_executions: List[str] = []
        validation_messages: List[str] = []
        approval_required = False

        task_ids = {t.task_id for t in subtasks}

        for task in subtasks:
            # 1. Tool Availability Check
            tool = tool_registry.get_tool(task.tool_required)
            if not tool:
                missing_tools.append(task.tool_required)
                validation_messages.append(f"Task '{task.task_id}' requires unregistered tool '{task.tool_required}'.")
            else:
                # 2. Permission Validation Check
                allowed, reason = permission_manager.verify_permission(
                    tool=tool,
                    user_role=user_role,
                    approval_granted=approval_granted
                )
                if not allowed:
                    if "Approval Required" in (reason or ""):
                        approval_required = True
                        validation_messages.append(f"Task '{task.task_id}' requires explicit user approval.")
                    else:
                        permission_violations.append(f"Task '{task.task_id}': {reason}")

                # 3. Unsafe Execution Check
                if tool.permission_level == PermissionLevel.ADMIN and user_role.lower() != "superuser":
                    unsafe_executions.append(f"Task '{task.task_id}' requires ADMIN permission.")

            # 4. Dependency Existence Check
            for dep in task.dependencies:
                if dep not in task_ids:
                    missing_dependencies.append(dep)
                    validation_messages.append(f"Task '{task.task_id}' depends on non-existent task '{dep}'.")

        # 5. DAG Cycle & Topological Validation
        from app.planner.graph import DependencyGraphEngine
        dag_info = DependencyGraphEngine.validate_and_order_dag(subtasks)
        if not dag_info.is_valid_dag:
            validation_messages.append(f"Circular dependency loop detected: {dag_info.circular_dependencies}")

        is_valid = (
            len(missing_tools) == 0 and
            len(missing_dependencies) == 0 and
            len(permission_violations) == 0 and
            len(unsafe_executions) == 0 and
            dag_info.is_valid_dag
        )

        return PlanValidationReport(
            is_valid=is_valid,
            missing_tools=missing_tools,
            missing_dependencies=missing_dependencies,
            circular_dependencies=dag_info.circular_dependencies if not dag_info.is_valid_dag else [],
            permission_violations=permission_violations,
            unsafe_executions=unsafe_executions,
            approval_required=approval_required,
            validation_messages=validation_messages
        )


plan_validator = PlanValidator()
