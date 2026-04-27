from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..core.database import get_db
from ..core.security import get_api_key
from ..models.event import Event
from ...shared.schemas.event_schema import EventOut, EventFilter

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/query", response_model=List[EventOut])
def query_events(
    filter: EventFilter,
    db: Session = Depends(get_db),
    app: App = Depends(get_api_key)
):
    query = db.query(Event).filter(Event.app_id == app.id)
    
    if filter.start_time:
        query = query.filter(Event.timestamp >= filter.start_time)
    if filter.end_time:
        query = query.filter(Event.timestamp <= filter.end_time)
    if filter.event_type:
        query = query.filter(Event.event_type == filter.event_type)
    if filter.user_id:
        query = query.filter(Event.user_id == filter.user_id)
    if filter.session_id:
        query = query.filter(Event.session_id == filter.session_id)
    
    query = query.order_by(desc(Event.timestamp))
    
    events = query.offset(filter.offset).limit(filter.limit).all()
    
    return events


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    app: App = Depends(get_api_key)
):
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.app_id == app.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event