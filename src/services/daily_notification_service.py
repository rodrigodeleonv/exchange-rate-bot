"""Daily notification service for exchange rate notifications."""

import asyncio
import logging

from src.database import get_session
from src.infrastructure.telegram_notification import TelegramNotification
from src.repositories import NotificationSubscriptionRepository
from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService

logger = logging.getLogger(__name__)


class DailyNotificationService:
    """Service for handling daily exchange rate notifications."""

    def __init__(
        self,
        exchange_service: ExchangeRateService,
        bot_service: BotService,
        telegram_client: TelegramNotification,
    ):
        """Initialize the daily notification service.

        Args:
            exchange_service: Service for fetching exchange rates
            bot_service: Service for formatting messages
            telegram_client: Client for sending Telegram messages
        """
        self.exchange_service = exchange_service
        self.bot_service = bot_service
        self.telegram_client = telegram_client

    async def send_daily_notifications(self) -> tuple[int, int]:
        """Send daily exchange rate notifications to all subscribers.

        Returns:
            Tuple of (sent_count, error_count)
        """
        try:
            logger.info("🌅 Starting daily rates notification...")

            # Get current exchange rates
            logger.info("📊 Fetching current exchange rates...")
            rates = await self.exchange_service.get_all_rates()

            if not any(rates.values()):
                logger.error("❌ No exchange rates available")
                return 0, 1

            # Format notification message
            message = await self.bot_service.format_daily_notification(rates)

            # Send notifications to all subscribers
            sent_count, error_count = await self._send_to_subscribers(message)

            # Log final results
            self._log_notification_results(sent_count, error_count)

            return sent_count, error_count

        except Exception as e:
            logger.error("❌ Failed to send daily rates notification: %s", e, exc_info=True)
            return 0, 1

    async def _send_to_subscribers(self, message: str) -> tuple[int, int]:
        """Send message to all subscribers.

        Args:
            message: The formatted message to send

        Returns:
            Tuple of (sent_count, error_count)
        """
        sent_count = 0
        error_count = 0

        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)

            async for chat_id in repo.get_all_chat_ids():
                try:
                    await self.telegram_client.send_message(chat_id=chat_id, text=message)
                    sent_count += 1
                    logger.info("✅ Daily rates sent to chat_id: %s", chat_id)

                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)

                except Exception as e:
                    error_count += 1
                    logger.error("❌ Error sending to chat_id %s: %s", chat_id, e)
                    continue

        return sent_count, error_count

    def _log_notification_results(self, sent_count: int, error_count: int) -> None:
        """Log the results of the notification process.

        Args:
            sent_count: Number of successfully sent notifications
            error_count: Number of failed notifications
        """
        if sent_count == 0:
            logger.error("No subscribers found for daily notification")
            logger.info("To add subscribers:")
            logger.info("1. Send /subscribe command to your bot")
            logger.info("2. Or manually add records to notification_subscriptions table")
        else:
            logger.info(
                "📊 Daily rates notification completed - Sent: %s, Errors: %s",
                sent_count,
                error_count,
            )

    async def close(self) -> None:
        """Close the telegram client connection."""
        await self.telegram_client.close()
