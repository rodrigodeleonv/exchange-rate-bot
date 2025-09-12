"""Exchange rate Telegram bot with FastAPI webhook implementation."""

import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Update
from fastapi import FastAPI, Request, Response

from src.config import get_config
from src.handlers.bot_handlers import BotHandlers
from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExchangeRateBotWebhook:
    """Exchange rate Telegram bot with webhook support using FastAPI."""

    def __init__(self) -> None:
        """Initialize the bot with dependency injection."""
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.handlers: BotHandlers | None = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment."""
        self.bot_token = get_config().telegram_bot_token
        self.webhook_url = get_config().webhook_url
        self.host = get_config().host
        self.port = get_config().port

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
        """Register message handlers - equivalent to FastAPI route registration."""
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

    async def close(self) -> None:
        """Close bot session."""
        if self.bot:
            await self.bot.session.close()


# Global bot instance
bot_instance = ExchangeRateBotWebhook()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Exchange Rate Bot webhook...")

    try:
        bot_instance.setup()

        if bot_instance.webhook_url:
            await bot_instance.set_webhook()
        else:
            logger.warning("⚠️ WEBHOOK_URL not configured. Set it in your .env file")

        logger.info("✅ Bot initialized successfully")
        yield

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise

    # Shutdown
    logger.info("🛑 Shutting down bot...")
    await bot_instance.close()
    logger.info("👋 Bot stopped")


# Create FastAPI app
app = FastAPI(
    title="Exchange Rate Bot Webhook",
    description="Telegram bot for exchange rates with webhook support",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/webhook")
async def webhook_handler(request: Request) -> Response:
    """Handle incoming webhook updates from Telegram."""
    try:
        # Get update data from request
        update_data = await request.json()

        # Create Update object
        update = Update.model_validate(update_data)

        # Process the update
        await bot_instance.process_update(update)

        return Response(status_code=200)

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return Response(status_code=500)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Exchange Rate Bot Webhook"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "bot_configured": bot_instance.bot is not None,
        "webhook_url": bot_instance.webhook_url,
    }


@app.post("/set-webhook")
async def set_webhook_endpoint():
    """Manually set webhook (for testing/management)."""
    try:
        await bot_instance.set_webhook()
        return {"message": "Webhook set successfully"}
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return {"error": str(e)}


@app.post("/delete-webhook")
async def delete_webhook_endpoint():
    """Manually delete webhook (switch back to polling)."""
    try:
        await bot_instance.delete_webhook()
        return {"message": "Webhook deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    try:
        logger.info("🌐 Starting FastAPI server...")
        uvicorn.run(
            "bot_webhook:app",
            host=bot_instance.host,
            port=bot_instance.port,
            reload=True,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
