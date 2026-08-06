"""
SQLAlchemy ORM Database Model for Workflow Persistence.
"""

from datetime import datetime
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from app.db.session import Base


class WorkflowInstanceModel(Base):
    """Stores persisted workflow definitions, active instances, variable state, and execution history."""

    __tablename__ = "workflow_instances"

    id = Column(String(36), primary_key=True, index=True)
    definition_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="RUNNING")
    current_node_id = Column(String(50), nullable=True)
    variables = Column(JSON, nullable=False, default=dict)
    execution_history = Column(JSON, nullable=False, default=list)
    pending_approval_id = Column(String(50), nullable=True)
    is_scheduled = Column(Boolean, default=False)
    cron_schedule = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
