"""
Browser Memory Bridge — Integrates Enterprise Memory Engine (Sprint 3) with Browser Automation Engine.
Stores visited pages, successful web workflows, and browser navigation metadata (NEVER storing passwords!).
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.memory.manager import memory_manager
from app.memory.schemas import MemoryCategory, MemoryCreate, MemoryQuery, MemoryType

logger = structlog.get_logger(__name__)


class BrowserMemoryBridge:
    """Interfaces Browser Automation Engine with Enterprise Memory Engine."""

    @classmethod
    async def retrieve_browser_memories(
        cls,
        db: AsyncSession,
        url_or_topic: str,
        user_id: Optional[str] = None
    ) -> List[str]:
        """Retrieves past navigation history and website preferences."""
        try:
            query = MemoryQuery(
                query=f"Browser history and preferences for: {url_or_topic}",
                top_k=3,
                min_importance=0.3
            )
            results = await memory_manager.retrieve(db=db, query=query, user_id=user_id)
            return [r.entry.content for r in results]
        except Exception as e:
            logger.warning("Browser memory pre-retrieval warning", error=str(e))
            return []

    @classmethod
    async def store_visited_page(
        cls,
        db: AsyncSession,
        url: str,
        title: str,
        extracted_text: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Stores visited web page metadata into Long-Term Memory (no password data)."""
        try:
            content = f"Visited Web Page '{title}' at URL: {url}. Text snippet: {(extracted_text or '')[:200]}"
            mem_create = MemoryCreate(
                content=content,
                category=MemoryCategory.LONG_TERM_EPISODIC,
                memory_type=MemoryType.CONVERSATION_LOG,
                importance_score=0.5,
                tags=["browser", "web_page", "history"],
                metadata={"url": url, "title": title}
            )
            await memory_manager.store(db=db, memory_in=mem_create, user_id=user_id)
            logger.info("Stored browser page history in Memory Engine", url=url)
        except Exception as e:
            logger.warning("Browser memory post-storage warning", error=str(e))


browser_memory_bridge = BrowserMemoryBridge()
