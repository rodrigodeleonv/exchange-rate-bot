"""Timezone utils."""

from zoneinfo import ZoneInfo

from src.config import get_config


def get_tz() -> ZoneInfo:
    """Get current timezone from ENV."""
    return ZoneInfo(get_config().server.timezone)
