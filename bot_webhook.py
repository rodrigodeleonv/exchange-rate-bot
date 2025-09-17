"""FastAPI webhook server for Telegram bot."""

import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request, Response

from src.config import get_config
from src.infrastructure.telegram_bot import TelegramBot
from src.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


class WebhookServer:
    """FastAPI webhook server encapsulating all web server logic."""

    def __init__(self, bot_instance: TelegramBot):
        """Initialize webhook server with bot instance."""
        self.bot = bot_instance
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="Exchange Rate Bot Webhook",
            description="Telegram bot for exchange rates with webhook support",
            version="1.0.0",
            lifespan=self._lifespan,
        )

        # Register routes
        self._register_routes(app)
        return app

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """FastAPI lifespan context manager for startup and shutdown."""
        # Startup
        logger.info("🚀 Starting Exchange Rate Bot webhook...")

        try:
            self.bot.setup()

            if self.bot.webhook_url:
                await self.bot.set_webhook()
            else:
                logger.warning("⚠️ WEBHOOK_URL not configured. Set it in your .env file")

            logger.info("✅ Bot initialized successfully")
            yield

        except Exception as e:
            logger.error(f"❌ Error during startup: {e}")
            raise

        # Shutdown
        logger.info("🛑 Shutting down bot...")
        await self.bot.close(
            cleanup_webhook=get_config().telegram.cleanup_webhook_on_shutdown
        )
        logger.info("👋 Bot stopped")

    def _register_routes(self, app: FastAPI) -> None:
        """Register all FastAPI routes."""

        @app.post("/webhook")
        async def webhook_handler(request: Request) -> Response:
            """Handle incoming webhook updates from Telegram."""
            try:
                secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

                if not self.bot.webhook_secret_token:
                    logger.error(
                        "Webhook secret token not configured - rejecting request"
                    )
                    return Response(status_code=401)

                if not secret_token or secret_token != self.bot.webhook_secret_token:
                    logger.warning("Invalid or missing secret token in webhook request")
                    return Response(status_code=401)

                update_data = await request.json()
                update = Update.model_validate(update_data)
                await self.bot.process_update(update)
                return Response(status_code=200)
            except Exception as e:
                logger.error(f"❌ Error processing webhook: {e}")
                return Response(status_code=500)

        @app.get("/health")
        async def health_check() -> dict[str, Any]:
            """Health check endpoint."""
            return {"status": "ok"}

        @app.post("/testing/set-webhook", tags=["Testing"])
        async def set_webhook_endpoint() -> dict[str, str]:
            """Manually set webhook (for testing/management)."""
            try:
                await self.bot.set_webhook()
                return {"message": "Webhook set successfully"}
            except Exception as e:
                logger.error(f"Error setting webhook: {e}")
                return {"error": str(e)}

        @app.post("/testing/delete-webhook", tags=["Testing"])
        async def delete_webhook_endpoint() -> dict[str, str]:
            """Manually delete webhook."""
            try:
                await self.bot.delete_webhook()
                return {"message": "Webhook deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting webhook: {e}")
                return {"error": str(e)}

        @app.get("/testing/status", tags=["Testing"])
        async def status() -> dict[str, Any]:
            """Bot status endpoint."""
            return {
                "status": "healthy",
                "bot_configured": self.bot.bot is not None,
                "webhook_url": self.bot.webhook_url,
            }

    def run(self, run_dev: bool = False) -> None:
        """Run the webhook server."""
        try:
            logger.info("🌐 Starting FastAPI server. Production mode: %s", not run_dev)
            uvicorn.run(
                self.app if not run_dev else "bot_webhook:create_app",
                host=self.bot.host,
                port=self.bot.port,
                log_level=get_config().log.level.lower(),
                reload=run_dev,
            )
        except KeyboardInterrupt:
            logger.info("👋 Server stopped by user")
        except Exception as e:
            logger.exception(f"❌ Server error: {e}")


def create_app() -> FastAPI:
    """Factory function to create FastAPI app (for uvicorn reload)."""
    bot_instance = TelegramBot()
    server = WebhookServer(bot_instance)
    return server.app


def main() -> None:
    """Main application entry point."""
    # Create bot and server instances
    bot_instance = TelegramBot()
    server = WebhookServer(bot_instance)

    # Run server in development mode
    server.run(run_dev=True)


if __name__ == "__main__":
    main()
