import json
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Any


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def to_json(data: Any) -> str:
    return json.dumps(data, cls=EnhancedJSONEncoder)


def from_json(json_str: str) -> Any:
    return json.loads(json_str)


def serialize_event(event_dict: dict) -> dict:
    result = event_dict.copy()
    if "timestamp" in result and isinstance(result["timestamp"], datetime):
        result["timestamp"] = result["timestamp"].isoformat()
    return result