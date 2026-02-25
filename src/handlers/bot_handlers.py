"""Bot message handlers - equivalent to FastAPI routers."""

from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.services import ExchangeRateService, MessageFormatter, SubscriptionService


class BotHandlers:
    """Telegram bot handlers with decorator-based registration."""

    def __init__(
        self,
        dp: Dispatcher,
        message_formatter: MessageFormatter,
        exchange_service: ExchangeRateService,
        subscription_service: SubscriptionService,
    ) -> None:
        """Initialize handlers and auto-register with dispatcher."""
        self.dp = dp
        self.message_formatter = message_formatter
        self.exchange_service = exchange_service
        self.subscription_service = subscription_service
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all handlers using decorators."""

        @self.dp.message(CommandStart())
        async def start_handler(message: Message) -> None:
            """Handle /start command."""
            user_name = message.from_user.first_name if message.from_user else "Usuario"
            response = self.message_formatter.format_start_message(user_name)
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("help"))
        async def help_handler(message: Message) -> None:
            """Handle /help command."""
            response = self.message_formatter.format_help_message()
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("ping"))
        async def ping_handler(message: Message) -> None:
            """Handle /ping command."""
            response = self.message_formatter.format_ping_message()
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("rates"))
        async def rates_handler(message: Message) -> None:
            """Handle /rates command."""
            loading_response = self.message_formatter.format_loading_message()
            loading_msg = await message.answer(loading_response, parse_mode=ParseMode.HTML)

            try:
                rates = await self.exchange_service.get_all_rates()
                response = self.message_formatter.format_rates_message(rates)
                await loading_msg.edit_text(response, parse_mode=ParseMode.HTML)
            except Exception:
                error_response = (
                    "❌ Error: No se pudieron obtener las tasas en este momento. "
                    "Por favor, inténtalo de nuevo más tarde."
                )
                await loading_msg.edit_text(error_response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("subscribe"))
        async def subscribe_handler(message: Message) -> None:
            """Handle /subscribe command."""
            if not message.from_user:
                await message.answer(
                    "❌ Error: No se pudo identificar el usuario.", parse_mode=ParseMode.HTML
                )
                return

            chat_id = message.chat.id
            await self.subscription_service.subscribe_user(chat_id)
            response = self.message_formatter.format_subscription_success()
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("unsubscribe"))
        async def unsubscribe_handler(message: Message) -> None:
            """Handle /unsubscribe command."""
            if not message.from_user:
                await message.answer(
                    "❌ Error: No se pudo identificar el usuario.", parse_mode=ParseMode.HTML
                )
                return

            chat_id = message.chat.id
            success = await self.subscription_service.unsubscribe_user(chat_id)
            if success:
                response = self.message_formatter.format_unsubscription_success()
            else:
                response = self.message_formatter.format_unsubscription_not_found()
            await message.answer(response, parse_mode=ParseMode.HTML)
