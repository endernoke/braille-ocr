from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    ocr_model_path: str = "/app/models/ocr_model.pth"
    classifier_model_path: str = "/app/models/classifier_model.pth"

    device: str = "cuda"  # or "cpu"
    
    upload_dir: str = "/app/uploads"
    result_dir: str = "/app/results"
    
    task_result_ttl: int = 3600  # 1 hour


settings = Settings()
