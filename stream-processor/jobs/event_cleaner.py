import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any
import pytz


def sanitize_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {}
    for key, value in properties.items():
        if isinstance(value, (str, int, float, bool, list, dict)):
            sanitized[str(key)] = value
    return sanitized


def generate_event_id(app_id: str, timestamp: datetime, user_id: str | None, session_id: str | None, event_type: str) -> str:
    data = f"{app_id}:{timestamp.isoformat()}:{user_id or ''}:{session_id or ''}:{event_type}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def clean_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = event_data.copy()
    
    if "timestamp" in cleaned:
        ts = cleaned["timestamp"]
        if isinstance(ts, str):
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            cleaned["timestamp"] = datetime.fromisoformat(ts)
    
    if "received_at" in cleaned:
        del cleaned["received_at"]
    
    cleaned["properties"] = sanitize_properties(cleaned.get("properties", {}))
    
    if not cleaned.get("processed_at"):
        cleaned["processed_at"] = datetime.now(timezone.utc).isoformat()
    
    return cleaned


def remove_pii(event_data: Dict[str, Any]) -> Dict[str, Any]:
    pii_fields = ["password", "token", "secret", "credit_card", "ssn"]
    cleaned = event_data.copy()
    
    if "properties" in cleaned:
        properties = cleaned["properties"]
        for field in pii_fields:
            if field in properties:
                del properties[field]
    
    return cleaned