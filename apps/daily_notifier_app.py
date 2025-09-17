"""Daily rates notifier application."""

import asyncio
import logging

from src.config import get_config
from src.database import get_session
from src.infrastructure.telegram_notification import TelegramNotification
from src.repositories import NotificationSubscriptionRepository
from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService

# Configure basic logging
logging.basicConfig(level=get_config().log.level)
logger = logging.getLogger(__name__)


class DailyNotifierApp:
    """Application for sending daily exchange rate notifications."""

    def __init__(self):
        """Initialize daily notifier with services."""
        self.notification_bot = TelegramNotification()
        self.exchange_service = ExchangeRateService()
        self.bot_service = BotService(self.exchange_service)

    async def send_daily_rates_notification(self) -> tuple[int, int]:
        """Send daily exchange rates to all subscribers.

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
                return 0, 0

            # Format notification message
            message = await self.bot_service.format_daily_notification(rates)

            # Get subscribers and send notifications
            sent_count = 0
            error_count = 0

            async with get_session() as session:
                repo = NotificationSubscriptionRepository(session)

                async for chat_id in repo.get_all_chat_ids():
                    try:
                        await self.notification_bot.send_message(chat_id=chat_id, text=message)
                        sent_count += 1
                        logger.info("✅ Daily rates sent to chat_id: %s", chat_id)

                        # Small delay to avoid rate limiting
                        await asyncio.sleep(0.1)

                    except Exception as e:
                        error_count += 1
                        logger.error("❌ Error sending to chat_id %s: %s", chat_id, e)
                        continue

            # Log results
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

            return sent_count, error_count

        except Exception as e:
            logger.error("❌ Failed to send daily rates notification: %s", e)
            return 0, 1

    async def send_startup_notification(self) -> tuple[int, int]:
        """Send startup notification to subscribers (legacy method).

        Returns:
            Tuple of (sent_count, error_count)
        """
        try:
            logger.info("🚀 Sending startup notification...")

            sent_count = 0
            error_count = 0

            async with get_session() as session:
                repo = NotificationSubscriptionRepository(session)

                async for chat_id in repo.get_all_chat_ids():
                    try:
                        await self.notification_bot.send_message(
                            chat_id=chat_id, text="🚀 Exchange Rate Bot started successfully!"
                        )
                        sent_count += 1
                        logger.info("✅ Startup message sent to chat_id: %s", chat_id)
                    except Exception as e:
                        error_count += 1
                        logger.error("❌ Error sending to chat_id %s: %s", chat_id, e)
                        continue

            if sent_count == 0:
                logger.error("No subscribers found for startup notification")
            else:
                logger.info("📊 Startup notifications sent to %s subscribers", sent_count)

            return sent_count, error_count

        except Exception as e:
            logger.error("❌ Failed to send startup notification: %s", e)
            return 0, 1

    async def close(self):
        """Close notification bot session."""
        await self.notification_bot.close()


async def send_daily_rates():
    """Main function for daily rates notification."""
    app = DailyNotifierApp()
    try:
        await app.send_daily_rates_notification()
    finally:
        await app.close()


async def send_startup_notification():
    """Main function for startup notification (legacy)."""
    app = DailyNotifierApp()
    try:
        await app.send_startup_notification()
    finally:
        await app.close()


def main_daily():
    """Entry point for daily rates notification."""
    asyncio.run(send_daily_rates())


def main_startup():
    """Entry point for startup notification."""
    asyncio.run(send_startup_notification())


if __name__ == "__main__":
    # Default to daily rates
    main_daily()
