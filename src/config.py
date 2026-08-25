from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is one level up from this file (armstrong_bikes/)
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str

    # Per-agent model assignments:
    # Specialists (cost + lead-time): Haiku 4.5 — fast, structured JSON, cost-effective
    # Coordinator, formatter, Q&A: Sonnet 4.6 — nuanced reasoning and prose quality
    specialist_model: str = "claude-haiku-4-5-20251001"
    coordinator_model: str = "claude-sonnet-4-6"
    formatter_model: str = "claude-sonnet-4-6"
    qa_model: str = "claude-sonnet-4-6"

    host: str = "0.0.0.0"
    port: int = 8000

    # Price per million tokens for cost-per-decision reporting
    # Haiku 4.5: $0.80 input / $4.00 output per 1M tokens
    # Sonnet 4.6: $3.00 input / $15.00 output per 1M tokens
    haiku_input_price_per_m: float = 0.80
    haiku_output_price_per_m: float = 4.00
    sonnet_input_price_per_m: float = 3.00
    sonnet_output_price_per_m: float = 15.00

    @property
    def skills_dir(self) -> Path:
        return PROJECT_ROOT

    @property
    def data_dir(self) -> Path:
        return PROJECT_ROOT / "data"

    @property
    def frontend_dir(self) -> Path:
        return PROJECT_ROOT / "frontend"


settings = Settings()
