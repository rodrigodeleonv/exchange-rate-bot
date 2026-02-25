"""Subscription management service."""

import logging

from src.repositories import NotificationSubscriptionRepository

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing notification subscriptions."""

    def __init__(self) -> None:
        """Initialize subscription service."""
        self.repository = NotificationSubscriptionRepository()

    async def subscribe_user(self, chat_id: int) -> None:
        """Subscribe user to daily notifications.

        Args:
            chat_id: Telegram chat ID to subscribe
        """
        await self.repository.create_subscription(chat_id=chat_id)
        logger.info("User %s subscribed to notifications", chat_id)

    async def unsubscribe_user(self, chat_id: int) -> bool:
        """Unsubscribe user from daily notifications.

        Args:
            chat_id: Telegram chat ID to unsubscribe

        Returns:
            True if user was unsubscribed, False if not found
        """
        success = await self.repository.delete_subscription(chat_id=chat_id)
        if success:
            logger.info("User %s unsubscribed from notifications", chat_id)
        else:
            logger.info("User %s was not subscribed to notifications", chat_id)
        return success
