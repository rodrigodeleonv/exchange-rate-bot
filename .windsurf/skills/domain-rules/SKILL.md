---
name: domain-rules
description: Use when modifying, extending, or understanding the Exchange Rate Bot codebase. Provides project structure, architecture decisions, business domain context, and conventions.
---

# Exchange Rate Bot — Domain Knowledge

## What this project does

Telegram bot that fetches **USD/GTQ buy rates** from Guatemalan banks and sends them to users on demand (`/rates`) or via daily scheduled notifications (`/subscribe`).

## Supported banks

| Bank | Source type | Module | Notes |
|------|-----------|--------|-------|
| **Banguat** (Banco de Guatemala) | SOAP API | `src/scrapers/banguat_client.py` | Official reference rate. Uses XML SOAP template in `src/resources/soap_templates/` |
| **Banrural** | Internal JSON API | `src/scrapers/banrural_scraper.py` | Requires `Referer`, `X-Requested-With`, `User-Agent` headers. Returns Virtual Banking rate (`compra_dolares_docto_bv`) |
| **Nexa Banco** | Web scraping (HTML) | `src/scrapers/nexa_scraper.py` | Parses HTML with BeautifulSoup + lxml |

All scrapers implement the `ScraperBase` Protocol defined in `src/scrapers/base_scraper.py`:
```python
class ScraperBase(Protocol):
    async def get_usd_buy_rate(self) -> float | None: ...
```

## Project structure

```
apps/                          # Entry points
├── webhook_app.py             # FastAPI server (Telegram webhook)
└── scheduler_app.py           # APScheduler (daily notifications)

src/
├── config.py                  # Pydantic Settings (env vars with nested delimiter)
├── scrapers/                  # Data fetching (one module per bank)
│   └── base_scraper.py        # ScraperBase Protocol
├── services/                  # Business logic
│   ├── exchange_rate_service.py  # Aggregates all scrapers concurrently
│   ├── bot_service.py            # Message formatting (Jinja2 templates)
│   └── daily_notification_service.py  # Sends to subscribers
├── handlers/bot_handlers.py   # Aiogram command handlers
├── infrastructure/            # Telegram client wrappers
├── repositories/              # SQLAlchemy data access
├── database/                  # Models, session, base
└── utils/                     # Timezone, URL helpers

templates/messages/            # Jinja2 HTML templates for bot messages
alembic/                       # Database migrations
```

## Key conventions

- **Adding a new bank:** Create a new scraper in `src/scrapers/` that satisfies `ScraperBase` Protocol, then add it to `ExchangeRateService.__init__` scrapers tuple. No other changes needed — the service auto-discovers scraper names from class names.
- **Bot messages:** All user-facing text lives in `templates/messages/*.html` as Jinja2 templates. The `BotService._render()` method injects common context like `bank_display_names`.
- **Configuration:** Uses `pydantic-settings` with `env_nested_delimiter="_"`. Env vars map to nested models (e.g., `TELEGRAM_BOT_TOKEN` → `Config.telegram.bot_token`). See `example.env` for all variables.
- **Database:** SQLAlchemy async with aiosqlite. Models in `src/database/models.py`. Migrations via Alembic (`uv run alembic revision --autogenerate -m "description"`).
- **HTTP clients:** Use `aiohttp` for scraping (session-per-request in scrapers). Telegram uses `aiogram` built-in client.

## Architecture principles (keep it simple)

- Favor **readability over abstraction**. Don't add layers unless there's a clear reason.
- The Protocol pattern for scrapers is intentional — it keeps scrapers independent with zero inheritance.
- Avoid unnecessary design patterns. The current structure (scrapers → service → handler) is sufficient.
- When in doubt, prefer a simple function over a new class.

## Logging, monitoring and messages

- Never user print statements. Use logging instead.
- Use structured logging with context fields for better observability.

## Async code

- Use async/await pattern consistently when possible.
- Use sync code when async is not needed or when it is not compatible with the current context. For heavy tasks, consider using a thread pool.

## Code Quality, Formatting and Linter

- Use ruff for linting and formatting
- Use pyright for static type checking
- Run quality checks with `uv run ruff check` and `uv run pyright`
- Fix formatting with `uv run ruff format`
