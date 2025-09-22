"""Repository pattern implementation using Protocols."""

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TelegramNotificationSubscription


@runtime_checkable
class NotificationSubscriptionRepositoryBase(Protocol):
    """Protocol for notification subscription repository operations."""

    async def create_subscription(
        self, chat_id: int
    ) -> TelegramNotificationSubscription:
        """Create a new notification subscription.

        Args:
            chat_id: Telegram chat ID to subscribe

        Returns:
            Created subscription instance
        """
        ...

    def get_all_chat_ids(self) -> AsyncIterator[int]:
        """Get all chat_ids from subscriptions.

        Returns:
            AsyncGenerator yielding chat_ids one by one.
        """
        ...

    async def delete_subscription(self, chat_id: int) -> bool:
        """Delete a notification subscription by chat_id.

        Args:
            chat_id: Telegram chat ID to unsubscribe

        Returns:
            True if subscription was deleted, False if not found
        """
        ...


class NotificationSubscriptionRepository(NotificationSubscriptionRepositoryBase):
    """SQLAlchemy implementation of notification subscription repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_subscription(
        self, chat_id: int
    ) -> TelegramNotificationSubscription:
        """Create a new notification subscription.

        Args:
            chat_id: Telegram chat ID to subscribe

        Returns:
            Created subscription instance
        """
        subscription = TelegramNotificationSubscription(chat_id=chat_id)
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def delete_subscription(self, chat_id: int) -> bool:
        """Delete a notification subscription by chat_id.

        Args:
            chat_id: Telegram chat ID to unsubscribe

        Returns:
            True if subscription was deleted, False if not found
        """
        stmt = select(TelegramNotificationSubscription).where(
            TelegramNotificationSubscription.chat_id == chat_id
        )
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()

        if subscription:
            await self.session.delete(subscription)
            await self.session.commit()
            return True
        return False

    async def get_all_chat_ids(self) -> AsyncIterator[int]:
        """Get all chat_ids from subscriptions.

        Returns:
            AsyncIterator yielding chat_ids one by one.
        """
        stmt = select(TelegramNotificationSubscription.chat_id).order_by(
            TelegramNotificationSubscription.id
        )
        stream = await self.session.stream_scalars(stmt)
        async for chat_id in stream:
            yield chat_id
