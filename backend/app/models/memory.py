"""
SQLAlchemy ORM Model for Memory Records Metadata.
Stores full memory context including type, conversation, project, agent, tags, source, and archival status.
"""

from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from app.db.session import Base


class MemoryRecordModel(Base):
    """Memory metadata database ORM entity with full enterprise context fields."""
    __tablename__ = "memory_records"

    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Ownership & Context
    user_id = Column(String, nullable=True, index=True)
    conversation_id = Column(String, nullable=True, index=True)
    project_id = Column(String, nullable=True, index=True)
    agent_id = Column(String, nullable=True)

    # Classification
    category = Column(String, nullable=False, index=True)
    memory_type = Column(String, nullable=False, default="GENERAL", index=True)
    source = Column(String, nullable=True)

    # Content
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Vector Reference (ChromaDB doc ID)
    vector_id = Column(String, nullable=True, index=True)

    # Scoring & Usage
    importance_score = Column(Float, nullable=False, default=0.5)
    access_count = Column(Integer, nullable=False, default=0)
    recall_count = Column(Integer, nullable=False, default=0)

    # Metadata
    tags_json = Column(Text, nullable=False, default="[]")
    metadata_json = Column(Text, nullable=False, default="{}")

    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)

    # Archival / GDPR
    archived = Column(Boolean, nullable=False, default=False, index=True)
    archived_at = Column(DateTime, nullable=True)
