from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://analytics:changeme@localhost:5432/analytics"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_raw_events: str = "raw_events"
    kafka_topic_processed_events: str = "processed_events"
    kafka_consumer_group: str = "stream-processor"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()