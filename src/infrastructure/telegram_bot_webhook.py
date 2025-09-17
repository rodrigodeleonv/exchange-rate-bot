"""Telegram bot webhook infrastructure and command handling."""

import logging

from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Update

from src.handlers.bot_handlers import BotHandlers
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
        """Setup bot with dependency injection pattern."""
        # Initialize dispatcher
        self.dp = Dispatcher()

        # Initialize services (dependency injection)
        exchange_service = ExchangeRateService()
        bot_service = BotService(exchange_service)
        self.handlers = BotHandlers(bot_service)

        # Register command handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register message handlers with dispatcher."""
        if not self.dp or not self.handlers:
            raise RuntimeError("Components not initialized")

        # TODO: Use decorators ~Replace with aiogram 4.0 handlers~
        self.dp.message(CommandStart())(self.handlers.start_handler)
        self.dp.message(Command("help"))(self.handlers.help_handler)
        self.dp.message(Command("ping"))(self.handlers.ping_handler)
        self.dp.message(Command("rates"))(self.handlers.rates_handler)
        self.dp.message(Command("subscribe"))(self.handlers.subscribe_handler)
        self.dp.message(Command("unsubscribe"))(self.handlers.unsubscribe_handler)

    async def process_update(self, update: Update) -> None:
        """Process incoming webhook update."""
        if not self.dp:
            raise RuntimeError("Dispatcher not initialized")

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
                logger.warning(f"Failed to cleanup webhook: {e}")

        await super().close()
