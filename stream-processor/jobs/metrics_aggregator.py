from datetime import datetime, timezone
from typing import Dict, Any, List
from collections import defaultdict
from .time_bucket import bucket_by_interval


AGGREGATION_KEYS = ["event_type", "user_id", "session_id"]


def aggregate_event_counts(events: List[Dict[str, Any]], interval: str = "hour") -> Dict[str, Any]:
    buckets = defaultdict(lambda: defaultdict(int))
    
    for event in events:
        ts = event.get("timestamp")
        if isinstance(ts, str):
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            ts = datetime.fromisoformat(ts)
        
        bucket_ts = bucket_by_interval(ts, interval)
        event_type = event.get("event_type", "unknown")
        
        buckets[bucket_ts][event_type] += 1
        buckets[bucket_ts]["_total"] += 1
    
    result = {}
    for bucket_ts, counts in buckets.items():
        result[bucket_ts.isoformat()] = dict(counts)
    
    return result


def aggregate_by_property(events: List[Dict[str, Any]], property_name: str) -> Dict[str, int]:
    counts = defaultdict(int)
    
    for event in events:
        props = event.get("properties", {})
        value = props.get(property_name, "unknown")
        if isinstance(value, (str, int, float, bool)):
            counts[str(value)] += 1
    
    return dict(counts)


def aggregate_user_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    metrics = {
        "total_events": len(events),
        "unique_users": len(set(e.get("user_id") for e in events if e.get("user_id"))),
        "unique_sessions": len(set(e.get("session_id") for e in events if e.get("session_id"))),
        "event_types": defaultdict(int)
    }
    
    for event in events:
        event_type = event.get("event_type", "unknown")
        metrics["event_types"][event_type] += 1
    
    metrics["event_types"] = dict(metrics["event_types"])
    return metrics