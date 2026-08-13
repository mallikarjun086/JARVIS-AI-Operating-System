"""
Pydantic Settings for Backend Configuration.
Handles PostgreSQL, SQLite fallback, CORS origins, JWT security, and AI provider settings.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "JARVIS AI Operating System"
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    PORT: int = Field(default=8000)
    HOST: str = Field(default="0.0.0.0")
    LOG_LEVEL: str = Field(default="INFO")

    # Security Settings
    SECRET_KEY: str = Field(
        default="jarvis_super_secret_jwt_key_change_in_production_min_32_chars!",
        description="Secret key for JWT token signatures"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)  # 24 Hours

    # Database Configuration
    DATABASE_URL: Optional[str] = Field(default=None)
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="jarvis_admin")
    POSTGRES_PASSWORD: str = Field(default="jarvis_secure_password")
    POSTGRES_DB: str = Field(default="jarvis_os")
    SQLITE_FALLBACK_URL: str = Field(default="sqlite+aiosqlite:///./jarvis_dev.db")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://localhost:8000"
        ]
    )

    # AI Provider API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API Key")
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API Key")

    # AI Provider Behaviour Settings
    DEFAULT_PROVIDER: str = Field(default="MockProvider", description="Default routing provider")
    ENABLE_PROVIDER_FALLBACK: bool = Field(default=True, description="Enable automatic fallback")
    ENABLE_STREAMING: bool = Field(default=True, description="Enable SSE streaming")
    ENABLE_COST_TRACKING: bool = Field(default=True, description="Enable cost telemetry")
    REQUEST_TIMEOUT: int = Field(default=60, description="Provider HTTP timeout in seconds")
    MAX_RETRIES: int = Field(default=3, description="Max retry attempts per provider")
    MAX_CONTEXT_MESSAGES: int = Field(default=50, description="Maximum messages in context window")
    MAX_PROMPT_BYTES: int = Field(default=512_000, description="Max request payload bytes")

    # Conversation Session Limits
    SESSION_TTL_SECONDS: int = Field(default=3600, description="Session idle expiry in seconds")
    MAX_CONCURRENT_SESSIONS: int = Field(default=1000, description="Max concurrent in-memory sessions")

    # Memory Engine Configuration
    CHROMA_PERSIST_PATH: str = Field(default="./chroma_db", description="ChromaDB persistence directory")
    CHROMA_COLLECTION_NAME: str = Field(default="jarvis_memory", description="Default ChromaDB collection name")
    EMBEDDING_PROVIDER: str = Field(default="sentence_transformer", description="Embedding provider: openai | sentence_transformer")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    SENTENCE_TRANSFORMER_MODEL: str = Field(default="all-MiniLM-L6-v2", description="Sentence Transformer model name")
    EMBEDDING_DIMENSION: int = Field(default=384, description="Embedding vector dimension")
    EMBEDDING_CACHE_SIZE: int = Field(default=1000, description="Max LRU embedding cache entries")
    MEMORY_MAX_BATCH_SIZE: int = Field(default=100, description="Max batch size for bulk memory insert")
    MEMORY_DEFAULT_TOP_K: int = Field(default=5, description="Default top-k for memory retrieval")
    MEMORY_MIN_IMPORTANCE: float = Field(default=0.3, description="Minimum importance threshold for retrieval")
    MEMORY_COMPRESSION_THRESHOLD: int = Field(default=10, description="Min turns before conversation compression")

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=200, description="Max requests per minute per IP")
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting middleware")

    # JARVIS Command Center Settings
    JARVIS_MAX_SESSION_HISTORY: int = Field(default=20, description="Max conversation turns per session")
    JARVIS_APPROVAL_TIMEOUT_SECONDS: int = Field(default=300, description="Approval gate timeout")
    JARVIS_MAX_CONCURRENT_EXECUTIONS: int = Field(default=5, description="Max parallel task executions")

    # Feature Flags
    ENABLE_VOICE_STT: bool = Field(default=True)
    ENABLE_VOICE_TTS: bool = Field(default=True)
    ENABLE_BROWSER_AUTOMATION: bool = Field(default=True)
    ENABLE_DESKTOP_AUTOMATION: bool = Field(default=True, description="Enabled desktop automation suite")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    def is_production(self) -> bool:
        """Returns True if system is running in production mode."""
        return self.ENV.lower() in ["prod", "production"]

    def validate_production_security(self) -> List[str]:
        """Validates critical production security parameters."""
        warnings: List[str] = []
        if self.is_production() and "change_in_production" in self.SECRET_KEY:
            warnings.append("CRITICAL: Default development SECRET_KEY is active in production environment.")
        if self.is_production() and self.DEBUG:
            warnings.append("WARNING: DEBUG mode is enabled in production environment.")
        return warnings

    def get_async_database_url(self) -> str:
        """Returns the async database URL — PostgreSQL if configured, else SQLite fallback."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Ensure asyncpg driver for postgres
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return self.SQLITE_FALLBACK_URL


settings = Settings()
