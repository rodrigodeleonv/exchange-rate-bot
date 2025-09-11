"""Exchange rate Telegram bot."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart

from src.config import get_config
from src.handlers.bot_handlers import BotHandlers
from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService

# Configure logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class ExchangeRateBot:
    """Exchange rate Telegram bot with clean architecture."""

    def __init__(self) -> None:
        """Initialize the bot with dependency injection."""
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.handlers: BotHandlers | None = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        self.bot_token = get_config().telegram_bot_token

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

    async def start_polling(self) -> None:
        """Start the bot polling."""
        if not self.bot or not self.dp:
            raise RuntimeError("Bot not properly initialized. Call setup() first.")

        logger.info("🚀 Starting bot...")
        logger.info("Press Ctrl+C to stop")

        try:
            await self.dp.start_polling(self.bot)  # pyright: ignore[reportUnknownMemberType]
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped")
        finally:
            await self.bot.session.close()


async def main() -> None:
    """Main function to run the bot."""
    try:
        bot = ExchangeRateBot()
        bot.setup()
        await bot.start_polling()
    except ValueError as e:
        logger.error(f"❌ Error: {e}")
        logger.info("💡 Create a .env file with your bot token")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.info("💡 Check your configuration and try again")


if __name__ == "__main__":
    asyncio.run(main())
