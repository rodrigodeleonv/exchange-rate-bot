"""Base Telegram bot client for common operations."""

import logging

from aiogram import Bot

from src.config import get_config

logger = logging.getLogger(__name__)


class TelegramBotClient:
    """Base Telegram bot client with common functionality."""

    def __init__(self) -> None:
        """Initialize Telegram bot client."""
        self._load_config()
        self._bot: Bot | None = None

    def _load_config(self) -> None:
        """Load configuration from environment."""
        self.bot_token = get_config().telegram.bot_token.get_secret_value()
        self.webhook_url = get_config().server.webhook_url
        self.webhook_secret_token = get_config().server.webhook_secret_token.get_secret_value()
        self.host = get_config().server.host
        self.port = get_config().server.port

    @property
    def bot(self) -> Bot:
        """Get or create Bot instance."""
        if self._bot is None:
            self._bot = Bot(token=self.bot_token)
        return self._bot

    async def send_message(self, chat_id: int, text: str) -> None:
        """Send message to a specific chat.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send
        """
        await self.bot.send_message(chat_id=chat_id, text=text)

    async def set_webhook(self) -> None:
        """Set webhook URL for the bot."""
        if not self.webhook_url:
            raise RuntimeError("Webhook URL not configured")

        if not self.webhook_secret_token:
            raise RuntimeError("Webhook secret token is required for security")

        logger.info("Setting webhook to: %s", self.webhook_url)

        await self.bot.set_webhook(
            url=self.webhook_url,
            secret_token=self.webhook_secret_token,
            drop_pending_updates=True,
        )
        logger.info("✅ Webhook set successfully with secret token")

    async def delete_webhook(self) -> None:
        """Delete webhook (useful for switching back to polling)."""
        await self.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️ Webhook deleted")

    async def close(self) -> None:
        """Close bot session."""
        if self._bot:
            await self._bot.session.close()
            self._bot = None
