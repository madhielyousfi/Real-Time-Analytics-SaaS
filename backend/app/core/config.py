from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./analytics.db"
    
    jwt_secret: str = "changeme-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_raw_events: str = "raw_events"
    kafka_topic_processed_events: str = "processed_events"
    
    redis_url: str = "redis://localhost:6379"
    
    cors_origins: str = "http://localhost:3000"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()