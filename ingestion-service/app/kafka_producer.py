import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from kafka import KafkaProducer
from config import get_settings

settings = get_settings()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


producer = None


def get_producer() -> KafkaProducer:
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, cls=JSONEncoder).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            max_in_flight_requests_per_connection=1,
        )
    return producer


def produce_event(app_id: str, event_data: dict) -> bool:
    try:
        producer = get_producer()
        event_data["app_id"] = app_id
        event_data["received_at"] = datetime.now(timezone.utc).isoformat()
        
        future = producer.send(
            settings.kafka_topic_raw_events,
            key=app_id,
            value=event_data
        )
        future.get(timeout=10)
        return True
    except Exception as e:
        print(f"Failed to produce event: {e}")
        return False


def close_producer():
    global producer
    if producer:
        producer.close()
        producer = None