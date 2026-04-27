from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..core.security import get_api_key
from ..models.event import Event
from ..models.app import App
from ...shared.schemas.metrics_schema import FunnelQuery, FunnelResult, FunnelStep

router = APIRouter(prefix="/funnels", tags=["funnels"])


@router.post("/query", response_model=FunnelResult)
def query_funnel(
    query: FunnelQuery,
    db: Session = Depends(get_db),
    app: App = Depends(get_api_key)
):
    if len(query.steps) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 steps required"
        )
    
    window_delta = timedelta(seconds=query.window_seconds)
    
    events = db.query(Event).filter(
        Event.app_id == app.id,
        Event.timestamp >= query.start_time,
        Event.timestamp <= query.end_time,
        Event.event_type.in_(query.steps)
    ).order_by(Event.timestamp).all()
    
    step_users = {step: set() for step in query.steps}
    
    for event in events:
        if event.user_id:
            step_users[event.event_type].add(event.user_id)
    
    steps_result = []
    previous_count = 0
    
    for i, step in enumerate(query.steps):
        count = len(step_users[step])
        
        if i == 0:
            conversion_rate = 100.0 if count > 0 else 0.0
        else:
            conversion_rate = (count / previous_count * 100) if previous_count > 0 else 0.0
        
        steps_result.append(FunnelStep(
            step_name=step,
            count=count,
            conversion_rate=conversion_rate
        ))
        
        previous_count = count
    
    overall = (steps_result[-1].count / steps_result[0].count * 100) if steps_result[0].count > 0 else 0.0
    
    return FunnelResult(
        steps=steps_result,
        overall_conversion=overall
    )