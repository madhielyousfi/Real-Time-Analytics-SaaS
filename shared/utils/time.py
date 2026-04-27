from datetime import datetime, timezone
from typing import Optional


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_iso_string(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.isoformat()


def parse_iso(dt_str: str) -> datetime:
    if dt_str.endswith("Z"):
        dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def start_of_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def time_bucket(timestamp: datetime, interval_seconds: int) -> datetime:
    epoch = timestamp.timestamp()
    bucket = int(epoch // interval_seconds) * interval_seconds
    return datetime.fromtimestamp(bucket, tz=timestamp.tzinfo)