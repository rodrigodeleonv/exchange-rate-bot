"""Repository pattern implementation using Protocols."""

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import TelegramNotificationSubscription


@runtime_checkable
class NotificationSubscriptionRepositoryBase(Protocol):
    """Protocol for notification subscription repository operations."""

    async def create_subscription(self, chat_id: int) -> TelegramNotificationSubscription:
        """Get or create a new notification subscription.

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

    async def create_subscription(self, chat_id: int) -> TelegramNotificationSubscription:
        """Get or create a new notification subscription.

        Args:
            chat_id: Telegram chat ID to subscribe

        Returns:
            Created subscription instance
        """
        # Check if subscription already exists
        stmt = select(TelegramNotificationSubscription).where(
            TelegramNotificationSubscription.chat_id == chat_id
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()

        if existing:
            return existing

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


class SessionScopedSubscriptionRepository(NotificationSubscriptionRepositoryBase):
    """Repository that creates a new session for each operation.

    This implementation follows the request-scoped session pattern,
    creating and closing a database session for each repository operation.
    Ideal for webhook handlers where each request should have its own session.
    """

    async def create_subscription(self, chat_id: int) -> TelegramNotificationSubscription:
        """Get or create a new notification subscription.

        Args:
            chat_id: Telegram chat ID to subscribe

        Returns:
            Created subscription instance
        """
        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)
            return await repo.create_subscription(chat_id)

    async def delete_subscription(self, chat_id: int) -> bool:
        """Delete a notification subscription by chat_id.

        Args:
            chat_id: Telegram chat ID to unsubscribe

        Returns:
            True if subscription was deleted, False if not found
        """
        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)
            return await repo.delete_subscription(chat_id)

    async def get_all_chat_ids(self) -> AsyncIterator[int]:
        """Get all chat_ids from subscriptions.

        Returns:
            AsyncIterator yielding chat_ids one by one.
        """
        chat_ids = []
        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)
            async for chat_id in repo.get_all_chat_ids():
                chat_ids.append(chat_id)
        for chat_id in chat_ids:
            yield chat_id
