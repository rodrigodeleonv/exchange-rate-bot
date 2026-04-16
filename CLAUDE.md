# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use `uv run` as the project manager.

```bash
# Run the webhook server (main entry point)
uv run python main.py

# Run the webhook server directly
uv run python -m apps.webhook_app

# Run the scheduler (daily notifications at 8:00 AM Guatemala time)
uv run python -m apps.scheduler_app

# Test scheduler by running once immediately
uv run python -m apps.scheduler_app --run-once

# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking
uv run pyright

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/path/to/test_file.py

# Database migrations
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "Description"
uv run alembic current
```

## Environment Setup

Copy `example.env` to `.env` and fill in:
- `TELEGRAM_BOT_TOKEN` — from @BotFather
- `SERVER_WEBHOOK_BASE_URL` — public HTTPS URL for the webhook
- `SERVER_WEBHOOK_SECRET_TOKEN` — generate with `openssl rand -hex 32`
- `DATABASE_URL` — SQLite (`sqlite+aiosqlite:///./exchange_bot.db`) or PostgreSQL

## Architecture

Clean Architecture with two independent entry points:

**`apps/webhook_app.py`** — FastAPI server that receives Telegram webhook POSTs at `/webhook`, validates the `X-Telegram-Bot-Api-Secret-Token` header, and feeds updates to the aiogram `Dispatcher`.

**`apps/scheduler_app.py`** — APScheduler process that fires daily at 8:00 AM (`SERVER_TIMEZONE`) and sends rate notifications to all subscribed users.

The two apps are deployed as separate Docker services and share the same SQLite database volume.

### Layer Flow

```
Telegram → POST /webhook → WebhookApp → TelegramBotWebhook → Dispatcher
                                                              → BotHandlers
                                                              → BotService
                                                              → ExchangeRateService → [scrapers]
                                                              → BotService (Jinja2 templates)
                                                              → aiogram reply

APScheduler → DailyNotificationService → ExchangeRateService → [scrapers]
                                       → BotService (format)
                                       → TelegramNotification (send to all subscribers)
```

### Key Components

- **`src/config.py`** — Pydantic-Settings `Config` class; uses `_` as nested delimiter so `TELEGRAM_BOT_TOKEN` maps to `config.telegram.bot_token`. Loaded once via `get_config()` with `@lru_cache`.
- **`src/scrapers/`** — Each scraper implements the `ScraperBase` protocol (`get_usd_buy_rate() -> float | None`). `ExchangeRateService` runs all scrapers concurrently with `asyncio.gather`. Banguat is marked `REFERENCE_ONLY_BANKS` — shown in output but excluded from "best rate" selection.
- **`src/services/bot_service.py`** — All Telegram message text lives in Jinja2 HTML templates under `templates/messages/`. `BotService._render()` injects shared context (bank display names) automatically. Messages are sent with `ParseMode.HTML`.
- **`src/database/`** — Async SQLAlchemy with aiosqlite. Models: `Institution`, `ExchangeRate`, `TelegramNotificationSubscription`. Migrations via Alembic (`alembic/versions/`). Migrations run automatically in Docker via `docker-entrypoint.sh`.
- **`src/repositories/notification_subscription.py`** — Data access for subscriber management (create/delete/list subscriptions).
- **`src/infrastructure/telegram_bot_client.py`** — Base aiogram `Bot` setup. `TelegramBotWebhook` extends it and adds the `Dispatcher` + handler wiring.

### Adding a New Bank Scraper

1. Create `src/scrapers/<bank>_scraper.py` implementing `get_usd_buy_rate() -> float | None`
2. Add it to the `self.scrapers` tuple in `ExchangeRateService.__init__`
3. Add a display name entry in `BotService._render()` → `bank_display_names` dict
4. Update the Jinja2 templates if needed

### Deployment

```bash
# Always clean-build before deploying
docker system prune -f
docker compose build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)
docker compose up -d

# Or use the automated script
./deploy.sh
```

Persistent data lives in `.volumes/data/exchange_bot.db` and `.volumes/logs/`.
