"""Simple Banco de Guatemala SOAP API client using aiohttp."""

import asyncio
import logging
from xml.etree import ElementTree as ET

import aiofiles
import aiohttp

from src.config import get_config

logger = logging.getLogger(__name__)


class BanguatClient:
    """Simple async client for Banco de Guatemala exchange rate API."""

    BASE_URL = get_config().banguat_base_url

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the client."""
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def get_daily_usd_rate(self) -> float | None:
        """Get current USD exchange rate."""
        async with aiofiles.open(
            "src/resources/soap_templates/exchange_rate_daily.xml", encoding="utf-8"
        ) as f:
            soap_body = await f.read()

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    self.BASE_URL, data=soap_body, headers=headers
                ) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

                    # Parse XML response
                    root = ET.fromstring(xml_content)

                    # Find USD reference rate
                    # Look for CambioDolar/VarDolar/referencia
                    for elem in root.iter():
                        if elem.tag.endswith("referencia") and elem.text:
                            try:
                                return float(elem.text)
                            except ValueError:
                                continue

                    # Fallback: look for USD in exchange rates (sell rate)
                    for elem in root.iter():
                        if elem.tag.endswith("venta") and elem.text:
                            try:
                                return float(elem.text)
                            except ValueError:
                                continue

        except Exception as e:
            logger.error("Error getting USD rate: %s", e)

        return None


async def get_current_usd_rate() -> float | None:
    """Get current USD exchange rate quickly."""
    client = BanguatClient()
    return await client.get_daily_usd_rate()


if __name__ == "__main__":

    async def test_client():
        """Test the client."""
        logging.basicConfig(level=logging.INFO)
        logger.info("Testing Banguat client...")

        quick_rate = await get_current_usd_rate()
        logger.info("Using convenience function... Quick USD Rate: %s", quick_rate)

    asyncio.run(test_client())
