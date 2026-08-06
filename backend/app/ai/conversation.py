"""
Conversation Session & Context Window Manager.
Tracks multi-turn history, enforces token context window truncation rules,
implements session TTL expiry, max-session cap, and automatic memory-safe eviction.
"""

import asyncio
import time
from typing import Dict, List, Optional
import uuid
from app.ai.schemas import LLMMessage, MessageRole
from app.config import settings


class ConversationSession:
    """Represents a single active conversation session."""

    def __init__(self, session_id: Optional[str] = None, system_prompt: Optional[str] = None) -> None:
        self.session_id = session_id or f"conv-{uuid.uuid4().hex[:8]}"
        self.messages: List[LLMMessage] = []
        self._created_at: float = time.time()
        self._last_accessed: float = time.time()

        if system_prompt:
            self.messages.append(LLMMessage(role=MessageRole.SYSTEM, content=system_prompt))

    def touch(self) -> None:
        """Updates last-accessed timestamp (resets TTL countdown)."""
        self._last_accessed = time.time()

    def is_expired(self, ttl_seconds: int) -> bool:
        """Returns True if the session has not been accessed within the TTL window."""
        return (time.time() - self._last_accessed) > ttl_seconds

    def add_user_message(self, content: str) -> None:
        """Appends user message turn and touches the session."""
        self.messages.append(LLMMessage(role=MessageRole.USER, content=content))
        self.touch()

    def add_assistant_message(self, content: str) -> None:
        """Appends assistant response turn and touches the session."""
        self.messages.append(LLMMessage(role=MessageRole.ASSISTANT, content=content))
        self.touch()

    def estimate_total_tokens(self) -> int:
        """Rough token count estimation (4 chars per token average)."""
        return sum(len(m.content) // 4 + 4 for m in self.messages)

    def truncate_context_window(self, max_context_tokens: int = 4096) -> List[LLMMessage]:
        """
        Truncates oldest user/assistant turns if total estimated tokens
        exceed context limit, while always preserving system prompt.
        """
        if self.estimate_total_tokens() <= max_context_tokens:
            return self.messages

        # Separate system messages from turn history
        system_msgs = [m for m in self.messages if m.role == MessageRole.SYSTEM]
        turn_msgs = [m for m in self.messages if m.role != MessageRole.SYSTEM]

        system_tokens = sum(len(m.content) // 4 + 4 for m in system_msgs)
        allowed_turn_tokens = max_context_tokens - system_tokens

        # Preserve most recent turns (sliding window from end)
        pruned_turns: List[LLMMessage] = []
        accumulated = 0
        for msg in reversed(turn_msgs):
            msg_tokens = len(msg.content) // 4 + 4
            if accumulated + msg_tokens <= allowed_turn_tokens:
                pruned_turns.insert(0, msg)
                accumulated += msg_tokens
            else:
                break

        self.messages = system_msgs + pruned_turns
        return self.messages


class ConversationManager:
    """
    Manages active conversation sessions in memory.
    Features: session TTL, maximum session cap, LRU-style eviction,
    and automatic background cleanup.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, ConversationSession] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    def start_cleanup_task(self) -> None:
        """Starts the background session cleanup task (call once at startup)."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """Cancels the background cleanup task gracefully."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self) -> None:
        """Background coroutine that evicts expired sessions every 60 seconds."""
        while True:
            try:
                await asyncio.sleep(60)
                await self._evict_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def _evict_expired_sessions(self) -> int:
        """
        Removes all sessions that have exceeded the TTL.
        Returns the number of evicted sessions.
        """
        ttl = settings.SESSION_TTL_SECONDS
        async with self._lock:
            expired = [
                sid for sid, session in self.sessions.items()
                if session.is_expired(ttl)
            ]
            for sid in expired:
                del self.sessions[sid]
            if expired:
                from app.core.logging import logger
                logger.info(
                    "Evicted expired conversation sessions",
                    count=len(expired),
                    remaining=len(self.sessions)
                )
            return len(expired)

    async def _enforce_max_sessions(self) -> None:
        """
        If session count exceeds the maximum cap, evicts the oldest-accessed sessions
        until within the limit (LRU eviction strategy).
        """
        max_sessions = settings.MAX_CONCURRENT_SESSIONS
        if len(self.sessions) < max_sessions:
            return
        # Sort by last_accessed ascending (oldest first)
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda kv: kv[1]._last_accessed
        )
        to_evict = len(self.sessions) - max_sessions + 1
        for sid, _ in sorted_sessions[:to_evict]:
            del self.sessions[sid]

    async def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> ConversationSession:
        """Fetches existing session or initializes a new one, enforcing limits."""
        async with self._lock:
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                session.touch()
                return session

            # Enforce max sessions before creating new one
            await self._enforce_max_sessions()

            session = ConversationSession(session_id=session_id, system_prompt=system_prompt)
            self.sessions[session.session_id] = session
            return session

    async def clear_session(self, session_id: str) -> bool:
        """Clears a conversation session by ID."""
        async with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
        return False

    def session_count(self) -> int:
        """Returns the number of active sessions (non-blocking)."""
        return len(self.sessions)


conversation_manager = ConversationManager()
