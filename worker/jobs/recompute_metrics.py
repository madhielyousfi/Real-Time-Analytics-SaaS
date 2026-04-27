import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def recompute_metrics(app_id: str, start_time: datetime, end_time: datetime):
    db = SessionLocal()
    
    try:
        from backend.app.models.event import Event
        
        events = db.query(Event).filter(
            Event.app_id == app_id,
            Event.timestamp >= start_time,
            Event.timestamp <= end_time
        ).all()
        
        event_counts = {}
        user_counts = set()
        session_counts = set()
        
        for event in events:
            event_type = event.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            if event.user_id:
                user_counts.add(event.user_id)
            if event.session_id:
                session_counts.add(event.session_id)
        
        metrics = {
            "app_id": app_id,
            "period_start": start_time.isoformat(),
            "period_end": end_time.isoformat(),
            "total_events": len(events),
            "unique_users": len(user_counts),
            "unique_sessions": len(session_counts),
            "event_counts": event_counts,
            "computed_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Recomputed metrics for {app_id}: {metrics['total_events']} events")
        return metrics
    
    finally:
        db.close()


def recompute_all_metrics():
    db = SessionLocal()
    
    try:
        from backend.app.models.app import App
        
        apps = db.query(App).all()
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=1)
        
        results = []
        for app in apps:
            metrics = recompute_metrics(str(app.id), start_time, end_time)
            results.append(metrics)
        
        return results
    
    finally:
        db.close()


if __name__ == "__main__":
    recompute_all_metrics()