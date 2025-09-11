"""Base scraper class."""

from typing import Protocol


class ScraperBase(Protocol):
    """Protocol for scrapers."""

    async def get_usd_buy_rate(self) -> float | None:
        """Get current USD buy rate."""
        raise NotImplementedError
