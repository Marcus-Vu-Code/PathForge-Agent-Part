from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ProviderMode = Literal[
    "fake",
    "openai",
    "gemini",
    "qwen",
    "local",
    "hybrid-local-first",
    "hybrid-openai-first",
    "hybrid-gemini-first",
]


class Settings(BaseSettings):
    """Environment-driven application settings.

    Secrets are only read from the process environment and are never logged.
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    provider_mode: ProviderMode = Field(default="hybrid-gemini-first", alias="PATHFORGE_PROVIDER_MODE")
    database_url: str = Field(default="sqlite:///./pathforge.db", alias="PATHFORGE_DATABASE_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.6-flash", alias="GEMINI_MODEL")
    gemini_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        alias="GEMINI_BASE_URL",
    )
    qwen_model: str = Field(default="Qwen/Qwen3-4B-Instruct-2507", alias="QWEN_MODEL")
    qwen_max_new_tokens: int = Field(default=1800, alias="QWEN_MAX_NEW_TOKENS")
    qwen_max_input_chars: int = Field(default=12_000, alias="QWEN_MAX_INPUT_CHARS")
    qwen_device_map: str = Field(default="auto", alias="QWEN_DEVICE_MAP")
    qwen_torch_dtype: str = Field(default="auto", alias="QWEN_TORCH_DTYPE")
    qwen_fast_background_extraction: bool = Field(default=True, alias="QWEN_FAST_BACKGROUND_EXTRACTION")
    local_model_base_url: str = Field(default="http://localhost:8080", alias="LOCAL_MODEL_BASE_URL")
    local_model_timeout_seconds: float = Field(default=12.0, alias="LOCAL_MODEL_TIMEOUT_SECONDS")
    enable_openai_fallback: bool = Field(default=True, alias="PATHFORGE_ENABLE_OPENAI_FALLBACK")
    max_upload_bytes: int = Field(default=2_000_000, alias="PATHFORGE_MAX_UPLOAD_BYTES")


@lru_cache
def get_settings() -> Settings:
    return Settings()
