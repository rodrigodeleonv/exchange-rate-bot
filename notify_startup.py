"""Send startup notification to Telegram chat."""

import asyncio
import logging

from src.config import get_config
from src.database import get_session
from src.infrastructure import TelegramNotification
from src.repositories import NotificationSubscriptionRepository

# Configure basic logging
logging.basicConfig(level=get_config().log.level)
logger = logging.getLogger(__name__)


async def send_startup_notification():
    """Send message to your Telegram chat."""
    try:
        notification_bot = TelegramNotification()

        sent_count = 0

        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)

            async for chat_id in repo.get_all_chat_ids():
                try:
                    # Send startup message
                    await notification_bot.send_message(
                        chat_id=chat_id, text="🚀 Hola async!"
                    )
                    sent_count += 1
                    logger.info("✅ Startup message sent to chat_id: %s", chat_id)
                except Exception as e:
                    logger.error("❌ Error sending to chat_id %s: %s", chat_id, e)
                    continue

        if sent_count == 0:
            logger.error("No chat_id found in notification subscriptions")
            logger.info("To add a subscription:")
            logger.info("1. Send /subscribe command to your bot")
            logger.info(
                "2. Or manually add a record to notification_subscriptions table"
            )
        else:
            logger.info("📊 Startup notifications sent to %s subscribers", sent_count)

        # Close bot session
        await notification_bot.close()

    except Exception as e:
        logger.error("❌ Failed to send startup message: %s", e)


if __name__ == "__main__":
    asyncio.run(send_startup_notification())
