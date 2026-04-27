import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .validators import EventPayload
from .kafka_producer import produce_event

router = APIRouter(prefix="/ingest", tags=["ingestion"])

_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine("postgresql://analytics:changeme@postgres:5432/analytics")
        _SessionLocal = sessionmaker(bind=_engine)
    return _engine, _SessionLocal


def verify_app_key(
    x_api_key: str = Header(None),
    x_secret_key: str = Header(None)
) -> str:
    if not x_api_key or not x_secret_key:
        raise HTTPException(
            status_code=401,
            detail="API key and secret key required"
        )
    
    from backend.app.models.app import App
    
    _, SessionLocal = get_engine()
    db = SessionLocal()
    
    try:
        app = db.query(App).filter(App.api_key == x_api_key).first()
        if not app or not secrets.compare_digest(app.secret_key, x_secret_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid API credentials"
            )
        return str(app.id)
    finally:
        db.close()


@router.post("/event")
def ingest_event(
    event: EventPayload,
    app_id: str = Depends(verify_app_key)
):
    event_data = event.model_dump()
    
    if not event_data.get("timestamp"):
        from datetime import datetime, timezone
        event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    success = produce_event(app_id, event_data)
    
    if not success:
        raise HTTPException(
            status_code=503,
            detail="Failed to process event"
        )
    
    return {"status": "accepted"}


@router.post("/batch")
def ingest_batch(
    events: list[EventPayload],
    app_id: str = Depends(verify_app_key)
):
    results = []
    
    for event in events:
        event_data = event.model_dump()
        if not event_data.get("timestamp"):
            from datetime import datetime, timezone
            event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        success = produce_event(app_id, event_data)
        results.append({"success": success})
    
    failed = sum(1 for r in results if not r["success"])
    
    return {
        "total": len(events),
        "failed": failed,
        "accepted": len(events) - failed
    }