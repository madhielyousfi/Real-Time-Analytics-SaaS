import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from collections import defaultdict


SESSION_TIMEOUT_MINUTES = 30


def create_session_id(user_id: str | None, session_id: str | None, app_id: str) -> str:
    if session_id:
        return f"{app_id}:{session_id}"
    if user_id:
        return f"{app_id}:{user_id}:{uuid.uuid4().hex[:8]}"
    return f"{app_id}:anonymous:{uuid.uuid4().hex[:8]}"


def detect_sessions(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not events:
        return []
    
    events_by_user = defaultdict(list)
    for event in events:
        user_id = event.get("user_id") or "anonymous"
        events_by_user[user_id].append(event)
    
    sessions = []
    current_session = None
    last_event_time = None
    
    for events in events_by_user.values():
        sorted_events = sorted(events, key=lambda e: e.get("timestamp"))
        
        for event in sorted_events:
            event_time = event.get("timestamp")
            if isinstance(event_time, str):
                if event_time.endswith("Z"):
                    event_time = event_time.replace("Z", "+00:00")
                event_time = datetime.fromisoformat(event_time)
            
            if current_session is None:
                current_session = {
                    "session_id": create_session_id(
                        event.get("user_id"),
                        event.get("session_id"),
                        event.get("app_id")
                    ),
                    "app_id": event.get("app_id"),
                    "user_id": event.get("user_id"),
                    "start_time": event_time,
                    "events": []
                }
            
            time_diff = (event_time - last_event_time).total_seconds() if last_event_time else SESSION_TIMEOUT_MINUTES * 60 + 1
            
            if time_diff > SESSION_TIMEOUT_MINUTES * 60:
                if current_session["events"]:
                    sessions.append(current_session)
                current_session = {
                    "session_id": create_session_id(
                        event.get("user_id"),
                        event.get("session_id"),
                        event.get("app_id")
                    ),
                    "app_id": event.get("app_id"),
                    "user_id": event.get("user_id"),
                    "start_time": event_time,
                    "events": []
                }
            
            current_session["events"].append(event)
            last_event_time = event_time
    
    if current_session and current_session["events"]:
        sessions.append(current_session)
    
    for session in sessions:
        end_time = session["events"][-1].get("timestamp")
        if isinstance(end_time, str):
            if end_time.endswith("Z"):
                end_time = end_time.replace("Z", "+00:00")
            end_time = datetime.fromisoformat(end_time)
        duration = (end_time - session["start_time"]).total_seconds()
        session["end_time"] = end_time
        session["duration_seconds"] = int(duration)
        del session["events"]
    
    return sessions