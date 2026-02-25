"""Notification subscription repository."""

from collections.abc import AsyncIterator

from sqlalchemy import select

from src.database import get_session
from src.database.models import TelegramNotificationSubscription


class NotificationSubscriptionRepository:
    """Repository for notification subscription operations.

    Each method manages its own database session for simplicity and isolation.
    """

    async def create_subscription(self, chat_id: int) -> TelegramNotificationSubscription:
        """Get or create a new notification subscription.

        Args:
            chat_id: Telegram chat ID to subscribe

        Returns:
            Created or existing subscription instance
        """
        async with get_session() as session:
            stmt = select(TelegramNotificationSubscription).where(
                TelegramNotificationSubscription.chat_id == chat_id
            )
            result = await session.execute(stmt)
            existing = result.scalars().first()

            if existing:
                return existing

            subscription = TelegramNotificationSubscription(chat_id=chat_id)
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            return subscription

    async def delete_subscription(self, chat_id: int) -> bool:
        """Delete a notification subscription by chat_id.

        Args:
            chat_id: Telegram chat ID to unsubscribe

        Returns:
            True if subscription was deleted, False if not found
        """
        async with get_session() as session:
            stmt = select(TelegramNotificationSubscription).where(
                TelegramNotificationSubscription.chat_id == chat_id
            )
            result = await session.execute(stmt)
            subscription = result.scalar_one_or_none()

            if subscription:
                await session.delete(subscription)
                await session.commit()
                return True
            return False

    async def get_all_chat_ids(self) -> AsyncIterator[int]:
        """Get all chat_ids from subscriptions.

        Returns:
            AsyncIterator yielding chat_ids one by one.
        """
        chat_ids = []
        async with get_session() as session:
            stmt = select(TelegramNotificationSubscription.chat_id).order_by(
                TelegramNotificationSubscription.id
            )
            result = await session.execute(stmt)
            chat_ids = result.scalars().all()

        for chat_id in chat_ids:
            yield chat_id
