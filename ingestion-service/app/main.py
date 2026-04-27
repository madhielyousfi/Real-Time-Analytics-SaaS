import json
import uuid
from datetime import datetime, timezone
from typing import List, Callable, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(
    title="Ingestion Service",
    description="High-throughput event ingestion API",
    version="1.0.0"
)

event_handlers: List[Callable[[dict], bool]] = []


class EventPayload(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: dict = {}
    timestamp: Optional[datetime] = None


class BatchPayload(BaseModel):
    events: List[EventPayload]


def register_event_handler(handler: Callable[[dict], bool]):
    event_handlers.append(handler)


@app.post("/track")
async def track_event(
    event: EventPayload,
    x_api_key: str = Header(None),
    x_secret_key: str = Header(None)
):
    if x_api_key and x_secret_key:
        app_id = f"{x_api_key[:8]}_{x_secret_key[:8]}"
    else:
        app_id = "demo_app"
    
    event_data = event.model_dump()
    
    if not event_data.get("timestamp"):
        event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    event_data["app_id"] = app_id
    event_data["received_at"] = datetime.now(timezone.utc).isoformat()
    
    success = True
    for handler in event_handlers:
        if not handler(event_data):
            success = False
    
    if not event_handlers:
        print(f"Event received: {event_data['event_type']} for app {app_id}")
    
    return {"status": "accepted", "event_type": event.event_type}


@app.post("/track/batch")
async def track_batch(
    payload: BatchPayload,
    x_api_key: str = Header(None),
    x_secret_key: str = Header(None)
):
    if x_api_key and x_secret_key:
        app_id = f"{x_api_key[:8]}_{x_secret_key[:8]}"
    else:
        app_id = "demo_app"
    
    results = []
    for event in payload.events:
        event_data = event.model_dump()
        
        if not event_data.get("timestamp"):
            event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        event_data["app_id"] = app_id
        event_data["received_at"] = datetime.now(timezone.utc).isoformat()
        
        success = True
        for handler in event_handlers:
            if not handler(event_data):
                success = False
        
        results.append({"success": True})
        print(f"Event received: {event_data['event_type']}")
    
    return {
        "total": len(payload.events),
        "accepted": len(payload.events)
    }


@app.get("/health")
def health():
    return {"status": "healthy"}