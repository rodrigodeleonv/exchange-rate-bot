"""Centralized configuration module for environment variables and settings."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass
class Config:
    """Main configuration class."""

    telegram_bot_token: str
    banguat_base_url: str
    banguat_timeout: int
    banguat_soap_namespace: str
    banguat_soap_action_prefix: str
    logging_level: str
    logging_format: str


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
        banguat_base_url=os.getenv(
            "BANGUAT_BASE_URL",
            "https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx",
        ),
        banguat_timeout=30,
        banguat_soap_namespace=os.getenv("BANGUAT_SOAP_NAMESPACE", ""),
        banguat_soap_action_prefix=os.getenv("BANGUAT_SOAP_ACTION_PREFIX", ""),
        logging_level=os.getenv("LOG_LEVEL", "INFO"),
        logging_format=os.getenv("LOG_FORMAT", ""),
    )
