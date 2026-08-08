"""
ChromaDB Vector Store — Persistent Vector Database for the Memory Engine.
Implements the vector storage layer with:
- Persistent local storage
- Named collections / namespace isolation
- Similarity search with metadata filtering
- CRUD: add, update, delete, bulk insert
- Health check
- Designed for drop-in replacement with pgvector / Qdrant / Pinecone / Milvus
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from app.config import settings
from app.core.logging import logger


# ─────────────────────────────────────────────────
# Result Types
# ─────────────────────────────────────────────────

class VectorSearchResult:
    """Single result from a ChromaDB similarity search."""

    def __init__(self, doc_id: str, distance: float, metadata: Dict[str, Any], document: str) -> None:
        self.doc_id = doc_id
        self.distance = distance
        self.similarity = max(0.0, min(1.0, 1.0 - distance))  # Convert L2/cosine distance to similarity
        self.metadata = metadata
        self.document = document


# ─────────────────────────────────────────────────
# ChromaDB Vector Store
# ─────────────────────────────────────────────────

class ChromaVectorStore:
    """
    Persistent ChromaDB vector store.
    Thread-safe with asyncio executor delegation for synchronous ChromaDB calls.
    Supports namespaced collections, full CRUD, and similarity search.
    """

    def __init__(self, persist_path: Optional[str] = None) -> None:
        self._persist_path = persist_path or settings.CHROMA_PERSIST_PATH
        self._client = None
        self._collections: Dict[str, Any] = {}
        self._initialized = False
        self._lock = asyncio.Lock()

    def _get_or_create_client(self):
        """Creates a ChromaDB persistent client (singleton per store)."""
        if self._client is not None:
            return self._client
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self._client = chromadb.PersistentClient(
                path=self._persist_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("ChromaDB client initialized", persist_path=self._persist_path)
            return self._client
        except ImportError:
            logger.error("chromadb package not installed — pip install chromadb")
            return None
        except Exception as e:
            logger.error("ChromaDB client initialization failed", error=str(e))
            return None

    def _get_or_create_collection_sync(self, collection_name: str):
        """Synchronously gets or creates a ChromaDB collection."""
        client = self._get_or_create_client()
        if client is None:
            return None
        if collection_name in self._collections:
            return self._collections[collection_name]
        try:
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            self._collections[collection_name] = collection
            return collection
        except Exception as e:
            logger.error("ChromaDB get_or_create_collection failed", collection=collection_name, error=str(e))
            return None

    async def _run_sync(self, func, *args, **kwargs):
        """Runs a synchronous ChromaDB call in the asyncio thread pool executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def initialize(self) -> bool:
        """Initializes ChromaDB client and default collection."""
        if self._initialized:
            return True
        async with self._lock:
            client = await self._run_sync(self._get_or_create_client)
            if client is None:
                return False
            collection = await self._run_sync(
                self._get_or_create_collection_sync,
                settings.CHROMA_COLLECTION_NAME
            )
            if collection is None:
                return False
            self._initialized = True
            logger.info("ChromaVectorStore initialized", collection=settings.CHROMA_COLLECTION_NAME)
            return True

    async def health_check(self) -> bool:
        """Verifies ChromaDB is available and responsive."""
        try:
            client = await self._run_sync(self._get_or_create_client)
            if client is None:
                return False
            # Heartbeat check
            await self._run_sync(client.heartbeat)
            return True
        except Exception as e:
            logger.warning("ChromaDB health check failed", error=str(e))
            return False

    async def add(
        self,
        doc_id: str,
        vector: List[float],
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """Adds a single document + vector to ChromaDB."""
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return False
        try:
            safe_meta = self._sanitize_metadata(metadata or {})
            await self._run_sync(
                collection.add,
                ids=[doc_id],
                embeddings=[vector],
                documents=[document],
                metadatas=[safe_meta]
            )
            return True
        except Exception as e:
            logger.error("ChromaDB add failed", doc_id=doc_id, error=str(e))
            return False

    async def add_batch(
        self,
        doc_ids: List[str],
        vectors: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """Bulk-inserts multiple documents into ChromaDB."""
        if not doc_ids:
            return True
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return False
        try:
            safe_metas = [self._sanitize_metadata(m) for m in (metadatas or [{}] * len(doc_ids))]
            # Process in batches of MEMORY_MAX_BATCH_SIZE
            batch_size = settings.MEMORY_MAX_BATCH_SIZE
            for i in range(0, len(doc_ids), batch_size):
                batch_end = min(i + batch_size, len(doc_ids))
                await self._run_sync(
                    collection.add,
                    ids=doc_ids[i:batch_end],
                    embeddings=vectors[i:batch_end],
                    documents=documents[i:batch_end],
                    metadatas=safe_metas[i:batch_end]
                )
            return True
        except Exception as e:
            logger.error("ChromaDB batch add failed", count=len(doc_ids), error=str(e))
            return False

    async def update(
        self,
        doc_id: str,
        vector: Optional[List[float]] = None,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """Updates an existing document's vector and/or metadata."""
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return False
        try:
            kwargs: Dict[str, Any] = {"ids": [doc_id]}
            if vector is not None:
                kwargs["embeddings"] = [vector]
            if document is not None:
                kwargs["documents"] = [document]
            if metadata is not None:
                kwargs["metadatas"] = [self._sanitize_metadata(metadata)]
            await self._run_sync(collection.update, **kwargs)
            return True
        except Exception as e:
            logger.error("ChromaDB update failed", doc_id=doc_id, error=str(e))
            return False

    async def delete(
        self,
        doc_id: str,
        collection_name: Optional[str] = None
    ) -> bool:
        """Deletes a document from ChromaDB by ID."""
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return False
        try:
            await self._run_sync(collection.delete, ids=[doc_id])
            return True
        except Exception as e:
            logger.error("ChromaDB delete failed", doc_id=doc_id, error=str(e))
            return False

    async def delete_batch(
        self,
        doc_ids: List[str],
        collection_name: Optional[str] = None
    ) -> bool:
        """Deletes multiple documents from ChromaDB."""
        if not doc_ids:
            return True
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return False
        try:
            await self._run_sync(collection.delete, ids=doc_ids)
            return True
        except Exception as e:
            logger.error("ChromaDB batch delete failed", count=len(doc_ids), error=str(e))
            return False

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """
        Searches ChromaDB for the top-k most similar vectors.
        Returns VectorSearchResult list sorted by similarity (descending).
        """
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return []

        start = time.time()
        try:
            query_kwargs: Dict[str, Any] = {
                "query_embeddings": [query_vector],
                "n_results": min(top_k, await self._run_sync(collection.count) or 1),
                "include": ["documents", "metadatas", "distances"]
            }
            if where:
                query_kwargs["where"] = where

            results = await self._run_sync(collection.query, **query_kwargs)

            elapsed_ms = (time.time() - start) * 1000.0
            logger.debug("ChromaDB search completed", top_k=top_k, latency_ms=round(elapsed_ms, 1))

            search_results: List[VectorSearchResult] = []
            if results and results.get("ids") and results["ids"][0]:
                ids = results["ids"][0]
                distances = results["distances"][0]
                metadatas = results["metadatas"][0]
                documents = results["documents"][0]

                for doc_id, distance, meta, doc in zip(ids, distances, metadatas, documents):
                    search_results.append(
                        VectorSearchResult(
                            doc_id=doc_id,
                            distance=float(distance),
                            metadata=meta or {},
                            document=doc or ""
                        )
                    )
            return search_results
        except Exception as e:
            logger.error("ChromaDB search failed", error=str(e))
            return []

    async def get_collection_count(self, collection_name: Optional[str] = None) -> int:
        """Returns the number of documents in a collection."""
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return 0
        try:
            return await self._run_sync(collection.count)
        except Exception:
            return 0

    async def delete_user_vectors(self, user_id: str, collection_name: Optional[str] = None) -> int:
        """Deletes all vectors belonging to a user (GDPR erase). Returns count deleted."""
        cname = collection_name or settings.CHROMA_COLLECTION_NAME
        collection = await self._run_sync(self._get_or_create_collection_sync, cname)
        if collection is None:
            return 0
        try:
            results = await self._run_sync(
                collection.get,
                where={"user_id": user_id},
                include=[]
            )
            ids = results.get("ids", [])
            if ids:
                await self._run_sync(collection.delete, ids=ids)
            return len(ids)
        except Exception as e:
            logger.error("ChromaDB user vector erase failed", user_id=user_id, error=str(e))
            return 0

    async def seed_from_dataset(self, dataset_path: str) -> int:
        """
        Seeds ChromaDB collection from a JSON dataset file if available.
        Returns total number of items inserted.
        """
        import os
        import json
        if not os.path.exists(dataset_path):
            logger.info("Dataset file not found for vector store seeding", path=dataset_path)
            return 0

        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list) or not data:
                return 0

            doc_ids = []
            vectors = []
            documents = []
            metadatas = []

            for item in data:
                doc_id = item.get("id") or str(uuid.uuid4())
                content = item.get("content") or item.get("document") or ""
                vector = item.get("vector") or item.get("embedding") or []
                if not content or not vector:
                    continue

                meta = item.get("metadata", {})
                if "memory_type" in item and "memory_type" not in meta:
                    meta["memory_type"] = item["memory_type"]

                doc_ids.append(doc_id)
                vectors.append(vector)
                documents.append(content)
                metadatas.append(meta)

            if doc_ids:
                success = await self.add_batch(
                    doc_ids=doc_ids,
                    vectors=vectors,
                    documents=documents,
                    metadatas=metadatas
                )
                if success:
                    logger.info("ChromaVectorStore seeded successfully from dataset", path=dataset_path, count=len(doc_ids))
                    return len(doc_ids)

            return 0
        except Exception as e:
            logger.error("Failed to seed ChromaVectorStore from dataset", path=dataset_path, error=str(e))
            return 0

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        ChromaDB only accepts str, int, float, bool metadata values.
        Converts lists to JSON strings and removes None values.
        """
        import json
        sanitized: Dict[str, Any] = {}
        for key, value in metadata.items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                sanitized[key] = json.dumps(value)
            else:
                sanitized[key] = str(value)
        return sanitized


# Module-level singleton
chroma_store = ChromaVectorStore()

