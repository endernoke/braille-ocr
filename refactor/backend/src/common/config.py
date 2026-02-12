from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    ocr_model_path: str = "/app/models/ocr_model.pth"
    classifier_model_path: str = "/app/models/classifier_model.pth"

    device: str = "cpu"  # or "cpu"
    
    upload_dir: str = "/app/uploads"
    result_dir: str = "/app/results"
    
    task_result_ttl: int = 3600  # 1 hour


class Settings2:
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
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

    device: str = "cpu"  # or "cpu"
    
    upload_dir: str = "/app/uploads"
    result_dir: str = "/app/results"
    
    task_result_ttl: int = 3600  # 1 hour



settings = Settings2()
