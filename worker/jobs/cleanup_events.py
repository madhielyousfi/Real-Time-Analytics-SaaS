import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def cleanup_events(days_old: int = 90):
    db = SessionLocal()
    
    try:
        from backend.app.models.event import Event
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        deleted = db.query(Event).filter(
            Event.timestamp < cutoff
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted} events older than {days_old} days")
        return {"deleted": deleted}
    
    finally:
        db.close()


def cleanup_sessions(days_old: int = 90):
    db = SessionLocal()
    
    try:
        from backend.app.models.session import Session
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        deleted = db.query(Session).filter(
            Session.end_time < cutoff
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted} sessions older than {days_old} days")
        return {"deleted": deleted}
    
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_events()
    cleanup_sessions()