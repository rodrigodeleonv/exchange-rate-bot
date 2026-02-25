"""Message formatting service for bot responses."""

import logging
from datetime import datetime

from src.services.exchange_rate_service import Rates
from src.utils import render_template
from src.utils.tz_utils import get_tz

logger = logging.getLogger(__name__)


class MessageFormatter:
    """Service for formatting bot messages using templates."""

    def format_start_message(self, user_name: str) -> str:
        """Generate start message for user."""
        return render_template("start.html", user_name=user_name)

    def format_help_message(self) -> str:
        """Generate help message with available commands."""
        return render_template("help.html")

    def format_ping_message(self) -> str:
        """Generate ping response message."""
        return render_template("ping.html")

    def format_loading_message(self) -> str:
        """Generate loading message for rate requests."""
        return render_template("loading.html")

    def format_rates_message(self, rates: Rates) -> str:
        """Format exchange rates response.

        Args:
            rates: Dictionary of bank names to exchange rates

        Returns:
            Formatted HTML message
        """
        try:
            valid_rates = {k: v for k, v in rates.items() if v is not None}
            best_bank = max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
            return render_template("rates.html", rates=rates, best_bank=best_bank)
        except Exception as e:
            logger.error("Error formatting rates: %s", e)
            return "❌ Error al obtener las tasas de cambio. Intenta más tarde."

    def format_subscription_success(self) -> str:
        """Format subscription success message."""
        return render_template("subscription.html", action="subscribe_success")

    def format_unsubscription_success(self) -> str:
        """Format unsubscription success message."""
        return render_template("subscription.html", action="unsubscribe_success")

    def format_unsubscription_not_found(self) -> str:
        """Format unsubscription not found message."""
        return render_template("subscription.html", action="unsubscribe_not_found")

    def format_daily_notification(self, rates: Rates) -> str:
        """Format daily notification message.

        Args:
            rates: Dictionary of bank names to exchange rates

        Returns:
            Formatted HTML message
        """
        current_time = datetime.now(get_tz()).strftime("%d/%m/%Y %H:%M")
        valid_rates = {k: v for k, v in rates.items() if v is not None}
        best_bank = max(valid_rates, key=lambda k: valid_rates[k]) if valid_rates else None
        return render_template(
            "daily_notification.html",
            rates=rates,
            best_bank=best_bank,
            date_time=current_time,
        )
