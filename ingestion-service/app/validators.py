from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class EventPayload(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=128)
    user_id: Optional[str] = Field(None, max_length=64)
    session_id: Optional[str] = Field(None, max_length=64)
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None
    
    @validator("properties", pre=True)
    def validate_properties(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("properties must be a dictionary")
        return v