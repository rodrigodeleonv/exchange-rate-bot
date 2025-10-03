"""Telegram bot webhook infrastructure and command handling."""

import logging

from aiogram import Dispatcher
from aiogram.types import Update

from src.handlers.bot_handlers import BotHandlers
from src.presentation import TemplateRenderer
from src.repositories import SessionScopedSubscriptionRepository
from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService

from .telegram_bot_client import TelegramBotClient

logger = logging.getLogger(__name__)


class TelegramBotWebhook(TelegramBotClient):
    """Telegram bot webhook infrastructure with command handling."""

    def __init__(self) -> None:
        """Initialize webhook bot with dependency injection."""
        super().__init__()
        self.dp: Dispatcher | None = None
        self.handlers: BotHandlers | None = None

    def setup(self) -> None:
        """Initialize bot components and register handlers.

        Note: The repository creates a new database session per operation (request-scoped pattern).
        """
        self.dp = Dispatcher()

        # Initialize services with dependency injection
        exchange_service = ExchangeRateService()
        # Create a repository that creates sessions on-demand per request
        subscription_repo = SessionScopedSubscriptionRepository()
        # Create template renderer for message formatting
        template_renderer = TemplateRenderer()
        bot_service = BotService(exchange_service, subscription_repo, template_renderer)

        # Initialize handlers with auto-registration
        self.handlers = BotHandlers(self.dp, bot_service)

    async def process_update(self, update: Update) -> None:
        """Process incoming webhook update."""
        if not self.dp:
            raise RuntimeError("Dispatcher not initialized")

        # Feed update to aiogram's Dispatcher for routing:
        # 1. Dispatcher analyzes the Update object (message, callback_query, etc.)
        # 2. Searches for handlers registered with @dp.message() decorators (see BotHandlers)
        # 3. Applies filters (CommandStart, Command("help"), etc.) to find matching handler
        # 4. Executes the matched handler (e.g., start_handler, help_handler, etc.)
        # 5. Handler delegates to service layer for business logic
        # 6. Handler sends response back to Telegram via message.answer()
        await self.dp.feed_update(bot=self.bot, update=update)

    async def start_polling(self) -> None:
        """Start bot in polling mode (alternative to webhook)."""
        if not self.dp:
            raise RuntimeError("Bot not properly initialized. Call setup() first.")

        logger.info("🚀 Starting bot in polling mode...")
        logger.info("Press Ctrl+C to stop")

        try:
            await self.dp.start_polling(self.bot)  # pyright: ignore[reportUnknownMemberType]
        finally:
            logger.info("👋 Bot stopped")
            await self.close()

    async def close(self, cleanup_webhook: bool = False) -> None:
        """Close bot session and optionally cleanup webhook."""
        if cleanup_webhook:
            try:
                await self.delete_webhook()
            except Exception as e:
                logger.warning("Failed to cleanup webhook: %s", e)

        await super().close()
