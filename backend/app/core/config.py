"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CodeBridge AI"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "super-secret-key-change-in-production-32bytes!"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days

    # Database
    postgres_user: str = "snaplogic_user"
    postgres_password: str = "snaplogic_pass"
    postgres_db: str = "snaplogic_platform"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str = "postgresql+asyncpg://snaplogic_user:snaplogic_pass@localhost:5432/snaplogic_platform"

    # Security & Rate Limiting
    jwt_secret_key: str = "super-secret-key-change-in-production-32bytes!"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days
    refresh_token_expire_days: int = 7
    session_timeout_minutes: int = 60
    otp_expire_minutes: int = 10
    otp_length: int = 6
    rate_limit_per_minute: int = 100
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://snaplogic-python-platform.onrender.com,*"

    # AI Service
    openai_api_key: str = ""
    ai_model: str = "gpt-4o"
    ai_max_tokens: int = 4096
    ai_temperature: float = 0.1

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@codebridge.ai"
    smtp_tls: bool = True

    snaplogic_base_url: str = "https://elastic.snaplogic.com"
    snaplogic_username: str = ""
    snaplogic_password: str = ""
    snaplogic_org: str = ""
    snaplogic_retry_attempts: int = 3
    snaplogic_retry_delay: int = 5

    openai_api_key: str = ""
    ai_model: str = "gpt-4o"
    ai_max_tokens: int = 8192
    ai_temperature: float = 0.1

    upload_dir: str = "uploads"
    snaplogic_json_dir: str = "snaplogic_json"
    generated_dir: str = "generated"
    completed_dir: str = "completed"
    failed_dir: str = "failed"
    logs_dir: str = "logs"
    reports_dir: str = "reports"
    temp_dir: str = "temp"
    downloads_dir: str = "downloads"

    airflow_base_url: str = "http://localhost:8080"
    airflow_username: str = "admin"
    airflow_password: str = "admin"

    dd_api_key: str = ""
    dd_app_key: str = ""
    dd_site: str = "datadoghq.com"
    dd_service: str = "snaplogic-platform"
    dd_env: str = "development"
    dd_version: str = "1.0.0"
    dd_logs_injection: bool = True
    dd_trace_enabled: bool = True

    redis_url: str = "redis://localhost:6379/0"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
