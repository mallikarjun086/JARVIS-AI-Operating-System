"""
Memory Retrieval Engine — Full Semantic Retrieval Pipeline.
Pipeline: Query → Embed → ChromaDB Similarity Search → Metadata Filter → Multi-Factor Rank → Top-K

Supports:
- Namespace-scoped search (per user / per project)
- Score threshold filtering
- Date range filtering
- Tag and type filtering
- Context match boosting
"""

import time
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.memory.embedding import embedding_engine
from app.memory.metrics import memory_metrics
from app.memory.ranking import ranker
from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryEntry, MemoryQuery, MemorySearchResult
from app.memory.vector_store import chroma_store


class MemoryRetriever:
    """
    Orchestrates the end-to-end memory retrieval pipeline:
    1. Embed the query text
    2. Search ChromaDB for nearest neighbors
    3. Load full metadata from SQL repository
    4. Apply additional filters (tags, date range)
    5. Multi-factor rank results
    6. Return top-k MemorySearchResult
    """

    async def retrieve(
        self,
        query: MemoryQuery,
        db: AsyncSession,
        user_id: Optional[str] = None,
        chroma_top_k_multiplier: int = 5
    ) -> List[MemorySearchResult]:
        """
        Full semantic retrieval pipeline.

        Args:
            query: MemoryQuery with text, filters, and top-k target
            db: SQLAlchemy async session for metadata fetching
            user_id: Optional user ID for isolation (None = cross-user search)
            chroma_top_k_multiplier: Fetch N× more from ChromaDB before ranking (improves recall)

        Returns:
            Ranked list of MemorySearchResult
        """
        start_time = time.time()

        # Stage 1: Embed the query
        embed_start = time.time()
        query_vector = await embedding_engine.embed(query.query)
        embed_ms = (time.time() - embed_start) * 1000.0
        memory_metrics.record_embedding(embed_ms)

        # Stage 2: Build ChromaDB metadata filter (where clause)
        chroma_where = self._build_chroma_where(query, user_id)

        # Stage 3: ChromaDB vector similarity search
        search_start = time.time()
        chroma_k = min(query.top_k * chroma_top_k_multiplier, 200)
        vector_results = await chroma_store.search(
            query_vector=query_vector,
            top_k=chroma_k,
            where=chroma_where if chroma_where else None
        )
        search_ms = (time.time() - search_start) * 1000.0
        memory_metrics.record_search(search_ms)

        if not vector_results:
            # Fallback: load directly from SQL with metadata filters
            return await self._fallback_sql_retrieve(query, db, user_id, query_vector)

        # Stage 4: Load full memory entries from SQL by vector_id
        vector_ids = [r.doc_id for r in vector_results]
        similarity_map: Dict[str, float] = {r.doc_id: r.similarity for r in vector_results}

        repo = MemoryRepository(db)
        candidates = await repo.list_by_vector_ids(vector_ids)

        # Stage 5: Apply post-filters (archived, date range, tags, importance)
        candidates = self._apply_filters(candidates, query, include_archived=query.include_archived)

        # Stage 6: Multi-factor rank with ChromaDB similarity scores
        results = ranker.rank(
            query=query,
            candidates=candidates,
            similarity_map=similarity_map,
            score_threshold=query.score_threshold
        )

        # Stage 7: Update recall counts
        recalled_ids = [r.entry.id for r in results]
        if recalled_ids:
            await repo.increment_recall_count(recalled_ids)

        total_ms = (time.time() - start_time) * 1000.0
        memory_metrics.record_recall(total_ms)

        logger.info(
            "Memory retrieval complete",
            query_len=len(query.query),
            chroma_results=len(vector_results),
            after_filter=len(candidates),
            returned=len(results),
            total_ms=round(total_ms, 1)
        )

        return results

    async def _fallback_sql_retrieve(
        self,
        query: MemoryQuery,
        db: AsyncSession,
        user_id: Optional[str],
        query_vector: List[float]
    ) -> List[MemorySearchResult]:
        """
        Fallback retrieval from SQL when ChromaDB has no results.
        Performs full scan with filters — slower but safe.
        """
        logger.warning("ChromaDB returned no results — falling back to SQL metadata scan")
        repo = MemoryRepository(db)
        candidates = await repo.list_active_memories(
            user_id=user_id,
            categories=query.categories,
            memory_types=query.memory_types,
            conversation_id=query.conversation_id,
            project_id=query.project_id,
            min_importance=query.min_importance,
            date_from=query.date_from,
            date_to=query.date_to,
            tags=query.tags,
            include_archived=query.include_archived
        )
        return ranker.rank(query, candidates, similarity_map=None, score_threshold=query.score_threshold)

    def _build_chroma_where(
        self,
        query: MemoryQuery,
        user_id: Optional[str]
    ) -> Optional[Dict]:
        """
        Builds a ChromaDB `where` clause from query filters.
        ChromaDB supports $and, $or, $eq, $ne, $in operators.
        """
        conditions = []

        if user_id:
            conditions.append({"user_id": {"$eq": user_id}})
        if query.project_id:
            conditions.append({"project_id": {"$eq": query.project_id}})
        if query.conversation_id:
            conditions.append({"conversation_id": {"$eq": query.conversation_id}})
        if not query.include_archived:
            conditions.append({"archived": {"$eq": False}})
        if query.min_importance > 0:
            conditions.append({"importance_score": {"$gte": query.min_importance}})

        if len(conditions) == 0:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def _apply_filters(
        self,
        candidates: List[MemoryEntry],
        query: MemoryQuery,
        include_archived: bool = False
    ) -> List[MemoryEntry]:
        """Applies post-retrieval filters on the SQL candidate list."""
        from datetime import datetime

        now = datetime.utcnow()
        result = []
        for entry in candidates:
            # Skip archived unless requested
            if entry.archived and not include_archived:
                continue
            # Skip expired
            if entry.expires_at and entry.expires_at <= now:
                continue
            # Date range
            if query.date_from and entry.created_at < query.date_from:
                continue
            if query.date_to and entry.created_at > query.date_to:
                continue
            # Category filter
            if query.categories and entry.category not in query.categories:
                continue
            # Memory type filter
            if query.memory_types and entry.memory_type not in query.memory_types:
                continue
            # Tag filter (OR logic)
            if query.tags and not any(t in entry.tags for t in query.tags):
                continue
            # Importance threshold
            if entry.importance_score < query.min_importance:
                continue
            result.append(entry)
        return result


# Module-level singleton
memory_retriever = MemoryRetriever()
