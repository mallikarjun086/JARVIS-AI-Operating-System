"""
Desktop Memory Bridge — Integrates Enterprise Memory Engine (Sprint 3) with Desktop Automation Engine.
Stores frequently used apps, window layouts, and automation sequences (NEVER storing passwords or clipboard secrets!).
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.memory.manager import memory_manager
from app.memory.schemas import MemoryCategory, MemoryCreate, MemoryQuery, MemoryType

logger = structlog.get_logger(__name__)


class DesktopMemoryBridge:
    """Interfaces Desktop Automation Engine with Enterprise Memory Engine."""

    @classmethod
    async def retrieve_desktop_memories(
        cls,
        db: AsyncSession,
        app_or_topic: str,
        user_id: Optional[str] = None
    ) -> List[str]:
        """Retrieves past desktop workflows and app layouts."""
        try:
            query = MemoryQuery(
                query=f"Desktop workflows and app layouts for: {app_or_topic}",
                top_k=3,
                min_importance=0.3
            )
            results = await memory_manager.retrieve(db=db, query=query, user_id=user_id)
            return [r.entry.content for r in results]
        except Exception as e:
            logger.warning("Desktop memory pre-retrieval warning", error=str(e))
            return []

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """Scubs passwords, tokens, API keys, and sensitive content from memory string."""
        import re
        # Scrub passwords, bearer tokens, secret patterns
        text = re.sub(r'(?i)(password|passwd|secret|api_key|token)\s*=\s*[\'"][^\'"]+[\'"]', r'\1="[REDACTED]"', text)
        text = re.sub(r'(?i)(bearer)\s+[a-zA-Z0-9\-\._~\+\/]+=*', r'Bearer [REDACTED]', text)
        return text

    @classmethod
    async def store_automation_sequence(
        cls,
        db: AsyncSession,
        app_name: str,
        window_title: str,
        action_summary: str,
        user_id: Optional[str] = None
    ) -> None:
        """Stores successful desktop automation sequence into Memory Engine (no password/secret content)."""
        try:
            sanitized_summary = cls.redact_secrets(action_summary)
            content = f"Desktop Automation Sequence for App '{app_name}' Window '{window_title}': {sanitized_summary}"
            mem_create = MemoryCreate(
                content=content,
                category=MemoryCategory.LONG_TERM_EPISODIC,
                memory_type=MemoryType.WORKFLOW,
                importance_score=0.6,
                tags=["desktop", "automation", "sequence"],
                metadata={"app_name": app_name, "window_title": window_title}
            )
            await memory_manager.store(db=db, memory_in=mem_create, user_id=user_id)
            logger.info("Stored desktop sequence in Memory Engine", app_name=app_name)
        except Exception as e:
            logger.warning("Desktop memory post-storage warning", error=str(e))


desktop_memory_bridge = DesktopMemoryBridge()
