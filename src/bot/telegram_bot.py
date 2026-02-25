"""Telegram bot client with webhook and notification capabilities."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from src.config import get_config
from src.utils import build_url

logger = logging.getLogger(__name__)


class TelegramBot:
    """Unified Telegram bot client for webhook, polling, and notifications."""

    def __init__(self) -> None:
        """Initialize Telegram bot client."""
        self._load_config()
        self._bot: Bot | None = None
        self.dp: Dispatcher | None = None

    def _load_config(self) -> None:
        """Load configuration from environment."""
        self.bot_token = get_config().telegram.bot_token.get_secret_value()
        self.webhook_url = self._build_webhook_url()
        self.webhook_secret_token = get_config().server.webhook_secret_token.get_secret_value()
        self.host = get_config().server.host
        self.port = get_config().server.port

    def _build_webhook_url(self) -> str:
        """Build webhook URL."""
        return build_url(get_config().server.webhook_base_url, get_config().server.webhook_endpoint)

    @property
    def bot(self) -> Bot:
        """Get or create Bot instance."""
        if self._bot is None:
            self._bot = Bot(token=self.bot_token)
        return self._bot

    def setup_dispatcher(self) -> Dispatcher:
        """Initialize and return dispatcher for handler registration."""
        if self.dp is None:
            self.dp = Dispatcher()
        return self.dp

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> None:
        """Send message to a specific chat.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            parse_mode: Parse mode for message formatting
        """
        await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

    async def send_message_safe(self, chat_id: int, text: str) -> bool:
        """Send message with error handling.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            await self.send_message(chat_id=chat_id, text=text)
            logger.info("✅ Message sent to chat_id: %s", chat_id)
            return True
        except Exception as e:
            logger.error("❌ Error sending to chat_id %s: %s", chat_id, e)
            return False

    async def broadcast_to_chat_ids(
        self, chat_ids: list[int], text: str, delay_seconds: float = 0.1
    ) -> tuple[int, int]:
        """Broadcast message to multiple chat IDs.

        Args:
            chat_ids: List of chat IDs to send to
            text: Message text to send
            delay_seconds: Delay between messages to avoid rate limiting

        Returns:
            Tuple of (sent_count, error_count)
        """
        sent_count = 0
        error_count = 0

        for chat_id in chat_ids:
            success = await self.send_message_safe(chat_id=chat_id, text=text)

            if success:
                sent_count += 1
            else:
                error_count += 1

            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

        logger.info("📊 Broadcast completed - Sent: %s, Errors: %s", sent_count, error_count)
        return sent_count, error_count

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

    async def process_update(self, update: Update) -> None:
        """Process incoming webhook update."""
        if not self.dp:
            raise RuntimeError("Dispatcher not initialized")

        await self.dp.feed_update(bot=self.bot, update=update)

    async def start_polling(self) -> None:
        """Start bot in polling mode (alternative to webhook)."""
        if not self.dp:
            raise RuntimeError("Bot not properly initialized. Call setup_dispatcher() first.")

        logger.info("🚀 Starting bot in polling mode...")
        logger.info("Press Ctrl+C to stop")

        try:
            await self.dp.start_polling(self.bot)
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

        if self._bot:
            await self._bot.session.close()
            self._bot = None
