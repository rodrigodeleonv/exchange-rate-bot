import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.config import get_config
from src.services.exchange_rate_service import ExchangeRateService

# Configure logging
logging.basicConfig(level=logging.INFO)


class ExchangeRateBot:
    """Exchange rate Telegram bot."""

    def __init__(self) -> None:
        """Initialize the bot with configuration."""
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.exchange_service: ExchangeRateService | None = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment variables."""

        self.bot_token = get_config().telegram_bot_token

    def setup(self) -> None:
        """Setup bot and dispatcher with handlers."""
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher()
        self.exchange_service = ExchangeRateService()
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

💱 **Tipos de cambio:**
/rates - Ver todas las tasas de cambio USD/GTQ
/best - Ver la mejor tasa de compra
/compare - Comparar tasas entre bancos
            """
            await message.answer(help_text)

        @self.dp.message(Command("ping"))
        async def ping_handler(message: Message) -> None:
            """Handle /ping command."""
            await message.answer("🏓 Pong! El bot está funcionando correctamente.")

        @self.dp.message(Command("rates"))
        async def rates_handler(message: Message) -> None:
            """Handle /rates command to show all exchange rates."""
            if not self.exchange_service:
                await message.answer("❌ Servicio no disponible. Intenta más tarde.")
                return

            await message.answer("🔄 Obteniendo tasas de cambio...")

            try:
                rates = await self.exchange_service.get_all_rates()

                response_lines = ["💱 **Tasas de cambio USD/GTQ:**\n"]

                for bank_name, rate in rates.items():
                    if rate is not None:
                        # Format bank names for display
                        display_name = {
                            "banguat": "🏛️ Banguat (Oficial)",
                            "banrural": "🏦 Banrural (Banca Virtual)",
                            "nexa": "🏪 Nexa Banco (Compra)",
                        }.get(bank_name, bank_name)

                        response_lines.append(f"{display_name}: **Q{rate:.4f}**")
                    else:
                        display_name = {
                            "banguat": "🏛️ Banguat (Oficial)",
                            "banrural": "🏦 Banrural (Banca Virtual)",
                            "nexa": "🏪 Nexa Banco (Compra)",
                        }.get(bank_name, bank_name)
                        response_lines.append(f"{display_name}: ❌ No disponible")

                response_lines.append(
                    f"\n🕐 Actualizado: {asyncio.get_event_loop().time()}"
                )
                await message.answer("\n".join(response_lines))

            except Exception as e:
                logging.error("Error fetching rates: %s", e)
                await message.answer(
                    "❌ Error al obtener las tasas de cambio. Intenta más tarde."
                )

        @self.dp.message(Command("best"))
        async def best_handler(message: Message) -> None:
            """Handle /best command to show the best buy rate."""
            if not self.exchange_service:
                await message.answer("❌ Servicio no disponible. Intenta más tarde.")
                return

            await message.answer("🔄 Buscando la mejor tasa...")

            try:
                rates = await self.exchange_service.get_all_rates()

                # Filter out None values and find the best rate
                valid_rates = {k: v for k, v in rates.items() if v is not None}

                if not valid_rates:
                    await message.answer("❌ No hay tasas disponibles en este momento.")
                    return

                best_bank = max(valid_rates, key=lambda k: valid_rates[k])
                best_rate = valid_rates[best_bank]

                display_name = {
                    "banguat": "🏛️ Banguat (Oficial)",
                    "banrural": "🏦 Banrural (Banca Virtual)",
                    "nexa": "🏪 Nexa Banco (Compra)",
                }.get(best_bank, best_bank)

                response = (
                    f"🏆 **Mejor tasa de compra:**\n\n{display_name}: "
                    f"**Q{best_rate:.4f}**"
                )
                await message.answer(response)

            except Exception as e:
                logging.error("Error finding best rate: %s", e)
                await message.answer(
                    "❌ Error al buscar la mejor tasa. Intenta más tarde."
                )

        @self.dp.message(Command("compare"))
        async def compare_handler(message: Message) -> None:
            """Handle /compare command to compare rates across banks."""
            if not self.exchange_service:
                await message.answer("❌ Servicio no disponible. Intenta más tarde.")
                return

            await message.answer("🔄 Comparando tasas...")

            try:
                rates = await self.exchange_service.get_all_rates()

                # Filter out None values
                valid_rates = {k: v for k, v in rates.items() if v is not None}

                if len(valid_rates) < 2:
                    await message.answer(
                        "❌ Se necesitan al menos 2 tasas para comparar."
                    )
                    return

                # Sort rates by value (highest first)
                sorted_rates = sorted(
                    valid_rates.items(), key=lambda x: x[1], reverse=True
                )

                response_lines = ["📊 **Comparación de tasas:**\n"]

                for i, (bank_name, rate) in enumerate(sorted_rates):
                    display_name = {
                        "banguat": "🏛️ Banguat (Oficial)",
                        "banrural": "🏦 Banrural (Banca Virtual)",
                        "nexa": "🏪 Nexa Banco (Compra)",
                    }.get(bank_name, bank_name)

                    if i == 0:
                        response_lines.append(f"🥇 {display_name}: **Q{rate:.4f}**")
                    elif i == 1:
                        response_lines.append(f"🥈 {display_name}: **Q{rate:.4f}**")
                    elif i == 2:
                        response_lines.append(f"🥉 {display_name}: **Q{rate:.4f}**")
                    else:
                        response_lines.append(f"   {display_name}: **Q{rate:.4f}**")

                # Calculate difference between best and worst
                if len(sorted_rates) >= 2:
                    best_rate = sorted_rates[0][1]
                    worst_rate = sorted_rates[-1][1]
                    difference = best_rate - worst_rate
                    response_lines.append(f"\n📈 Diferencia: **Q{difference:.4f}**")

                await message.answer("\n".join(response_lines))

            except Exception as e:
                logging.error("Error comparing rates: %s", e)
                await message.answer("❌ Error al comparar tasas. Intenta más tarde.")

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
