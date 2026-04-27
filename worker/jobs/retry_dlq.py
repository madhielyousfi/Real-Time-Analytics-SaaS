import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def retry_failed_events():
    return {"retry_count": 0, "message": "No failed events to retry"}


def get_dead_letter_queue():
    return {"events": []}


if __name__ == "__main__":
    retry_failed_events()