import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_id = Column(UUID(as_uuid=True), ForeignKey("apps.id"), nullable=False, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    user_id = Column(String(64), nullable=True, index=True)
    session_id = Column(String(64), nullable=True, index=True)
    properties = Column(JSONB, default=dict)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index("idx_events_app_time", "app_id", "timestamp"),
        Index("idx_events_app_type_time", "app_id", "event_type", "timestamp"),
    )


class EventOut:
    pass