"""Bot message handlers - equivalent to FastAPI routers."""

from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.services.bot_service import BotService


class BotHandlers:
    """Telegram bot handlers with decorator-based registration."""

    def __init__(self, dp: Dispatcher, bot_service: BotService) -> None:
        """Initialize handlers and auto-register with dispatcher."""
        self.dp = dp
        self.bot_service = bot_service
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all handlers using decorators."""

        @self.dp.message(CommandStart())
        async def start_handler(message: Message) -> None:
            """Handle /start command."""
            user_name = message.from_user.first_name if message.from_user else "Usuario"
            response = await self.bot_service.get_start_message(user_name)
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("help"))
        async def help_handler(message: Message) -> None:
            """Handle /help command."""
            response = await self.bot_service.get_help_message()
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("ping"))
        async def ping_handler(message: Message) -> None:
            """Handle /ping command."""
            response = await self.bot_service.get_ping_message()
            await message.answer(response, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("rates"))
        async def rates_handler(message: Message) -> None:
            """Handle /rates command."""
            # Send loading message first
            loading_response = await self.bot_service.get_loading_message()
            loading_msg = await message.answer(loading_response, parse_mode=ParseMode.HTML)

            try:
                response = await self.bot_service.get_rates_response()
                await loading_msg.edit_text(response, parse_mode=ParseMode.HTML)
            except Exception:
                error_response = (
                    await self.bot_service.get_rates_response()
                )  # This will return error message
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
            response = await self.bot_service.subscribe_user(chat_id)
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
            response = await self.bot_service.unsubscribe_user(chat_id)
            await message.answer(response, parse_mode=ParseMode.HTML)
