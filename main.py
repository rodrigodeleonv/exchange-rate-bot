import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.config import get_config


class ExchangeRateBot:
    """Exchange rate Telegram bot."""

    def __init__(self) -> None:
        """Initialize the bot with configuration."""
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment variables."""

        self.bot_token = get_config().telegram_bot_token

    def setup(self) -> None:
        """Setup bot and dispatcher with handlers."""
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup message handlers using decorators."""
        if not self.dp:
            raise RuntimeError("Dispatcher not initialized")

        @self.dp.message(CommandStart())
        async def start_handler(message: Message) -> None:
            """Handle /start command."""
            user_name = message.from_user.first_name if message.from_user else "Usuario"
            await message.answer(
                f"¡Hola {user_name}! 👋\n"
                "Soy tu bot de tipos de cambio.\n"
                "Envía /help para ver los comandos disponibles."
            )

        @self.dp.message(Command("help"))
        async def help_handler(message: Message) -> None:
            """Handle /help command."""
            help_text = """
🤖 **Comandos disponibles:**

/start - Iniciar el bot
/help - Mostrar esta ayuda
/ping - Verificar que el bot funciona

🔄 **Próximamente:**
- Conversión de monedas
- Tipos de cambio en tiempo real
            """
            await message.answer(help_text)

        @self.dp.message(Command("ping"))
        async def ping_handler(message: Message) -> None:
            """Handle /ping command."""
            await message.answer("🏓 Pong! El bot está funcionando correctamente.")

    async def start_polling(self) -> None:
        """Start the bot polling."""
        if not self.bot or not self.dp:
            raise RuntimeError("Bot not properly initialized. Call setup() first.")

        print("🚀 Starting bot...")
        print("Press Ctrl+C to stop")

        try:
            await self.dp.start_polling(self.bot)  # pyright: ignore[reportUnknownMemberType]
        except KeyboardInterrupt:
            print("\n👋 Bot stopped")
        finally:
            await self.bot.session.close()


async def main() -> None:
    """Main function to run the bot."""
    try:
        bot = ExchangeRateBot()
        bot.setup()
        await bot.start_polling()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Create a .env file with your bot token")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check your configuration and try again")


if __name__ == "__main__":
    asyncio.run(main())
