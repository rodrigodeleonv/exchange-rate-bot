"""Webhook application - FastAPI server for Telegram bot."""

import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request, Response

from src.bot import TelegramBot
from src.config import get_config
from src.handlers.bot_handlers import BotHandlers
from src.logging_config import setup_logging
from src.services import ExchangeRateService, MessageFormatter, SubscriptionService

setup_logging()
logger = logging.getLogger(__name__)


class WebhookApp:
    """FastAPI webhook application encapsulating all web server logic."""

    def __init__(self, telegram_bot: TelegramBot):
        """Initialize webhook app with bot instance."""
        self.telegram_bot = telegram_bot
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="Exchange Rate Bot Webhook",
            description="Telegram bot webhook server for exchange rates",
            version="1.0.0",
            lifespan=self._lifespan,
        )

        self._register_routes(app)
        return app

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """FastAPI lifespan context manager for startup and shutdown."""
        # Startup
        logger.info("🚀 Starting Exchange Rate Bot webhook...")

        # Setup bot dispatcher and handlers
        try:
            dp = self.telegram_bot.setup_dispatcher()

            # Initialize services
            exchange_service = ExchangeRateService()
            message_formatter = MessageFormatter()
            subscription_service = SubscriptionService()

            # Register handlers
            BotHandlers(dp, message_formatter, exchange_service, subscription_service)

            logger.info("✅ Bot client initialized successfully")
        except Exception as e:
            logger.error("❌ Critical error during bot setup: %s", e)
            raise

        # Setup webhook (optional - can fail gracefully)
        await self._setup_webhook()

        logger.info("🚀 FastAPI server ready to accept requests")

        yield

        # Shutdown
        await self._shutdown_bot()

    async def _setup_webhook(self) -> None:
        """Setup webhook with proper error handling."""
        if not self.telegram_bot.webhook_url:
            logger.error("⚠️ WEBHOOK_URL not configured. Server running without webhook setup")
            return

        try:
            await self.telegram_bot.set_webhook()
            logger.info("✅ Webhook configured successfully")
        except Exception as webhook_error:
            logger.error("⚠️ Failed to set webhook: %s", webhook_error)
            logger.warning(
                "⚠️ Server will continue running - webhook endpoints available for manual setup"
            )

    async def _shutdown_bot(self) -> None:
        """Shutdown bot with proper error handling."""
        logger.info("🛑 Shutting down bot...")
        try:
            await self.telegram_bot.close(
                cleanup_webhook=get_config().telegram.cleanup_webhook_on_shutdown
            )
            logger.info("✅ Bot shutdown completed successfully")
        except Exception as shutdown_error:
            logger.warning("⚠️ Error during bot shutdown: %s", shutdown_error)
        logger.info("👋 Server stopped")

    def _register_routes(self, app: FastAPI) -> None:
        """Register FastAPI routes."""

        @app.post("/webhook")
        async def webhook_handler(request: Request) -> Response:
            """Handle incoming webhook updates from Telegram."""
            try:
                secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

                if not self.telegram_bot.webhook_secret_token:
                    logger.error("Webhook secret token not configured - rejecting request")
                    return Response(status_code=401)

                if secret_token != self.telegram_bot.webhook_secret_token:
                    logger.warning("Invalid secret token.")
                    return Response(status_code=401)

                update_data = await request.json()
                update = Update.model_validate(update_data)
                await self.telegram_bot.process_update(update)
                return Response(status_code=200)
            except Exception as e:
                logger.error("❌ Error processing webhook: %s", e)
                return Response(status_code=500)

        @app.get("/health")
        async def health_check() -> dict[str, Any]:
            """Bot status endpoint."""
            return {
                "status": "healthy",
                "webhook_url": self.telegram_bot.webhook_url,
            }

    def run(self, run_dev: bool = False) -> None:
        """Run the webhook server."""
        logger.info("🌐 Starting FastAPI server. Production mode: %s", not run_dev)
        uvicorn.run(
            self.app if not run_dev else "apps.webhook_app:create_app",
            host=self.telegram_bot.host,
            port=self.telegram_bot.port,
            log_level=get_config().log.level.lower(),
            reload=run_dev,
        )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app (for uvicorn reload)."""
    bot_instance = TelegramBot()
    app = WebhookApp(bot_instance)
    return app.app


def main() -> None:
    """Main application entry point."""
    # Create bot and app instances
    bot_instance = TelegramBot()
    app = WebhookApp(bot_instance)

    app.run(run_dev=not get_config().production)


if __name__ == "__main__":
    main()
