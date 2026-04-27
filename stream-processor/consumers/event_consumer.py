import logging
from datetime import datetime, timezone
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..utils.config import get_settings
from ..jobs.event_cleaner import clean_event
from .kafka_consumer import create_consumer

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def process_event(event_data: dict):
    cleaned = clean_event(event_data)
    
    db = SessionLocal()
    try:
        from backend.app.models.event import Event
        
        ts = cleaned.get("timestamp")
        if isinstance(ts, datetime):
            ts = ts.replace(tzinfo=timezone.utc)
        
        event = Event(
            id=uuid.uuid4(),
            app_id=cleaned.get("app_id"),
            event_type=cleaned.get("event_type"),
            user_id=cleaned.get("user_id"),
            session_id=cleaned.get("session_id"),
            properties=cleaned.get("properties", {}),
            timestamp=ts,
            processed_at=datetime.now(timezone.utc)
        )
        
        db.add(event)
        db.commit()
        logger.info(f"Stored event: {event.id}")
    
    except Exception as e:
        logger.error(f"Error storing event: {e}")
        db.rollback()
    finally:
        db.close()


def run_consumer():
    logger.info("Starting event consumer...")
    
    consumer = create_consumer(
        settings.kafka_topic_raw_events,
        settings.kafka_consumer_group
    )
    
    try:
        for message in consumer:
            try:
                process_event(message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()