"""Exchange rate service."""

import asyncio
import logging
from collections.abc import Mapping
from typing import cast

from src.scrapers.banguat_client import BanguatClient
from src.scrapers.banrural_scraper import BanruralScraper
from src.scrapers.base_scraper import ScraperBase
from src.scrapers.nexa_scraper import NexaScraper

logger = logging.getLogger(__name__)


Rates = Mapping[str, float | None]


class ExchangeRateService:
    """Service to aggregate exchange rates from multiple sources."""

    def __init__(self) -> None:
        """Initialize the service with all scrapers."""

        self.scrapers: tuple[ScraperBase, ...] = (
            BanguatClient(),
            BanruralScraper(),
            NexaScraper(),
        )

    async def get_all_rates(self) -> Rates:
        """Get rates from all banks concurrently."""
        logger.info("Fetching exchange rates from all sources...")

        # Run all scrapers concurrently - automatically scales with new scrapers
        tasks = [scraper.get_usd_buy_rate() for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to scraper names using class names
        rates: Rates = {}

        for i, scraper in enumerate(self.scrapers):
            class_name = scraper.__class__.__name__.lower()
            scraper_name = class_name.replace("client", "").replace("scraper", "")
            result = results[i]
            if isinstance(result, Exception):
                logger.error("Error getting rate from %s: %s", scraper_name, result)
                rates[scraper_name] = None
            else:
                rates[scraper_name] = cast(float | None, result)

        logger.info("Completed fetching rates: %s", rates)
        return rates
