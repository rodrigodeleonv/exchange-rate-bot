"""Centralized logging configuration for the exchange rate bot."""

import logging
import logging.handlers
import sys
from pathlib import Path

from src.config import get_config


def setup_logging(log_dir: str | None = None) -> None:
    """
    Configure centralized logging with console and rotating file handlers.

    Args:
        log_dir: Directory for log files. Defaults to 'logs' in project root.
    """

    # Create logs directory
    if log_dir is None:
        log_dir_path = Path(__file__).parent.parent / "logs"
    else:
        log_dir_path = Path(log_dir)

    log_dir_path.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(get_config().log.level.upper())

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Rotating file handler for general logs
    app_log_file = log_dir_path / "app.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=app_log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding="utf-8",
        utc=True,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    file_handler.suffix = "%Y-%m-%d"  # Add date suffix to rotated files
    root_logger.addHandler(file_handler)

    # Separate error log file
    error_log_file = log_dir_path / "errors.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=error_log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days of error logs
        encoding="utf-8",
        utc=True,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    error_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(error_handler)

    # Configure specific loggers to reduce noise
    _configure_third_party_loggers()

    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    logger.info("Log directory: %s", log_dir_path.absolute())
    logger.info("Log level: %s", get_config().log.level)
    logger.info("Log retention: 30 days")


def _configure_third_party_loggers() -> None:
    """Configure third-party library loggers to reduce noise."""
    # Reduce uvicorn access log noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Reduce aiohttp noise
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    # Reduce watchfiles noise in development
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    # Keep aiogram logs at INFO level for debugging
    logging.getLogger("aiogram").setLevel(logging.INFO)
