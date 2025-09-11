"""Bot message handlers - equivalent to FastAPI routers."""

from aiogram.types import Message

from src.services.bot_service import BotService


class BotHandlers:
    """Telegram bot handlers with minimal business logic."""

    def __init__(self, bot_service: BotService) -> None:
        """Initialize handlers with bot service dependency."""
        self.bot_service = bot_service

    async def start_handler(self, message: Message) -> None:
        """Handle /start command."""
        user_name = message.from_user.first_name if message.from_user else "Usuario"
        response = await self.bot_service.get_start_message(user_name)
        await message.answer(response)

    async def help_handler(self, message: Message) -> None:
        """Handle /help command."""
        response = await self.bot_service.get_help_message()
        await message.answer(response)

    async def ping_handler(self, message: Message) -> None:
        """Handle /ping command."""
        response = await self.bot_service.get_ping_message()
        await message.answer(response)

    async def rates_handler(self, message: Message) -> None:
        """Handle /rates command."""
        # Send loading message
        loading_response = await self.bot_service.get_loading_message()
        await message.answer(loading_response)

        # Get formatted rates response
        response = await self.bot_service.get_rates_response()
        await message.answer(response)

    async def subscribe_handler(self, message: Message) -> None:
        """Handle /subscribe command."""
        chat_id = message.chat.id
        response = await self.bot_service.subscribe_user(chat_id)
        await message.answer(response)

    async def unsubscribe_handler(self, message: Message) -> None:
        """Handle /unsubscribe command."""
        chat_id = message.chat.id
        response = await self.bot_service.unsubscribe_user(chat_id)
        await message.answer(response)
