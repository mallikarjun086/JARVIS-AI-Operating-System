"""
Workflow Library Engine (Sprint 10 Step 10).
Stores, versions, clones, searches, and archives completed workflow definitions and execution histories.
"""

from typing import Dict, List, Optional
import structlog

from app.workflow.schemas import WorkflowDefinition, WorkflowInstance, WorkflowStatus

logger = structlog.get_logger(__name__)


class WorkflowLibrary:
    """Library manager storing reusable workflow blueprints and instances."""

    def __init__(self) -> None:
        self._definitions: Dict[str, WorkflowDefinition] = {}
        self._archived_definitions: Dict[str, WorkflowDefinition] = {}

    def save_definition(self, definition: WorkflowDefinition) -> WorkflowDefinition:
        """Saves or updates workflow definition in library."""
        self._definitions[definition.definition_id] = definition
        logger.info("Saved workflow definition in library", definition_id=definition.definition_id, name=definition.name)
        return definition

    def clone_definition(self, definition_id: str, new_name: str) -> Optional[WorkflowDefinition]:
        """Clones an existing workflow definition blueprint."""
        orig = self._definitions.get(definition_id)
        if not orig:
            return None

        cloned = WorkflowDefinition(
            name=new_name,
            description=f"Cloned from '{orig.name}' ({orig.definition_id})",
            nodes=orig.nodes,
            cron_schedule=orig.cron_schedule
        )
        self._definitions[cloned.definition_id] = cloned
        logger.info("Cloned workflow definition in library", original_id=definition_id, new_id=cloned.definition_id)
        return cloned

    def search_definitions(self, query: str) -> List[WorkflowDefinition]:
        """Searches workflow definitions by name or description substring."""
        q = query.lower()
        return [
            d for d in self._definitions.values()
            if q in d.name.lower() or q in d.description.lower()
        ]

    def archive_definition(self, definition_id: str) -> bool:
        """Archives a workflow definition."""
        d = self._definitions.pop(definition_id, None)
        if d:
            self._archived_definitions[definition_id] = d
            logger.info("Archived workflow definition", definition_id=definition_id)
            return True
        return False


workflow_library = WorkflowLibrary()
