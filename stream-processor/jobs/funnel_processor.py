from datetime import datetime, timezone
from typing import List, Dict, Any
from collections import defaultdict


def process_funnel_events(events: List[Dict[str, Any]], steps: List[str]) -> Dict[str, Any]:
    if len(steps) < 2:
        return {"error": "At least 2 steps required"}
    
    user_sequences = defaultdict(list)
    
    for event in events:
        user_id = event.get("user_id")
        if not user_id:
            continue
        
        ts = event.get("timestamp")
        if isinstance(ts, str):
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            ts = datetime.fromisoformat(ts)
        
        user_sequences[user_id].append({
            "step": event.get("event_type"),
            "timestamp": ts
        })
    
    funnel_results = []
    
    for user_id, sequence in user_sequences.items():
        sorted_events = sorted(sequence, key=lambda e: e["timestamp"])
        steps_completed = set()
        
        for event in sorted_events:
            if event["step"] in steps:
                steps_completed.add(event["step"])
        
        funnel_results.append({
            "user_id": user_id,
            "completed_steps": len(steps_completed),
            "steps": list(steps_completed)
        })
    
    step_counts = {step: 0 for step in steps}
    
    for result in funnel_results:
        completed = result["completed_steps"]
        step_counts[steps[min(completed, len(steps) - 1)]] += 1
    
    return {
        "total_users": len(funnel_results),
        "step_counts": step_counts,
        "results": funnel_results[:100]
    }