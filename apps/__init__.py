"""Applications layer - Entry points and composition roots."""

from apps.daily_notifier_app import DailyNotifierApp
from apps.webhook_app import WebhookApp

__all__ = [
    "WebhookApp",
    "DailyNotifierApp",
]
