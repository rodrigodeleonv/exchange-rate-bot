"""Telegram bot infrastructure and webhook management."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Update

from src.config import get_config
from src.handlers.bot_handlers import BotHandlers
from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot infrastructure with webhook support."""

    def __init__(self) -> None:
        """Initialize the bot with dependency injection."""
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.handlers: BotHandlers | None = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment."""
        config = get_config()
        self.bot_token = config.telegram_bot_token
        self.webhook_url = config.webhook_url
        self.host = config.host
        self.port = config.port

    def setup(self) -> None:
        """Setup bot with dependency injection pattern."""
        # Initialize core components
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher()

        # Initialize services (dependency injection)
        exchange_service = ExchangeRateService()
        bot_service = BotService(exchange_service)
        self.handlers = BotHandlers(bot_service)

        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register message handlers."""
        if not self.dp or not self.handlers:
            raise RuntimeError("Components not initialized")

        self.dp.message(CommandStart())(self.handlers.start_handler)
        self.dp.message(Command("help"))(self.handlers.help_handler)
        self.dp.message(Command("ping"))(self.handlers.ping_handler)
        self.dp.message(Command("rates"))(self.handlers.rates_handler)
        self.dp.message(Command("subscribe"))(self.handlers.subscribe_handler)
        self.dp.message(Command("unsubscribe"))(self.handlers.unsubscribe_handler)

    async def set_webhook(self) -> None:
        """Set webhook URL for the bot."""
        if not self.bot or not self.webhook_url:
            raise RuntimeError("Bot or webhook URL not configured")
        logger.info("Setting webhook to: %s", self.webhook_url)

        await self.bot.set_webhook(url=self.webhook_url, drop_pending_updates=True)
        logger.info("✅ Webhook set successfully")

    async def delete_webhook(self) -> None:
        """Delete webhook (useful for switching back to polling)."""
        if not self.bot:
            raise RuntimeError("Bot not initialized")

        await self.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️ Webhook deleted")

    async def process_update(self, update: Update) -> None:
        """Process incoming webhook update."""
        if not self.dp or not self.bot:
            raise RuntimeError("Bot components not initialized")

        await self.dp.feed_update(bot=self.bot, update=update)

    async def close(self, cleanup_webhook: bool = False) -> None:
        """Close bot session and optionally cleanup webhook."""
        if cleanup_webhook and self.bot:
            try:
                await self.delete_webhook()
            except Exception as e:
                logger.warning(f"Failed to cleanup webhook: {e}")

        if self.bot:
            await self.bot.session.close()

    async def start_polling(self) -> None:
        """Start bot in polling mode (alternative to webhook)."""
        if not self.bot or not self.dp:
            raise RuntimeError("Bot not properly initialized. Call setup() first.")

        logger.info("🚀 Starting bot in polling mode...")
        logger.info("Press Ctrl+C to stop")

        try:
            await self.dp.start_polling(self.bot)  # pyright: ignore[reportUnknownMemberType]
        finally:
            logger.info("👋 Bot stopped")
            await self.close()
