"""
Configuration Management for JARVIS AI Operating System.
Uses Pydantic BaseSettings for strict environment parsing and validation.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core System Environment
    APP_NAME: str = "JARVIS AI Operating System"
    ENV: str = Field(default="development", description="Environment: development, production, testing")
    DEBUG: bool = Field(default=False, description="Enable debug logging and diagnostic details")
    HOST: str = Field(default="0.0.0.0", description="API Server Bind Host")
    PORT: int = Field(default=8000, description="API Server Bind Port")
    LOG_LEVEL: str = Field(default="INFO", description="System log level")

    # LLM Gateway Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    LLM_MODEL: str = Field(default="gpt-4o", description="Primary LLM Model Identifier")
    LLM_TEMPERATURE: float = Field(default=0.2, description="Generation Temperature")
    LLM_TIMEOUT_SECONDS: float = Field(default=30.0, description="API Call Timeout in Seconds")
    LLM_MAX_RETRIES: int = Field(default=3, description="Maximum API Retry Attempts")
    LLM_FALLBACK_MODE: bool = Field(default=True, description="Enable offline fallback LLM when API is unreachable")

    # Vector Memory Store Configuration
    VECTOR_DIMENSION: int = Field(default=384, description="Vector Embeddings Dimension Size")
    VECTOR_STORE_PATH: Path = Field(default=Path("./data/vector_store.json"), description="Vector Database Storage Path")
    SIMILARITY_THRESHOLD: float = Field(default=0.65, description="Minimum cosine similarity for memory retrieval")

    # Process Scheduler Configuration
    SCHEDULER_CONCURRENCY: int = Field(default=10, description="Maximum Concurrent Processes Executing in Scheduler")
    MAX_TASK_TIMEOUT_SECONDS: int = Field(default=300, description="Maximum Allowed Execution Time for Single Task")

    # Security Sandbox Settings
    WORKSPACE_ROOT: Path = Field(default=Path(".").resolve(), description="Absolute Sandbox Root Workspace Path")
    ALLOW_SHELL_EXECUTION: bool = Field(default=False, description="Explicit flag allowing restricted shell command execution")

    # Database Persistence Settings
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./jarvis_os.db", description="Async SQLAlchemy Database URI")


# Global Settings Singleton
settings = Settings()
