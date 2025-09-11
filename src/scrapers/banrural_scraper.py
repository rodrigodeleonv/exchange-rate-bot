"""Banrural web scraper for USD exchange rates."""

import asyncio
import logging
import re

import aiohttp

from src.config import get_config

logger = logging.getLogger(__name__)


class BanruralScraper:
    """Scraper for Banrural exchange rates."""

    BASE_URL = get_config().banrural_base_url

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the scraper."""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def get_usd_buy_rate(self) -> float | None:
        """Get USD buy rate from Banrural API."""
        try:
            logger.debug("Trying to get USD buy rate from Banrural API...")
            rate = await self._get_rate_from_api()
            if rate:
                return rate

            logger.debug("API request failed, falling back to web scraping...")
            return await self._get_rate_from_web()

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

    async def _get_rate_from_web(self) -> float | None:
        """Fallback: get rate from web scraping."""
        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout, headers=self.headers
            ) as session:
                async with session.get(self.BASE_URL) as response:
                    response.raise_for_status()
                    html_content = await response.text()

                    rate = await self._extract_rate_from_html(html_content)

                    if rate:
                        logger.info(
                            "Successfully extracted USD buy rate from web: %s", rate
                        )
                        return rate
                    else:
                        logger.warning("Could not find USD buy rate in HTML content")
                        return None

        except Exception as e:
            logger.error("Error scraping web: %s", e)
            return None

    async def _extract_rate_from_html(self, html_content: str) -> float | None:
        """Extract exchange rate from HTML content (fallback method)."""

        # Look for the specific rate pattern in HTML
        # Since Banrural loads data dynamically, this is mainly a fallback
        rate_patterns = [
            r"Q\s*(\d+\.\d+)",
            r"(\d+\.\d+)\s*Q",
            r"compra\s*[:=]\s*(\d+\.\d+)",
        ]

        for pattern in rate_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                try:
                    rate = float(match)
                    if 7.0 <= rate <= 9.0:
                        logger.debug("Found rate using pattern %s: %s", pattern, rate)
                        return rate
                except ValueError:
                    continue

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
