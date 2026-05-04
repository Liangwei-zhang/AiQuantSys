from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AiQuantSys", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(default="sqlite:///./aiquantsys.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    alpaca_api_key: str | None = Field(default=None, alias="ALPACA_API_KEY")
    alpaca_secret_key: str | None = Field(default=None, alias="ALPACA_SECRET_KEY")
    alpaca_paper_base_url: str = Field(
        default="https://paper-api.alpaca.markets", alias="ALPACA_PAPER_BASE_URL"
    )
    alpaca_data_base_url: str = Field(
        default="https://data.alpaca.markets", alias="ALPACA_DATA_BASE_URL"
    )

    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")

    default_timezone: str = Field(default="America/New_York", alias="DEFAULT_TIMEZONE")
    allow_live_trading: bool = Field(default=False, alias="ALLOW_LIVE_TRADING")
    allow_extended_hours: bool = Field(default=False, alias="ALLOW_EXTENDED_HOURS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
