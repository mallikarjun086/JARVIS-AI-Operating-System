"""
Workflow Versioning Engine (Sprint 10).
Manages Workflow Version, Template Version, Schema Version, and Migration Version.
Ensures running workflows continue using the exact version they started with.
"""

from typing import Dict, Optional
import structlog

from app.workflow.schemas import VersionInfo, WorkflowDefinition, WorkflowInstance

logger = structlog.get_logger(__name__)


class WorkflowVersioningEngine:
    """Manages versioning specifications and schema migrations for workflow definitions."""

    @classmethod
    def get_current_version_info(cls) -> VersionInfo:
        """Returns standard system version information."""
        return VersionInfo(
            workflow_version="1.0.0",
            template_version="1.0.0",
            schema_version="1.0.0",
            migration_version="1.0.0"
        )

    @classmethod
    def bind_version_to_instance(cls, instance: WorkflowInstance, definition: WorkflowDefinition) -> WorkflowInstance:
        """Binds definition version info immutably to instance execution state."""
        instance.version_info = definition.version_info
        logger.info("Bound immutable version info to instance", instance_id=instance.instance_id, version=definition.version_info.workflow_version)
        return instance


workflow_versioning_engine = WorkflowVersioningEngine()
