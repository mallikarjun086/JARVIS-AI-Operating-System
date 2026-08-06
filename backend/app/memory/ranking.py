"""
Multi-Factor Memory Ranking Engine.
Calculates unified relevance scores combining:
- ChromaDB semantic similarity (cosine)
- Recency (exponential time decay)
- Importance (user-assigned weight)
- Access/Recall frequency (logarithmic scaling)
- Project context match boost
- Conversation context match boost
"""

import math
from datetime import datetime
from typing import List, Optional

from app.memory.schemas import MemoryEntry, MemoryQuery, MemorySearchResult


class MemoryRanker:
    """
    Multi-factor memory ranker producing a composite scored result list.
    Weights are tunable at instantiation time for different use cases.
    """

    def __init__(
        self,
        weight_similarity: float = 0.45,
        weight_importance: float = 0.25,
        weight_recency: float = 0.15,
        weight_frequency: float = 0.10,
        weight_context: float = 0.05,
        recency_decay_rate: float = 0.005,  # slower decay for long-term memories
    ) -> None:
        self.w_sim = weight_similarity
        self.w_imp = weight_importance
        self.w_rec = weight_recency
        self.w_freq = weight_frequency
        self.w_ctx = weight_context
        self.decay_rate = recency_decay_rate

    def rank(
        self,
        query: MemoryQuery,
        candidates: List[MemoryEntry],
        similarity_map: Optional[dict] = None,
        score_threshold: float = 0.0
    ) -> List[MemorySearchResult]:
        """
        Ranks memory entries using multi-factor composite scoring.

        Args:
            query: The original memory query with context (project_id, conversation_id, etc.)
            candidates: List of MemoryEntry objects to rank
            similarity_map: Optional dict {vector_id -> similarity_score} from ChromaDB
            score_threshold: Minimum ranked_score to include in results

        Returns:
            List[MemorySearchResult] sorted by ranked_score descending, top_k results.
        """
        now = datetime.utcnow()
        results: List[MemorySearchResult] = []

        for entry in candidates:
            # 1. Semantic Similarity (from ChromaDB or fallback to 0.5)
            sim_score = 0.5  # default if no similarity available
            if similarity_map:
                if entry.vector_id and entry.vector_id in similarity_map:
                    sim_score = similarity_map[entry.vector_id]
                elif entry.id in similarity_map:
                    sim_score = similarity_map[entry.id]

            # 2. Importance score (already 0-1)
            imp_score = entry.importance_score

            # 3. Recency (exponential decay by hours since creation)
            age_hours = max(0.0, (now - entry.created_at).total_seconds() / 3600.0)
            rec_score = math.exp(-self.decay_rate * age_hours)

            # 4. Access + Recall Frequency (logarithmic, capped at 1.0)
            total_access = entry.access_count + (entry.recall_count * 2)  # recalls weighted higher
            freq_score = min(1.0, math.log1p(total_access) / 6.0)

            # 5. Context Match Boost
            ctx_score = self._compute_context_score(entry, query)

            # Composite Score
            composite = (
                (self.w_sim * sim_score) +
                (self.w_imp * imp_score) +
                (self.w_rec * rec_score) +
                (self.w_freq * freq_score) +
                (self.w_ctx * ctx_score)
            )

            if composite < score_threshold:
                continue

            results.append(
                MemorySearchResult(
                    entry=entry,
                    vector_similarity=round(sim_score, 4),
                    importance_score=round(imp_score, 4),
                    recency_score=round(rec_score, 4),
                    access_frequency_score=round(freq_score, 4),
                    ranked_score=round(composite, 4)
                )
            )

        # Sort by ranked_score descending
        results.sort(key=lambda r: r.ranked_score, reverse=True)
        return results[:query.top_k]

    def _compute_context_score(self, entry: MemoryEntry, query: MemoryQuery) -> float:
        """
        Boosts score when memory context matches query context.
        Considers: project_id match, conversation_id match.
        """
        score = 0.0
        matches = 0

        if query.project_id and entry.project_id == query.project_id:
            score += 0.6
            matches += 1
        if query.conversation_id and entry.conversation_id == query.conversation_id:
            score += 0.4
            matches += 1

        return min(1.0, score) if matches > 0 else 0.0


# ──────────────────────────────────────────────────────────
# Backward-compatible alias (used by existing API endpoint)
# ──────────────────────────────────────────────────────────

class MemoryRankingEngine:
    """Backward-compatible wrapper around MemoryRanker for legacy callers."""

    def __init__(self, **kwargs) -> None:
        self._ranker = MemoryRanker(**kwargs)

    def rank_memories(
        self,
        query: MemoryQuery,
        query_vector: List[float],
        candidates: List[MemoryEntry]
    ) -> List[MemorySearchResult]:
        """Legacy interface: ranks without ChromaDB similarity scores."""
        return self._ranker.rank(query, candidates)


ranking_engine = MemoryRankingEngine()
ranker = MemoryRanker()
