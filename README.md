# 🤖 Exchange Rate Bot

A Telegram bot that provides real-time USD/GTQ exchange rates from multiple banks with webhook support and scheduled daily notifications.

## ✨ Features

- **📊 Real-time Exchange Rates**: Fetch current USD/GTQ rates from multiple banks
- **🔔 Daily Notifications**: Automated notifications at configurable time
- **🏦 Multiple Sources**: official bank and commercial banks
- **⚡ Fast & Async**: Built with modern async Python for high performance
- **🐳 Docker Ready**: Easy deployment with Docker Compose
- **🔒 Secure**: Bearer token authentication for admin endpoints
- **📝 Template System**: Jinja2-based message templates with HTML support

## 🤖 Bot Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show available commands and usage
- `/ping` - Test bot responsiveness
- `/rates` - Get current exchange rates from all banks
- `/subscribe` - Subscribe to daily rate notifications
- `/unsubscribe` - Unsubscribe from notifications

## 🚀 Deployment

### Prerequisites

- **Docker & Docker Compose** (20.10+)
- **Telegram Bot Token** from [@BotFather](https://t.me/botfather)
- **Domain with SSL** (for webhook mode)

### Quick Start

1. **Clone and configure:**
   ```bash
   git clone <repository-url>
   cd exchange-rate-bot
   cp example.env .env
   # Edit .env with your bot token and configuration
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh
   ```


### Environment Configuration

Edit `.env` with your settings:


### Docker Compose Services

The bot runs two services:

**webhook** - FastAPI server for real-time bot interactions
```yaml
webhook:
  command: python main.py webhook
  ports:
    - "23456:23456"
  restart: unless-stopped
```

**scheduler** - APScheduler for daily notifications
```yaml
scheduler:
  command: python -m apps.scheduler_app
  restart: unless-stopped
```

### Volume Structure

```
.volumes/
├── data/                    # Database files
│   └── exchange_bot.db     # SQLite database
└── logs/                    # Application logs
    ├── app.log             # General logs
    └── errors.log          # Error logs
```

### Webhook Setup

1. Configure Reverse Proxy

2. Set Telegram Webhook (Automatically registered in the bot)

### Database Migrations

Migrations run **automatically** when containers start via `docker-entrypoint.sh`.

For manual management:
```bash
# Enter container
docker compose exec webhook bash

# Run migrations
alembic upgrade head

# Check current revision
alembic current
```

### Monitoring & Health Checks

```bash
# Application health
# curl /health

# Container status
docker compose ps
docker compose logs -f

# View specific service logs
docker compose logs -f webhook
docker compose logs -f scheduler
```

### Troubleshooting

**Bot not responding:**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Delete and reset webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

**Port conflicts:**
```bash
# Find process using port
lsof -i :23456

# Kill process
kill -9 <PID>
```

**Permission issues:**
```bash
# Fix volume permissions
sudo chown -R $(id -u):$(id -g) .volumes/
chmod -R 755 .volumes/
```

---

## 👨‍💻 Development

### Prerequisites

- **Python 3.13+**
- **uv** (Python package manager)
- **Docker & Docker Compose** (for deployment)

### Local Setup

1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

4. **Set up database:**
   ```bash
   uv run alembic upgrade head
   ```

### Running Locally

**Webhook Mode:**
```bash
# Kill existing processes first
pkill -f "python main.py"

# Start webhook server
uv run python main.py
```

**Scheduler Mode:**
```bash
# Kill existing processes first
pkill -f "python -m apps.scheduler_app"

# Start scheduler
uv run python -m apps.scheduler_app

# Test scheduler (run once)
uv run python -m apps.scheduler_app --run-once
```

### Code Quality

```bash
# Check code style
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix

# Format code
uv run ruff format

# Type check
uv run pyright

# Run all checks
uv run ruff check && uv run ruff format && uv run pyright
```

### Webhook Testing

Simplify webhook testing with temporal URLs from [Pinggy](https://pinggy.io/), you must update the webhook URL in the bot configuration.

```bash
ssh -p 443 -R0:127.0.0.1:8000 qr@free.pinggy.io
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_utils/test_url_utils.py

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run with verbose output
uv run pytest -v
```

### Database Management

**Create Migration:**
```bash
# Auto-generate from model changes
uv run alembic revision --autogenerate -m "Add new field"

# Create empty migration
uv run alembic revision -m "Add custom index"
```

**Apply Migrations:**
```bash
# Apply all pending
uv run alembic upgrade head

# Apply specific migration
uv run alembic upgrade <revision_id>

# Apply next migration only
uv run alembic upgrade +1
```

**Revert Migrations:**
```bash
# Revert last migration
uv run alembic downgrade -1

# Revert to specific migration
uv run alembic downgrade <revision_id>

# Revert all
uv run alembic downgrade base
```

**Migration Status:**
```bash
# View current migration
uv run alembic current

# View history
uv run alembic history

# Check pending
uv run alembic show head
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# ✅ Good: Use %s interpolation
logger.info("Processing %s items for user %s", count, user_id)

# ❌ Avoid: f-strings (formats even when logging disabled)
logger.info(f"Processing {count} items for user {user_id}")

# Log levels
logger.debug("Detailed debug information")
logger.info("Business event occurred")
logger.warning("Something unexpected happened")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical system failure")
```

### Adding New Features

#### Add New Scraper

```python
# src/scrapers/new_bank_scraper.py
from src.scrapers.base_scraper import ExchangeRateScraper

class NewBankScraper(ExchangeRateScraper):
    """Scraper for New Bank exchange rates."""

    def __init__(self):
        self.base_url = "https://newbank.com/api/rates"

    async def get_exchange_rate(self) -> float:
        """Fetch USD/GTQ exchange rate."""
        # Implementation here
        pass
```

Register in `src/services/exchange_rate_service.py`:
```python
from src.scrapers.new_bank_scraper import NewBankScraper

class ExchangeRateService:
    def __init__(self):
        self.scrapers = {
            "banguat": BanguatClient(),
            "banrural": BanruralScraper(),
            "nexa": NexaScraper(),
            "newbank": NewBankScraper(),  # Add here
        }
```

#### Add New Bot Command

Add handler in `src/handlers/bot_handlers.py`:
```python
async def new_command_handler(self, message: Message):
    """Handle /newcommand."""
    result = await self.bot_service.handle_new_command(message.from_user.id)
    await message.answer(result)
```

Register in `src/infrastructure/telegram_bot_webhook.py`:
```python
self.dp.message.register(
    self.handlers.new_command_handler,
    Command("newcommand")
)
```

Add business logic in `src/services/bot_service.py`:
```python
async def handle_new_command(self, user_id: int) -> str:
    """Handle new command logic."""
    return self.template_engine.render("new_command.html", {})
```

Create template in `templates/messages/new_command.html`:
```html
<b>New Command Response</b>

This is the response for the new command.
```

### Code Style Guidelines

**Naming Conventions:**
- Variables & Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Import Order:**
```python
# Standard library
import logging
from datetime import datetime

# Third-party
import aiohttp
from aiogram import Bot

# Local
from src.config import get_config
from src.services.bot_service import BotService
```

---

## 🏗️ Architecture

The project follows **Clean Architecture** principles with clear separation of concerns across multiple layers.

### Project Structure

```
exchange-rate-bot/
├── apps/                    # 📱 Application Layer
│   ├── webhook_app.py      # FastAPI webhook server
│   └── scheduler_app.py    # APScheduler for notifications
│
├── src/                     # 🎯 Core Application
│   ├── handlers/           # Request handlers (controllers)
│   ├── services/           # Business logic
│   ├── repositories/       # Data access abstraction
│   ├── infrastructure/     # External services (Telegram, HTTP)
│   ├── scrapers/           # Bank data scrapers
│   ├── database/           # ORM models & session management
│   └── utils/              # Pure utility functions
│
├── templates/              # 📝 Jinja2 Message Templates
├── alembic/                # 🔄 Database Migrations
├── tests/                  # 🧪 Test Suite
└── .volumes/               # 💾 Persistent Data (Docker)
```

### Architecture Layers

**1. Application Layer (`apps/`)**
- Entry points for different application modes
- Framework integration (FastAPI, APScheduler)
- Dependency wiring and composition root
- Signal handling and lifecycle management

**2. Handler Layer (`src/handlers/`)**
- Telegram command routing
- Minimal validation
- Delegates to service layer
- Returns formatted responses

**3. Service Layer (`src/services/`)**
- Business logic and orchestration
- Data transformation
- Error handling and logging
- Coordinates repositories and scrapers

**4. Repository Layer (`src/repositories/`)**
- Data access abstraction
- Database operations encapsulation
- Uses Protocol classes for interfaces

**5. Infrastructure Layer (`src/infrastructure/`)**
- External service integration (Telegram API)
- HTTP client management
- Rate limiting
- Webhook management

**6. Scraper Layer (`src/scrapers/`)**
- External data source integration
- Fetches exchange rates from banks
- Parse and normalize data
- Strategy pattern implementation

**7. Database Layer (`src/database/`)**
- ORM models (User, Subscription, ExchangeRate)
- Async session management
- SQLAlchemy configuration

### Design Principles

**SOLID Principles:**
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes substitutable for base classes
- **Interface Segregation**: Clients don't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

**Design Patterns:**
- **Repository Pattern**: Data access abstraction using Protocol classes
- **Service Layer**: Business logic orchestration
- **Strategy Pattern**: Different exchange rate providers (scrapers)
- **Template Method**: Message rendering with Jinja2
- **Dependency Injection**: Loose coupling throughout

### Data Flow

**Webhook Request:**
```
Telegram → FastAPI → BotHandlers → BotService
                                        ↓
                            ExchangeRateService + Repositories
                                        ↓
                                  Scrapers + Database
                                        ↓
                              TemplateEngine → Response
```

**Scheduled Notification:**
```
APScheduler → DailyNotificationService
                        ↓
          ExchangeRateService + Repository
                        ↓
                  Scrapers + Database
                        ↓
              BotService → TelegramNotification
```

### Technology Stack

**Core:**
- Python 3.13+ with async/await
- aiogram 3.15+ (Telegram bot framework)
- FastAPI (Web framework)
- SQLAlchemy 2.0+ (Async ORM)

**Infrastructure:**
- aiohttp (Async HTTP client)
- APScheduler (Job scheduling)
- Alembic (Database migrations)
- Jinja2 (Template engine)

**Data Sources:**
- SOAP API
- REST API
- Web Scraping

**Development:**
- uv (Package manager)
- ruff (Linting and formatting)
- pyright (Type checking)
- pytest (Testing framework)

### Why These Choices?

**Protocol Classes over ABC:**
- Structural typing (duck typing)
- Less coupling
- Better for testing and mocking
- Superior type checking support

**Jinja2 for Templates:**
- Separates content from code
- HTML native (Telegram HTML tags)
- Powerful (loops, conditionals, filters)
- Easy for non-programmers to edit

**Repository Pattern:**
- Abstracts database implementation
- Easy to test (mock data access)
- Flexible (can swap databases)
- Single Responsibility

**Service Layer:**
- Centralizes business logic
- Reusable across handlers/apps
- Testable independently
- Orchestrates multiple repositories

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow code style** (run `uv run ruff format`)
4. **Add tests** for new features
5. **Update documentation** as needed
6. **Commit changes** (`git commit -m 'feat: add amazing feature'`)
7. **Push to branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

Commit Convention: use conventional commits

## 🙏 Acknowledgments

- **aiogram** - Excellent Telegram bot framework
- **FastAPI** - Modern web framework


## 🗺️ Roadmap

- [ ] Historical rate tracking and charts
- [ ] Rate change alerts
- [ ] User preferences and customization
- [ ] Internationalization (Spanish/English)
- [ ] GraphQL API for rate queries
- [ ] Redis caching layer
- [ ] Prometheus metrics
