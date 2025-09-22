"""Centralized configuration module for environment variables and settings."""

from functools import lru_cache
from typing import ClassVar

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScrapperHeaderSettings(BaseModel):
    """Scrapper headers class."""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    accept_language: str = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
    accept_encoding: str = "gzip, deflate, br"
    connection: str = "keep-alive"
    upgrade_insec_req: str = "1"


class ScraperUrlSettings(BaseModel):
    """Scraper URL settings class."""

    banguat_base_url: str = "https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx"
    nexa_base_url: str = "https://www.nexabanco.com/"
    banrural_base_url: str = "https://www.banrural.com.gt/site/personas"


class TelegramSettings(BaseModel):
    """Telegram configuration class."""

    bot_token: SecretStr
    cleanup_webhook_on_shutdown: bool


class ServerSettings(BaseModel):
    """Server configuration class."""

    webhook_base_url: str
    webhook_endpoint: str = "/webhook"
    webhook_secret_token: SecretStr
    host: str
    port: int
    timezone: str


class DatabaseSettings(BaseModel):
    """Database configuration class."""

    url: str
    echo: bool


class LoggingSettings(BaseModel):
    """Logging configuration class."""

    level: str


class Config(BaseSettings):
    """Main configuration class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )

    telegram: TelegramSettings
    server: ServerSettings
    database: DatabaseSettings
    log: LoggingSettings

    scraper_url: ScraperUrlSettings = ScraperUrlSettings()
    scraper_header: ClassVar[ScrapperHeaderSettings] = ScrapperHeaderSettings()

    production: bool


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get the global configuration instance."""
    return Config()  # pyright: ignore[reportCallIssue]


if __name__ == "__main__":
    print(get_config())
