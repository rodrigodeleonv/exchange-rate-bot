"""Banrural web scraper for USD exchange rates."""

import asyncio
import logging

import aiohttp

from src.config import get_config
from src.scrapers.base_scraper import ScraperBase

logger = logging.getLogger(__name__)


class BanruralScraper(ScraperBase):
    """Scraper for Banrural exchange rates."""

    BASE_URL = get_config().scraper_url.banrural_base_url

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the scraper."""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = {
            "User-Agent": get_config().scraper_header.user_agent,
            "Accept": get_config().scraper_header.accept,
            "Accept-Language": get_config().scraper_header.accept_language,
            "Accept-Encoding": get_config().scraper_header.accept_encoding,
            "Connection": get_config().scraper_header.connection,
            "Upgrade-Insecure-Requests": (
                get_config().scraper_header.upgrade_insec_req
            ),
        }

    async def get_usd_buy_rate(self) -> float | None:
        """Get USD buy rate from Banrural API."""
        try:
            logger.debug("Trying to get USD buy rate from Banrural API...")
            return await self._get_rate_from_api()

        except Exception as e:
            logger.error("Error getting USD buy rate from Banrural: %s", e)
            return None

    async def _get_rate_from_api(self) -> float | None:
        """Try to get rate from Banrural API."""
        api_url = "https://www.banrural.com.gt/_hcms/api/site/banrural/tasadecambio"

        # Add referer to appear as legitimate request
        api_headers = self.headers.copy()
        api_headers["Referer"] = self.BASE_URL
        api_headers["X-Requested-With"] = "XMLHttpRequest"

        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout, headers=api_headers
            ) as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Look for Banca Virtual APP buy rate in API response
                        if "compra_dolares_docto_bv" in data:
                            rate = float(data["compra_dolares_docto_bv"])
                            logger.info("Successfully got USD buy rate: %s", rate)
                            return rate

        except Exception as e:
            logger.debug("API request failed: %s", e)

        return None


async def get_banrural_usd_buy_rate() -> float | None:
    """Get current USD buy rate from Banrural quickly."""
    scraper = BanruralScraper()
    return await scraper.get_usd_buy_rate()


if __name__ == "__main__":

    async def test_scraper():
        """Test the Banrural scraper."""
        logging.basicConfig(level=logging.DEBUG)
        logger.info("Testing Banrural scraper...")

        # Test convenience function
        quick_rate = await get_banrural_usd_buy_rate()
        logger.info("Quick USD Buy Rate: %s", quick_rate)

    asyncio.run(test_scraper())
