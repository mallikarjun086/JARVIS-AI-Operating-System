"""
FastAPI Endpoints for Enterprise Multi-Tier Memory Engine.
Includes: CRUD, semantic vector search, ranking, compression, archival, GDPR erase, and statistics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.memory.compressor import memory_compressor
from app.memory.manager import memory_manager
from app.memory.maintenance import maintenance_engine
from app.memory.repository import MemoryRepository
from app.memory.schemas import (
    MemoryCategory,
    MemoryCompressionRequest,
    MemoryCreate,
    MemoryEntry,
    MemoryQuery,
    MemorySearchResult,
    MemoryStats,
    MemoryType,
    MemoryUpdate,
)
from app.models.user import User

router = APIRouter()


@router.post("", response_model=MemoryEntry, status_code=status.HTTP_201_CREATED, summary="Create Memory Record")
async def create_memory(
    memory_in: MemoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryEntry:
    """Stores a memory record in SQL metadata and ChromaDB vector store."""
    return await memory_manager.store(db=db, memory_in=memory_in, user_id=current_user.id)


@router.get("/{memory_id}", response_model=MemoryEntry, summary="Get Single Memory Record")
async def get_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryEntry:
    """Fetches single memory by ID."""
    repo = MemoryRepository(db)
    entry = await repo.get_memory(memory_id=memory_id, user_id=current_user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")
    return entry


@router.patch("/{memory_id}", response_model=MemoryEntry, summary="Update Memory Record")
async def update_memory(
    memory_id: str,
    update_in: MemoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryEntry:
    """Updates content, importance, tags, metadata, or type for a memory record."""
    updated = await memory_manager.update(db=db, memory_id=memory_id, update_in=update_in, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")
    return updated


@router.get("", response_model=List[MemoryEntry], summary="List Memory Records")
async def list_memories(
    categories: Optional[List[MemoryCategory]] = Query(default=None),
    memory_types: Optional[List[MemoryType]] = Query(default=None),
    conversation_id: Optional[str] = Query(default=None),
    project_id: Optional[str] = Query(default=None),
    agent_id: Optional[str] = Query(default=None),
    tags: Optional[List[str]] = Query(default=None),
    min_importance: float = Query(default=0.0, ge=0.0, le=1.0),
    include_archived: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[MemoryEntry]:
    """Lists memory records with flexible filtering."""
    repo = MemoryRepository(db)
    return await repo.list_active_memories(
        user_id=current_user.id,
        categories=categories,
        memory_types=memory_types,
        conversation_id=conversation_id,
        project_id=project_id,
        agent_id=agent_id,
        tags=tags,
        min_importance=min_importance,
        include_archived=include_archived,
        limit=limit
    )


@router.post("/query", response_model=List[MemorySearchResult], summary="Ranked Semantic Memory Search")
async def query_memories(
    query_in: MemoryQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[MemorySearchResult]:
    """
    Performs full semantic vector search (ChromaDB) and multi-factor ranking
    combining vector similarity, importance, recency, access frequency, and context.
    """
    return await memory_manager.retrieve(db=db, query=query_in, user_id=current_user.id)


@router.post("/compress", response_model=MemoryEntry, summary="Compress Conversation Turns")
async def compress_conversation_turns(
    req: MemoryCompressionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryEntry:
    """Summarizes conversation turns into a high-density long-term semantic memory record."""
    return await memory_compressor.compress_conversation(
        db=db,
        conversation_turns=req.conversation_turns,
        user_id=current_user.id,
        conversation_id=req.conversation_id,
        project_id=req.project_id,
        importance_score=req.importance_score
    )


@router.post("/archive/{memory_id}", response_model=MemoryEntry, summary="Archive Memory Record")
async def archive_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryEntry:
    """Soft-deletes a memory record by archiving it."""
    archived = await memory_manager.archive(db=db, memory_id=memory_id, user_id=current_user.id)
    if not archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")
    return archived


@router.post("/restore/{memory_id}", response_model=MemoryEntry, summary="Restore Archived Memory Record")
async def restore_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryEntry:
    """Restores an archived memory record."""
    restored = await memory_manager.restore(db=db, memory_id=memory_id, user_id=current_user.id)
    if not restored:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")
    return restored


@router.delete("/{memory_id}", summary="Delete Memory Record")
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hard-deletes a memory record from SQL and ChromaDB."""
    deleted = await memory_manager.delete(db=db, memory_id=memory_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory record '{memory_id}' not found.")
    return {"message": f"Memory '{memory_id}' deleted successfully."}


@router.delete("/conversation/{conv_id}", summary="Clear Conversation Memories")
async def clear_conversation_memories(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes all memories associated with a specific conversation ID."""
    count = await memory_manager.clear_conversation(db=db, conversation_id=conv_id, user_id=current_user.id)
    return {"message": f"Deleted {count} memories for conversation '{conv_id}'."}


@router.delete("/user/{user_id}", summary="GDPR Erase All User Memories")
async def erase_user_memories(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GDPR compliance: hard-deletes all memories belonging to specified user."""
    # Ensure standard users can only erase their own memories
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete other user memories.")
    sql_count, vector_count = await memory_manager.erase_user(db=db, user_id=user_id)
    return {"message": f"GDPR Erase complete. Purged {sql_count} database records and {vector_count} vector embeddings."}


@router.get("/stats/engine", response_model=MemoryStats, summary="Memory Engine Observability Statistics")
async def get_memory_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryStats:
    """Returns real-time memory engine telemetry, cache hit rates, and latency statistics."""
    user_filter = None if current_user.is_superuser else current_user.id
    return await memory_manager.get_stats(db=db, user_id=user_filter)


@router.post("/cleanup", summary="Purge Expired Memories")
async def purge_expired(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes garbage collection purging expired TTL memory records."""
    count = await maintenance_engine.cleanup_expired_memories(db)
    return {"message": f"Purged {count} expired memory records."}


@router.post("/train-dataset", summary="Ingest & Train Vector Memory Dataset Batch")
async def train_dataset(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Ingests a batch of JSON/Text documents into ChromaDB vector store, computes embeddings,
    and updates vector knowledge indices.
    """
    from app.memory.trainer import dataset_trainer
    items = payload.get("items") or payload.get("documents") or []
    category = payload.get("category", "LONG_TERM_EPISODIC")
    importance = float(payload.get("importance_score", 0.8))

    if not items and payload.get("content"):
        items = [{"content": payload["content"], "title": payload.get("title", "Ingested Document")}]

    res = await dataset_trainer.ingest_dataset_batch(items=items, category=category, importance_score=importance)
    return res


@router.post("/generate-fewshot", summary="Generate Synthetic Few-Shot Training Examples")
async def generate_fewshot(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Generates synthetic Question/Answer few-shot dataset pairs for AI agent prompt tuning."""
    from app.memory.trainer import dataset_trainer
    topic = payload.get("topic", "JARVIS System Architecture")
    count = int(payload.get("count", 5))

    res = await dataset_trainer.generate_synthetic_fewshot_dataset(topic=topic, sample_count=count)
    return res


@router.get("/export-fine-tune", summary="Export Formatted Fine-Tuning JSONL Dataset")
async def export_fine_tune(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Exports indexed vector memories and synthetic training pairs into OpenAI/Gemini JSONL format."""
    from app.memory.trainer import dataset_trainer
    res = await dataset_trainer.export_fine_tuning_jsonl(limit=limit)
    return res

