from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from ..core.database import get_db
from ..core.security import get_api_key
from ..models.event import Event
from ..models.session import Session as SessionModel
from ..models.app import App
from ...shared.schemas.metrics_schema import (
    MetricsQuery, MetricsResult, TimeSeriesPoint,
    SummaryStats
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=SummaryStats)
def get_summary_stats(
    app_id: str,
    start_time: datetime = Query(default=None),
    end_time: datetime = Query(default=None),
    db: Session = Depends(get_db),
    app: App = Depends(get_api_key)
):
    if not start_time:
        start_time = datetime.now() - timedelta(days=7)
    if not end_time:
        end_time = datetime.now()
    
    query = db.query(Event).filter(
        Event.app_id == app.id,
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    )
    
    total_events = query.count()
    unique_users = query.filter(Event.user_id.isnot(None)).distinct(Event.user_id).count()
    unique_sessions = query.filter(Event.session_id.isnot(None)).distinct(Event.session_id).count()
    
    avg_duration = db.query(func.avg(SessionModel.duration_seconds)).filter(
        SessionModel.app_id == app.id,
        SessionModel.start_time >= start_time,
        SessionModel.start_time <= end_time
    ).scalar() or 0
    
    return SummaryStats(
        total_events=total_events,
        unique_users=unique_users,
        unique_sessions=unique_sessions,
        avg_session_duration_seconds=float(avg_duration)
    )


@router.post("/timeseries", response_model=MetricsResult)
def get_timeseries_metrics(
    query: MetricsQuery,
    db: Session = Depends(get_db),
    app: App = Depends(get_api_key)
):
    interval_seconds = {
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800
    }.get(query.interval, 3600)
    
    base_query = db.query(Event).filter(
        Event.app_id == app.id,
        Event.timestamp >= query.start_time,
        Event.timestamp <= query.end_time
    )
    
    if query.event_type:
        base_query = base_query.filter(Event.event_type == query.event_type)
    
    events = base_query.all()
    
    from collections import defaultdict
    buckets = defaultdict(float)
    
    for event in events:
        ts = event.timestamp
        bucket_time = ts.replace(minute=0, second=0, microsecond=0)
        if interval_seconds >= 86400:
            bucket_time = bucket_time.replace(hour=0)
        
        buckets[bucket_time] += 1
    
    data = [
        TimeSeriesPoint(timestamp=ts, value=value)
        for ts, value in sorted(buckets.items())
    ]
    
    total = sum(point.value for point in data)
    
    return MetricsResult(
        metric_name=query.metric_name,
        data=data,
        total=total
    )