"""Nexa Banco web scraper for USD exchange rates."""

import asyncio
import logging
import re

import aiohttp
from bs4 import BeautifulSoup

from src.config import get_config
from src.scrapers.base_scraper import ScraperBase

logger = logging.getLogger(__name__)


class NexaScraper(ScraperBase):
    """Scraper for Nexa Banco exchange rates."""

    BASE_URL = get_config().nexa_base_url

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the scraper."""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = {
            "User-Agent": get_config().scrapper_headers.user_agent,
            "Accept": get_config().scrapper_headers.accept,
            "Accept-Language": get_config().scrapper_headers.accept_language,
            "Accept-Encoding": get_config().scrapper_headers.accept_encoding,
            "Connection": get_config().scrapper_headers.connection,
            "Upgrade-Insecure-Requests": (
                get_config().scrapper_headers.upgrade_insec_req
            ),
        }

    async def get_usd_buy_rate(self) -> float | None:
        """Get USD buy rate (Compra) from Nexa Banco website."""
        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout, headers=self.headers
            ) as session:
                async with session.get(self.BASE_URL) as response:
                    response.raise_for_status()
                    html_content = await response.text()

                    # Parse HTML with BeautifulSoup
                    soup = BeautifulSoup(html_content, "html.parser")

                    # Look for exchange rate information in various ways
                    rate = await self._extract_rate_from_html(soup)

                    if rate:
                        logger.info("Successfully extracted USD buy rate: %s", rate)
                        return rate
                    else:
                        logger.warning("Could not find USD buy rate in HTML content")
                        return None

        except Exception as e:
            logger.error("Error getting USD buy rate from Nexa: %s", e)
            return None

    async def _extract_rate_from_html(self, soup: BeautifulSoup) -> float | None:
        """Extract exchange rate from HTML content."""
        html_text = soup.get_text()

        # Look for "Compra: X.XX" pattern
        match = re.search(r"Compra:\s*(\d+\.\d+)", html_text, re.IGNORECASE)
        if match:
            try:
                rate = float(match.group(1))
                logger.debug("Found USD buy rate: %s", rate)
                return rate
            except ValueError:
                pass

        return None


async def get_nexa_usd_buy_rate() -> float | None:
    """Get current USD buy rate from Nexa Banco quickly."""
    scraper = NexaScraper()
    return await scraper.get_usd_buy_rate()


if __name__ == "__main__":

    async def test_scraper():
        """Test the Nexa scraper."""
        logging.basicConfig(level=logging.DEBUG)
        logger.info("Testing Nexa Banco scraper...")

        # Test convenience function
        quick_rate = await get_nexa_usd_buy_rate()
        logger.info("Quick USD Buy Rate: %s", quick_rate)

    asyncio.run(test_scraper())
