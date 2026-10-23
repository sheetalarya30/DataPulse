import os
import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "DataPulse"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./datapulse.db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "datapulse"
    ALLOW_SQLITE_FALLBACK: bool = True

    # AI Configuration
    AI_PROVIDER: str = "rule_based"  # "rule_based", "openai", "gemini"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    def get_database_url(self) -> str:
        """
        Returns the resolved database connection URL.
        Constructs PostgreSQL URL if specific parameters are passed and DATABASE_URL is default.
        """
        if self.DATABASE_URL and not self.DATABASE_URL.startswith("sqlite") and "localhost" in self.DATABASE_URL:
            return self.DATABASE_URL
        
        # If POSTGRES credentials are fully configured in env, construct it
        if self.POSTGRES_PASSWORD and self.POSTGRES_USER:
            return (
                f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        return self.DATABASE_URL


settings = Settings()
