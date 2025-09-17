"""Telegram notification service for broadcasting messages."""

import asyncio
import logging
from collections.abc import AsyncIterator

from src.infrastructure import TelegramBotClient

logger = logging.getLogger(__name__)


class TelegramNotification(TelegramBotClient):
    """Service for sending Telegram notifications to subscribers."""

    def __init__(self) -> None:
        """Initialize notification service."""
        super().__init__()

    async def send_message_safe(self, chat_id: int, text: str) -> bool:
        """Send message to a specific chat with error handling.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            await self.send_message(chat_id=chat_id, text=text)
            logger.info("✅ Message sent to chat_id: %s", chat_id)
            return True
        except Exception as e:
            logger.error("❌ Error sending to chat_id %s: %s", chat_id, e)
            return False

    async def broadcast_to_subscribers(
        self, chat_ids: AsyncIterator[int], text: str, delay_seconds: float = 0.1
    ) -> tuple[int, int]:
        """Broadcast message to multiple subscribers.

        Args:
            chat_ids: AsyncIterator of chat IDs to send to
            text: Message text to send
            delay_seconds: Delay between messages to avoid rate limiting

        Returns:
            Tuple of (sent_count, error_count)
        """
        sent_count = 0
        error_count = 0

        async for chat_id in chat_ids:
            success = await self.send_message_safe(chat_id=chat_id, text=text)

            if success:
                sent_count += 1
            else:
                error_count += 1

            # Rate limiting delay
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

        logger.info(
            "📊 Broadcast completed - Sent: %s, Errors: %s", sent_count, error_count
        )
        return sent_count, error_count

    # TODO: Not used
    async def send_exchange_rate_update(
        self, chat_ids: AsyncIterator[int], rates_message: str
    ) -> tuple[int, int]:
        """Send exchange rate update to subscribers.

        Args:
            chat_ids: AsyncIterator of chat IDs to notify
            rates_message: Formatted exchange rates message

        Returns:
            Tuple of (sent_count, error_count)
        """
        sent_count, error_count = await self.broadcast_to_subscribers(
            chat_ids=chat_ids, text=rates_message
        )

        logger.info("💱 Exchange rate update sent to %s subscribers", sent_count)
        return sent_count, error_count

    # TODO: Not used
    async def send_daily_summary(
        self, chat_ids: AsyncIterator[int], summary_message: str
    ) -> tuple[int, int]:
        """Send daily summary to subscribers.

        Args:
            chat_ids: AsyncIterator of chat IDs to notify
            summary_message: Daily summary message

        Returns:
            Tuple of (sent_count, error_count)
        """
        sent_count, error_count = await self.broadcast_to_subscribers(
            chat_ids=chat_ids,
            text=summary_message,
            delay_seconds=0.2,  # Slightly longer delay for summaries
        )

        logger.info("📈 Daily summary sent to %s subscribers", sent_count)
        return sent_count, error_count
