from pathlib import Path
import yaml
from pydantic import BaseModel


class ProjectConfig(BaseModel):
    brand: str
    content_root: str
    timezone: str


class OllamaConfig(BaseModel):
    target: str
    cloud_url: str
    localhost_url: str
    lan_url: str
    api_key_env: str
    text_model: str
    embedding_model: str


class OpenRouterConfig(BaseModel):
    base_url: str
    api_key_env_primary: str
    api_key_env_secondary: str
    text_model: str
    embedding_model: str


class ProvidersConfig(BaseModel):
    active_text: str
    active_embeddings: str
    ollama: OllamaConfig
    openrouter: OpenRouterConfig


class RuntimeConfig(BaseModel):
    delay_between_calls_ms: int
    delay_between_steps_ms: int
    max_retries: int
    retry_backoff_seconds: int
    switch_api_key_on_rate_limit: bool
    dry_run: bool


class SimilarityConfig(BaseModel):
    review_threshold: float
    reject_threshold: float
    keyword_review_threshold: float


class LoggingConfig(BaseModel):
    level: str


class AppConfig(BaseModel):
    project: ProjectConfig
    providers: ProvidersConfig
    runtime: RuntimeConfig
    similarity: SimilarityConfig
    logging: LoggingConfig


def load_config(path: Path) -> AppConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return AppConfig(**data)
