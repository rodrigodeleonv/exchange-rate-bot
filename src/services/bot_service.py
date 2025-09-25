"""Bot service layer - contains business logic and response formatting."""

import logging
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.database import get_session
from src.repositories import NotificationSubscriptionRepository
from src.services.exchange_rate_service import ExchangeRateService, Rates
from src.utils.tz_utils import get_tz

logger = logging.getLogger(__name__)


class BotService:
    """Service layer for bot business logic and response formatting."""

    def __init__(self, exchange_service: ExchangeRateService) -> None:
        """Initialize bot service with dependencies and template environment."""
        self.exchange_service = exchange_service

        # Templates directory (root-level 'templates/')
        self._templates_dir = Path("templates")
        self._messages_dir = self._templates_dir / "messages"
        self._config_dir = self._templates_dir / "config"

        # Initialize Jinja2 environment
        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )


    def _render(self, template_name: str, **context: object) -> str:
        """Render a template from templates/messages with shared context."""
        try:
            template = self._env.get_template(f"messages/{template_name}")
            # Inject common context
            context.update({
                "bank_display_names": {
                    "banguat": "🏛️ Banguat (Oficial)",
                    "banrural": "🏦 Banrural (Banca Virtual)",
                    "nexa": "🏪 Nexa Banco (Compra)",
                }
            })
            return template.render(**context).strip()
        except Exception as e:
            logger.error("Error rendering template %s: %s", template_name, e)
            return f"❌ Error al generar mensaje: {template_name}"

    async def get_start_message(self, user_name: str) -> str:
        """Generate start message for user."""
        return self._render("start.html", user_name=user_name)

    async def get_help_message(self) -> str:
        """Generate help message with available commands."""
        return self._render("help.html")

    async def get_ping_message(self) -> str:
        """Generate ping response message."""
        return self._render("ping.html")

    async def get_loading_message(self) -> str:
        """Generate loading message for rate requests."""
        return self._render("loading.html")

    async def get_rates_response(self) -> str:
        """Get formatted exchange rates response."""
        try:
            rates = await self.exchange_service.get_all_rates()
            # Compute best bank here (business logic belongs in service)
            valid_rates = {k: v for k, v in rates.items() if v is not None}
            best_bank = max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
            return self._render("rates.html", rates=rates, best_bank=best_bank)
        except Exception as e:
            logger.error("Error fetching rates: %s", e)
            return self._render("errors.html", error_type="rates_error")

    async def subscribe_user(self, chat_id: int) -> str:
        """Subscribe user to daily notifications."""
        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)
            await repo.create_subscription(chat_id=chat_id)
        logger.info("User %s subscribed to notifications", chat_id)
        return self._render("subscription.html", action="subscribe_success")

    async def unsubscribe_user(self, chat_id: int) -> str:
        """Unsubscribe user from daily notifications."""
        async with get_session() as session:
            repo = NotificationSubscriptionRepository(session)
            success = await repo.delete_subscription(chat_id=chat_id)
        if success:
            logger.info("User %s unsubscribed from notifications", chat_id)
            return self._render("subscription.html", action="unsubscribe_success")
        else:
            logger.info("User %s was not subscribed to notifications", chat_id)
            return self._render("subscription.html", action="unsubscribe_not_found")

    async def format_daily_notification(self, rates: Rates) -> str:
        """Format daily notification message."""
        current_time = datetime.now(get_tz()).strftime("%d/%m/%Y %H:%M")
        valid_rates = {k: v for k, v in rates.items() if v is not None}
        best_bank = max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
        return self._render(
            "daily_notification.html",
            rates=rates,
            best_bank=best_bank,
            date_time=current_time,
        )
