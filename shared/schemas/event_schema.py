from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EventIn(BaseModel):
    app_id: str
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None


class EventOut(BaseModel):
    id: str
    app_id: str
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    properties: Dict[str, Any]
    timestamp: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventFilter(BaseModel):
    app_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = 0