"""
Memory Compressor & Summarizer.
Uses the LLM Router to compress conversation turns into dense semantic memories.
Implements duplicate detection to avoid redundant memory storage.
"""

import hashlib
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.router import llm_router
from app.ai.schemas import LLMMessage, LLMRequest, MessageRole
from app.config import settings
from app.core.logging import logger
from app.memory.metrics import memory_metrics
from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryCategory, MemoryCreate, MemoryEntry, MemoryType


# Default compression system prompt
COMPRESSION_SYSTEM_PROMPT = """You are a memory compression engine for an AI Operating System.
Your task is to compress conversation history into dense, information-rich semantic memories.
Extract only the most important facts, decisions, preferences, and goals.
Output should be concise (3-5 bullet points maximum).
Format: plain text, no markdown, one key fact per line."""

COMPRESSION_USER_TEMPLATE = """Compress the following conversation turns into key memories:

{turns}

Return only the most important facts and insights (3-5 bullet points maximum)."""


class MemoryCompressor:
    """
    Compresses and summarizes conversation history into long-term semantic memories.
    Handles:
    - LLM-based summarization
    - Content deduplication via content hash
    - Automatic memory type assignment
    - Configurable compression threshold
    """

    def __init__(self) -> None:
        self._seen_hashes: set = set()  # In-memory dedup cache (per process)

    def _content_hash(self, content: str) -> str:
        """SHA-256 fingerprint for duplicate detection."""
        normalized = " ".join(content.lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def _is_duplicate(self, content: str) -> bool:
        """Returns True if this content has been compressed before in this session."""
        h = self._content_hash(content)
        if h in self._seen_hashes:
            return True
        self._seen_hashes.add(h)
        return False

    async def compress_conversation(
        self,
        db: AsyncSession,
        conversation_turns: List[str],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        project_id: Optional[str] = None,
        importance_score: float = 0.8,
        model: Optional[str] = None
    ) -> MemoryEntry:
        """
        Compresses multiple conversation turns into a semantic long-term memory using LLM.

        Args:
            db: Async SQLAlchemy session
            conversation_turns: List of raw conversation turn strings
            user_id: Owner user ID
            conversation_id: Source conversation ID
            project_id: Associated project ID
            importance_score: Importance weight for the compressed memory
            model: Optional override for the LLM model (defaults to best available)

        Returns:
            MemoryEntry of the stored compressed memory
        """
        if len(conversation_turns) < settings.MEMORY_COMPRESSION_THRESHOLD:
            logger.info(
                "Compression skipped — too few turns",
                turns=len(conversation_turns),
                threshold=settings.MEMORY_COMPRESSION_THRESHOLD
            )
            # Store as-is with reduced importance
            combined = "Compressed Knowledge: " + "\n".join(conversation_turns)
            return await self._store_memory(
                db, combined, user_id, conversation_id, project_id,
                importance_score, MemoryType.CONVERSATION
            )

        combined_text = "\n".join(f"[Turn {i+1}]: {turn}" for i, turn in enumerate(conversation_turns))
        user_prompt = COMPRESSION_USER_TEMPLATE.format(turns=combined_text)

        # Select best available model (prefer a real LLM; fall back to mock)
        compression_model = model or "mock-gpt"
        if settings.OPENAI_API_KEY:
            compression_model = "gpt-3.5-turbo"
        elif settings.ANTHROPIC_API_KEY:
            compression_model = "claude-3-haiku"
        elif settings.GEMINI_API_KEY:
            compression_model = "gemini-1.5-flash"

        llm_req = LLMRequest(
            model=compression_model,
            messages=[LLMMessage(role=MessageRole.USER, content=user_prompt)],
            system_prompt=COMPRESSION_SYSTEM_PROMPT,
            max_tokens=512,
            temperature=0.1
        )

        try:
            llm_res = await llm_router.generate_completion(llm_req)
            summary_content = "Compressed Knowledge: " + llm_res.content.strip()
        except Exception as e:
            logger.warning("LLM compression failed — storing raw summary", error=str(e))
            summary_content = f"Compressed Knowledge: {len(conversation_turns)} conversation turns."


        # Deduplication check
        if self._is_duplicate(summary_content):
            logger.info("Compression result is duplicate — skipping storage")
            # Return a dummy entry to maintain API contract
            return MemoryEntry(
                content=summary_content,
                category=MemoryCategory.SEMANTIC,
                memory_type=MemoryType.CONVERSATION,
                importance_score=importance_score,
                user_id=user_id,
                conversation_id=conversation_id,
                project_id=project_id,
                source="conversation_compression",
                metadata={"compressed": True, "duplicate": True, "turn_count": len(conversation_turns)}
            )

        memory_metrics.record_compression()

        return await self._store_memory(
            db=db,
            content=summary_content,
            user_id=user_id,
            conversation_id=conversation_id,
            project_id=project_id,
            importance_score=importance_score,
            memory_type=MemoryType.CONVERSATION,
            metadata={"source": "conversation_compression", "turn_count": len(conversation_turns)}
        )

    async def summarize_and_store(
        self,
        db: AsyncSession,
        content: str,
        memory_type: MemoryType = MemoryType.KNOWLEDGE,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        importance_score: float = 0.7
    ) -> MemoryEntry:
        """
        Summarizes a single document/content block and stores it as a knowledge memory.
        Used for document ingestion and knowledge base updates.
        """
        summarize_model = "mock-gpt"
        if settings.OPENAI_API_KEY:
            summarize_model = "gpt-3.5-turbo"

        llm_req = LLMRequest(
            model=summarize_model,
            messages=[LLMMessage(
                role=MessageRole.USER,
                content=f"Summarize the following content into 3-5 key facts:\n\n{content}"
            )],
            system_prompt="You are a knowledge extraction engine. Extract key facts concisely.",
            max_tokens=256,
            temperature=0.1
        )

        try:
            llm_res = await llm_router.generate_completion(llm_req)
            summary = llm_res.content.strip()
        except Exception as e:
            logger.warning("LLM summarization failed — storing original", error=str(e))
            summary = content[:500]

        return await self._store_memory(
            db=db,
            content=summary,
            user_id=user_id,
            project_id=project_id,
            importance_score=importance_score,
            memory_type=memory_type,
            metadata={"source": "document_summarization", "original_length": len(content)}
        )

    async def _store_memory(
        self,
        db: AsyncSession,
        content: str,
        user_id: Optional[str],
        conversation_id: Optional[str] = None,
        project_id: Optional[str] = None,
        importance_score: float = 0.7,
        memory_type: MemoryType = MemoryType.GENERAL,
        metadata: Optional[dict] = None
    ) -> MemoryEntry:
        """Internal helper — creates a memory record via MemoryManager."""
        # Import here to avoid circular dependency
        from app.memory.manager import memory_manager
        mem_create = MemoryCreate(
            content=content,
            category=MemoryCategory.SEMANTIC,
            memory_type=memory_type,
            importance_score=importance_score,
            conversation_id=conversation_id,
            project_id=project_id,
            source="compression",
            metadata=metadata or {}
        )
        return await memory_manager.store(db, mem_create, user_id=user_id)


memory_compressor = MemoryCompressor()
