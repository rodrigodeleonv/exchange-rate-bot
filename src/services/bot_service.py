"""Bot service layer - contains business logic and response formatting."""

import logging

from src.services.exchange_rate_service import ExchangeRateService, Rates

logger = logging.getLogger(__name__)


class BotService:
    """Service layer for bot business logic and response formatting."""

    def __init__(self, exchange_service: ExchangeRateService) -> None:
        """Initialize bot service with dependencies."""
        self.exchange_service = exchange_service
        self.subscribers: list[int] = []

    async def get_start_message(self, user_name: str) -> str:
        """Generate start message for user."""
        return (
            f"¡Hola {user_name}! 👋\n"
            "Soy tu bot de tipos de cambio.\n"
            "Envía /help para ver los comandos disponibles."
        )

    async def get_help_message(self) -> str:
        """Generate help message with available commands."""
        return """
🤖 **Comandos disponibles:**

/start - Iniciar el bot
/help - Mostrar esta ayuda
/ping - Verificar que el bot funciona

💱 **Tipos de cambio:**
/rates - Ver todas las tasas de cambio USD/GTQ

📢 **Notificaciones:**
/subscribe - Recibir notificaciones diarias
/unsubscribe - Cancelar notificaciones
        """

    async def get_ping_message(self) -> str:
        """Generate ping response message."""
        return "🏓 Pong! El bot está funcionando correctamente."

    async def get_loading_message(self) -> str:
        """Generate loading message for rate requests."""
        return "🔄 Obteniendo tasas de cambio..."

    async def get_rates_response(self) -> str:
        """Get formatted exchange rates response."""
        try:
            rates = await self.exchange_service.get_all_rates()
            return self._format_rates_message(rates)
        except Exception as e:
            logger.error("Error fetching rates: %s", e)
            return "❌ Error al obtener las tasas de cambio. Intenta más tarde."

    async def subscribe_user(self, chat_id: int) -> str:
        """Subscribe user to daily notifications."""
        if chat_id not in self.subscribers:
            self.subscribers.append(chat_id)
            logger.info(f"User {chat_id} subscribed to notifications")
            return (
                "✅ ¡Suscrito exitosamente!\n"
                "Recibirás notificaciones diarias con las tasas de cambio."
            )
        else:
            return "ℹ️ Ya estás suscrito a las notificaciones diarias."

    async def unsubscribe_user(self, chat_id: int) -> str:
        """Unsubscribe user from daily notifications."""
        if chat_id in self.subscribers:
            self.subscribers.remove(chat_id)
            logger.info(f"User {chat_id} unsubscribed from notifications")
            return "❌ Te has desuscrito de las notificaciones diarias."
        else:
            return "ℹ️ No estás suscrito a notificaciones."

    def _format_rates_message(self, rates: Rates) -> str:
        """Format rates data into user-friendly message."""
        response_lines = ["💱 **Tasas de cambio USD/GTQ:**\n"]

        # Find best rate for highlighting
        valid_rates = {k: v for k, v in rates.items() if v is not None}
        best_bank = (
            max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
        )

        for bank_name, rate in rates.items():
            display_name = self._get_bank_display_name(bank_name)

            if rate is not None:
                emoji = " ⭐" if bank_name == best_bank else ""
                response_lines.append(f"{display_name}: **Q{rate:.4f}**{emoji}")
            else:
                response_lines.append(f"{display_name}: ❌ No disponible")

        if best_bank:
            response_lines.append(f"\n🏆 **Mejor tasa**: Q{valid_rates[best_bank]:.4f}")

        return "\n".join(response_lines)

    def _get_bank_display_name(self, bank_name: str) -> str:
        """Get user-friendly display name for bank."""
        display_names = {
            "banguat": "🏛️ Banguat (Oficial)",
            "banrural": "🏦 Banrural (Banca Virtual)",
            "nexa": "🏪 Nexa Banco (Compra)",
        }
        return display_names.get(bank_name, bank_name)

    def get_subscribers(self) -> list[int]:
        """Get list of subscribed chat IDs."""
        return self.subscribers.copy()

    async def format_daily_notification(self, rates: dict[str, float | None]) -> str:
        """Format daily notification message."""
        from datetime import datetime

        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        header = f"🌅 **Buenos días!**\n📅 {current_time}\n\n"

        rates_message = self._format_rates_message(rates)
        footer = "\n💡 Usa /rates para ver tasas actualizadas en cualquier momento"

        return header + rates_message + footer
