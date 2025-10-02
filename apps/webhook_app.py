"""Webhook application - FastAPI server for Telegram bot."""

import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Header, Response

from src.config import get_config
from src.infrastructure.telegram_bot_webhook import TelegramBotWebhook
from src.infrastructure.telegram_webhook_schemas import TelegramWebhookUpdate
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class WebhookApp:
    """FastAPI webhook application encapsulating all web server logic."""

    def __init__(self, bot_webhook: TelegramBotWebhook):
        """Initialize webhook app with bot instance."""
        self.bot_webhook = bot_webhook
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

        # Setup bot client (critical - must succeed)
        try:
            self.bot_webhook.setup()
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
        if not self.bot_webhook.webhook_url:
            logger.error("⚠️ WEBHOOK_URL not configured. Server running without webhook setup")
            return

        try:
            await self.bot_webhook.set_webhook()
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
            await self.bot_webhook.close(
                cleanup_webhook=get_config().telegram.cleanup_webhook_on_shutdown
            )
            logger.info("✅ Bot shutdown completed successfully")
        except Exception as shutdown_error:
            logger.warning("⚠️ Error during bot shutdown: %s", shutdown_error)
        logger.info("👋 Server stopped")

    def _register_routes(self, app: FastAPI) -> None:
        """Register FastAPI routes."""

        @app.post("/webhook")
        async def webhook_handler(
            telegram_update: TelegramWebhookUpdate,
            x_telegram_bot_api_secret_token: str | None = Header(
                None, description="Telegram Bot API Secret Token for webhook validation"
            ),
        ) -> Response:
            """Handle incoming webhook updates from Telegram."""
            try:
                if not self.bot_webhook.webhook_secret_token:
                    logger.error("Webhook secret token not configured - rejecting request")
                    return Response(status_code=401)

                if x_telegram_bot_api_secret_token != self.bot_webhook.webhook_secret_token:
                    logger.warning("Invalid secret token.")
                    return Response(status_code=401)

                logger.info("Received update_id: %s", telegram_update.update_id)
                if telegram_update.message:
                    user_id = (
                        telegram_update.message.from_.id
                        if telegram_update.message.from_
                        else "unknown"
                    )
                    logger.info(
                        "Message from user %s: %s",
                        user_id,
                        telegram_update.message.text,
                    )

                update = Update.model_validate(telegram_update.model_dump(by_alias=True))
                await self.bot_webhook.process_update(update)
                return Response(status_code=200)
            except Exception as e:
                logger.error("❌ Error processing webhook: %s", e)
                return Response(status_code=500)

        @app.get("/health")
        async def health_check() -> dict[str, Any]:
            """Bot status endpoint."""
            return {
                "status": "healthy",
                "webhook_url": self.bot_webhook.webhook_url,
            }

    def run(self, run_dev: bool = False) -> None:
        """Run the webhook server."""
        logger.info("🌐 Starting FastAPI server. Production mode: %s", not run_dev)
        uvicorn.run(
            self.app if not run_dev else "apps.webhook_app:create_app",
            host=self.bot_webhook.host,
            port=self.bot_webhook.port,
            log_level=get_config().log.level.lower(),
            reload=run_dev,
        )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app (for uvicorn reload)."""
    bot_instance = TelegramBotWebhook()
    app = WebhookApp(bot_instance)
    return app.app


def main() -> None:
    """Main application entry point."""
    # Create bot and app instances
    bot_instance = TelegramBotWebhook()
    app = WebhookApp(bot_instance)

    app.run(run_dev=not get_config().production)


if __name__ == "__main__":
    main()
