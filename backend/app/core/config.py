from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_from_backend(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (backend_root() / path).resolve()


class AppSettings(BaseSettings):
    """Application-level configuration loaded through Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    name: str = "Enterprise AI Financial Customer Intelligence Platform"
    version: str = "0.1.0"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


class DatabaseSettings(BaseSettings):
    """Database configuration for the local SQLite foundation."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        env_prefix="DATABASE_",
        extra="ignore",
    )

    url: str = "sqlite:///../data/enterprise_ai_financial_platform.db"
    echo: bool = False

    @property
    def sqlite_path(self) -> Path:
        if not self.url.startswith("sqlite:///"):
            msg = "Only SQLite URLs are supported."
            raise ValueError(msg)

        raw_path = self.url.replace("sqlite:///", "", 1)
        path = Path(raw_path).expanduser()
        if path.is_absolute():
            return path
        return resolve_from_backend(raw_path)

    @property
    def sqlalchemy_url(self) -> str:
        return f"sqlite:///{self.sqlite_path.as_posix()}"


class DataSettings(BaseSettings):
    """Local dataset storage paths."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        env_prefix="DATA_",
        extra="ignore",
    )

    raw_dir: str = "../data/raw"
    processed_dir: str = "../data/processed"
    external_dir: str = "../data/external"
    samples_dir: str = "../data/samples"
    policies_dir: str = "../data/policies"

    def resolve(self, value: str) -> Path:
        return resolve_from_backend(value)

    @property
    def raw_path(self) -> Path:
        return self.resolve(self.raw_dir)

    @property
    def processed_path(self) -> Path:
        return self.resolve(self.processed_dir)

    @property
    def external_path(self) -> Path:
        return self.resolve(self.external_dir)

    @property
    def samples_path(self) -> Path:
        return self.resolve(self.samples_dir)

    @property
    def policies_path(self) -> Path:
        return self.resolve(self.policies_dir)


class AISettings(BaseSettings):
    """AI processing and provider configuration loaded through Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        env_prefix="AI_",
        extra="ignore",
    )

    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 5
    max_tokens: int = 1200
    chunk_size: int = 1000
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    conversation_memory: bool = True
    groq_api_key: str | None = None
    openai_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com/openai/v1"
    openai_base_url: str = "https://api.openai.com/v1"
    retrieval_top_k: int = 4
    similarity_threshold: float = 0.18
    vectorstore_dir: str = "../vectorstore"
    prompt_dir: str = "app/prompts/templates"

    @property
    def vectorstore_path(self) -> Path:
        path = Path(self.vectorstore_dir).expanduser()
        if path.is_absolute():
            return path
        return resolve_from_backend(self.vectorstore_dir)

    @property
    def prompt_path(self) -> Path:
        path = Path(self.prompt_dir).expanduser()
        if path.is_absolute():
            return path
        return resolve_from_backend(self.prompt_dir)


class MLSettings(BaseSettings):
    """Machine learning configuration for local model training and artifacts."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        env_prefix="ML_",
        extra="ignore",
    )

    artifact_dir: str = "../models"
    random_seed: int = 42
    test_size: float = 0.2
    risk_model_name: str = "risk_prediction"
    segmentation_model_name: str = "customer_segmentation"
    segmentation_clusters: int = 5

    @property
    def artifact_path(self) -> Path:
        path = Path(self.artifact_dir).expanduser()
        if path.is_absolute():
            return path
        return resolve_from_backend(self.artifact_dir)


class LoggingSettings(BaseSettings):
    """Structured logging configuration."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        env_prefix="LOGGING_",
        extra="ignore",
    )

    level: str = "INFO"
    structured: bool = True


class Settings(BaseModel):
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    ai: AISettings = Field(default_factory=AISettings)
    ml: MLSettings = Field(default_factory=MLSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
