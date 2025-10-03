"""Bot service layer - contains business logic and orchestration."""

import logging
from datetime import datetime

from src.presentation import TemplateRenderer
from src.repositories import NotificationSubscriptionRepositoryBase
from src.services.exchange_rate_service import ExchangeRateService, Rates
from src.utils.tz_utils import get_tz

logger = logging.getLogger(__name__)


class BotService:
    """Service layer for bot business logic and orchestration.

    This service coordinates between different layers:
    - ExchangeRateService for fetching rates
    - NotificationSubscriptionRepository for managing subscriptions
    - TemplateRenderer for formatting messages
    """

    def __init__(
        self,
        exchange_service: ExchangeRateService,
        subscription_repo: NotificationSubscriptionRepositoryBase,
        template_renderer: TemplateRenderer,
    ) -> None:
        """Initialize bot service with dependencies.

        Args:
            exchange_service: Service for fetching exchange rates
            subscription_repo: Repository for notification subscriptions
            template_renderer: Renderer for HTML templates
        """
        self.exchange_service = exchange_service
        self.subscription_repo = subscription_repo
        self.template_renderer = template_renderer

        # Bank display names for templates that show exchange rates
        self._bank_display_names = {
            "banguat": "🏛️ Banguat (Oficial)",
            "banrural": "🏦 Banrural (Banca Virtual)",
            "nexa": "🏪 Nexa Banco (Compra)",
        }

    async def get_start_message(self, user_name: str) -> str:
        """Generate start message for user."""
        return self.template_renderer.render("start.html", user_name=user_name)

    async def get_help_message(self) -> str:
        """Generate help message with available commands."""
        return self.template_renderer.render("help.html")

    async def get_ping_message(self) -> str:
        """Generate ping response message."""
        return self.template_renderer.render("ping.html")

    async def get_loading_message(self) -> str:
        """Generate loading message for rate requests."""
        return self.template_renderer.render("loading.html")

    async def get_rates_response(self) -> str:
        """Get formatted exchange rates response."""
        try:
            rates = await self.exchange_service.get_all_rates()
            # Compute best bank here (business logic belongs in service)
            valid_rates = {k: v for k, v in rates.items() if v is not None}
            best_bank = max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
            return self.template_renderer.render(
                "rates.html",
                rates=rates,
                best_bank=best_bank,
                bank_display_names=self._bank_display_names,
            )
        except Exception as e:
            logger.error("Error fetching rates: %s", e)
            return "❌ Error al obtener las tasas de cambio. Intenta más tarde."

    async def subscribe_user(self, chat_id: int) -> str:
        """Subscribe user to daily notifications."""
        await self.subscription_repo.create_subscription(chat_id=chat_id)
        logger.info("User %s subscribed to notifications", chat_id)
        return self.template_renderer.render("subscription.html", action="subscribe_success")

    async def unsubscribe_user(self, chat_id: int) -> str:
        """Unsubscribe user from daily notifications."""
        success = await self.subscription_repo.delete_subscription(chat_id=chat_id)
        if success:
            logger.info("User %s unsubscribed from notifications", chat_id)
            return self.template_renderer.render("subscription.html", action="unsubscribe_success")
        else:
            logger.info("User %s was not subscribed to notifications", chat_id)
            return self.template_renderer.render(
                "subscription.html", action="unsubscribe_not_found"
            )

    async def format_daily_notification(self, rates: Rates) -> str:
        """Format daily notification message."""
        current_time = datetime.now(get_tz()).strftime("%d/%m/%Y %H:%M")
        valid_rates = {k: v for k, v in rates.items() if v is not None}
        best_bank = max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
        return self.template_renderer.render(
            "daily_notification.html",
            rates=rates,
            best_bank=best_bank,
            date_time=current_time,
            bank_display_names=self._bank_display_names,
        )
