from datetime import datetime, timezone
import pytz


def time_bucket(timestamp: datetime, interval_seconds: int) -> datetime:
    if timestamp.tzinfo is None:
        timestamp = pytz.utc.localize(timestamp)
    
    epoch = timestamp.timestamp()
    bucket = int(epoch // interval_seconds) * interval_seconds
    return datetime.fromtimestamp(bucket, tz=timezone.utc)


def bucket_by_interval(timestamp: datetime, interval: str) -> datetime:
    buckets = {
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800
    }
    seconds = buckets.get(interval, 3600)
    return time_bucket(timestamp, seconds)


def floor_to_hour(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.replace(minute=0, second=0, microsecond=0)


def floor_to_day(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)