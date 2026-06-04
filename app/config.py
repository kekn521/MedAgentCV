from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = dotenv_values(Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")

	openai_api_key: str = _env.get("OPENAI_API_KEY", "")
	openai_model: str = _env.get("OPENAI_MODEL", "")
	max_iterations: int = int(_env.get("MAX_ITERATIONS", "3"))

@lru_cache
def get_settings() -> Settings:
	return Settings()
