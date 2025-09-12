"""Centralized configuration module for environment variables and settings."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class ScrapperHeaders:
    """User agent class."""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    accept: str = (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    )
    accept_language: str = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
    accept_encoding: str = "gzip, deflate, br"
    connection: str = "keep-alive"
    upgrade_insec_req: str = "1"


@dataclass(frozen=True)
class Config:
    """Main configuration class."""

    # Telegram
    telegram_bot_token: str

    # Webhook configuration
    webhook_url: str
    webhook_secret_token: str
    cleanup_webhook_on_shutdown: bool
    host: str
    port: int

    # Scrapers
    banguat_base_url: str
    nexa_base_url: str
    banrural_base_url: str
    scrapper_headers: ScrapperHeaders

    # Logging
    logging_level: str


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get the global configuration instance."""
    load_dotenv()

    # TODO: Add validation for required environment variables
    # Check if required environment variables are set
    # if not os.getenv("TELEGRAM_BOT_TOKEN"):
    #     raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

    return Config(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        webhook_url=os.getenv("WEBHOOK_URL", ""),
        webhook_secret_token=os.getenv("WEBHOOK_SECRET_TOKEN", ""),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        cleanup_webhook_on_shutdown=os.getenv(
            "CLEANUP_WEBHOOK_ON_SHUTDOWN", "False"
        ).lower()
        == "true",
        banguat_base_url=os.getenv(
            "BANGUAT_BASE_URL",
            "https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx",
        ),
        nexa_base_url="https://www.nexabanco.com/",
        banrural_base_url="https://www.banrural.com.gt/site/personas",
        scrapper_headers=ScrapperHeaders(),
        logging_level=os.getenv("LOG_LEVEL", "INFO"),
    )
