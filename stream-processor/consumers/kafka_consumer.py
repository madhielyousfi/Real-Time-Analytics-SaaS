import json
import logging
from typing import Callable
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from ..utils.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(
        self,
        topic: str,
        group_id: str,
        message_handler: Callable[[dict], None]
    ):
        self.topic = topic
        self.group_id = group_id
        self.message_handler = message_handler
        self.consumer = None
        self.running = False
    
    def start(self):
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            auto_commit_interval_ms=5000
        )
        
        self.running = True
        logger.info(f"Starting consumer for topic {self.topic}")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    self.message_handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info(f"Consumer stopped for topic {self.topic}")


def create_consumer(topic: str, group_id: str):
    return KafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True
    )