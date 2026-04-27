from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MetricsQuery(BaseModel):
    app_id: str
    metric_name: str
    start_time: datetime
    end_time: datetime
    interval: str = "hour"
    filters: Dict[str, Any] = Field(default_factory=dict)


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float


class MetricsResult(BaseModel):
    metric_name: str
    data: List[TimeSeriesPoint]
    total: float


class FunnelQuery(BaseModel):
    app_id: str
    steps: List[str]
    start_time: datetime
    end_time: datetime
    window_seconds: int = 86400


class FunnelStep(BaseModel):
    step_name: str
    count: int
    conversion_rate: float


class FunnelResult(BaseModel):
    steps: List[FunnelStep]
    overall_conversion: float


class EventCount(BaseModel):
    count: int
    timestamp: datetime


class SummaryStats(BaseModel):
    total_events: int
    unique_users: int
    unique_sessions: int
    avg_session_duration_seconds: float