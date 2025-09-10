import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


def setup_bot() -> tuple[Bot, Dispatcher]:
    """Initialize bot and dispatcher with environment variables."""
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Setup handlers with decorators
    setup_handlers(dp)

    return bot, dp


def setup_handlers(dp: Dispatcher) -> None:
    """Setup message handlers using decorators."""

    @dp.message(CommandStart())
    async def start_handler(message: Message) -> None:
        """Handle /start command."""
        user_name = message.from_user.first_name if message.from_user else "Usuario"
        await message.answer(
            f"¡Hola {user_name}! 👋\n"
            "Soy tu bot de tipos de cambio.\n"
            "Envía /help para ver los comandos disponibles."
        )

    @dp.message(Command("help"))
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

    @dp.message(Command("ping"))
    async def ping_handler(message: Message) -> None:
        """Handle /ping command."""
        await message.answer("🏓 Pong! El bot está funcionando correctamente.")


async def main() -> None:
    """Main function to run the bot."""
    try:
        bot, dp = setup_bot()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Create a .env file with your bot token")
        return

    print("🚀 Starting bot...")
    print("Press Ctrl+C to stop")

    try:
        # Start polling
        await dp.start_polling(bot)  # type: ignore[misc]
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
