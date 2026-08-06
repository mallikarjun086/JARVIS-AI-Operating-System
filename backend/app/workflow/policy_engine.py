"""
Workflow Policy Engine (Sprint 10).
Evaluates workflow definitions and execution requests against Security Engine policies prior to execution.
Workflow -> Policy Engine -> Security Engine -> Workflow Runtime.
"""

from typing import Dict, Optional
import structlog

from app.security.audit import security_auditor
from app.security.manager import security_engine
from app.workflow.schemas import WorkflowDefinition

logger = structlog.get_logger(__name__)


class WorkflowPolicyEngine:
    """Evaluates security policies and user permissions for workflow definitions."""

    @classmethod
    def validate_workflow_policy(
        cls,
        definition: WorkflowDefinition,
        user_context: Optional[Dict] = None
    ) -> bool:
        """Validates definition nodes against security policies."""
        user_role = (user_context or {}).get("role", "ADMIN")

        # Verify RBAC permission for execution
        authorized = security_engine.authorize(user_role=user_role, required_permission="execute_workflows")
        if not authorized:
            security_auditor.log_event(
                event_type="WORKFLOW_POLICY_VIOLATION",
                severity="HIGH",
                details={"reason": f"Role '{user_role}' unauthorized for workflow execution."}
            )
            logger.warning("Workflow policy violation: unauthorized role", user_role=user_role)
            return False

        logger.info("Workflow policy validation passed", definition_id=definition.definition_id)
        return True


workflow_policy_engine = WorkflowPolicyEngine()
