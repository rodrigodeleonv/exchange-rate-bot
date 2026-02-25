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

Simplify webhook testing with temporary URLs from [Pinggy](https://pinggy.io/), you must update the webhook URL in the bot configuration.

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
@self.dp.message(Command("newcommand"))
async def new_command_handler(message: Message) -> None:
    """Handle /newcommand."""
    # Format response using MessageFormatter
    response = self.message_formatter.format_new_command()
    await message.answer(response, parse_mode=ParseMode.HTML)
```

Add method in `src/services/message_formatter.py`:
```python
def format_new_command(self) -> str:
    """Format new command response."""
    return render_template("new_command.html")
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
│   ├── bot/                # 🤖 Telegram bot (unified)
│   │   └── telegram_bot.py # Webhook + Polling + Notifications
│   ├── handlers/           # 🎮 Request handlers (controllers)
│   │   └── bot_handlers.py # Command routing
│   ├── services/           # 💼 Business logic
│   │   ├── exchange_rate_service.py   # Rate fetching
│   │   ├── message_formatter.py       # Message formatting
│   │   └── subscription_service.py    # Subscription management
│   ├── repositories/       # 💾 Data access
│   │   └── notification_subscription.py
│   ├── scrapers/           # 🏦 Bank data scrapers
│   │   ├── banguat_client.py
│   │   ├── banrural_scraper.py
│   │   └── nexa_scraper.py
│   ├── database/           # 🗄️ ORM & session management
│   │   ├── models.py
│   │   └── session.py
│   └── utils/              # 🔧 Utilities
│       ├── templates.py    # Jinja2 rendering
│       ├── tz_utils.py
│       └── url_utils.py
│
├── templates/              # 📝 Jinja2 Message Templates
├── alembic/                # 🔄 Database Migrations
├── tests/                  # 🧪 Test Suite
└── .volumes/               # 💾 Persistent Data (Docker)
```

### Architecture Layers

**1. Application Layer (`apps/`)**
- Entry points for webhook and scheduler modes
- Framework integration (FastAPI, APScheduler)
- Dependency injection and composition root
- Lifecycle management

**2. Bot Layer (`src/bot/`)**
- Unified Telegram bot client
- Webhook and polling support
- Message broadcasting
- Bot lifecycle management

**3. Handler Layer (`src/handlers/`)**
- Command routing (/start, /rates, /subscribe, etc.)
- Minimal validation
- Delegates to services
- Returns formatted responses

**4. Service Layer (`src/services/`)**
- **ExchangeRateService**: Fetches rates from all banks
- **MessageFormatter**: Formats messages using templates
- **SubscriptionService**: Manages user subscriptions
- Pure business logic, no framework dependencies

**5. Repository Layer (`src/repositories/`)**
- Simple data access (no Protocol overhead)
- Manages own database sessions
- CRUD operations for subscriptions

**6. Scraper Layer (`src/scrapers/`)**
- Bank-specific rate fetching
- Strategy pattern for different sources
- Async HTTP operations

**7. Database Layer (`src/database/`)**
- SQLAlchemy models
- Simple session management
- Async operations

### Design Principles

**SOLID Principles:**
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes substitutable for base classes
- **Interface Segregation**: Clients don't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

**Design Patterns:**
- **Repository Pattern**: Simple data access (no Protocol overhead)
- **Service Layer**: Business logic with single responsibilities
- **Strategy Pattern**: Different exchange rate providers (scrapers)
- **Composition over Inheritance**: Services composed, not inherited
- **Dependency Injection**: Constructor injection throughout

### Data Flow

**Webhook Request:**
```
Telegram → FastAPI → BotHandlers → MessageFormatter + ExchangeRateService
                                              ↓
                                        Scrapers
                                              ↓
                                        Response
```

**Scheduled Notification:**
```
APScheduler → Scheduler → ExchangeRateService + MessageFormatter
                                    ↓
                              Scrapers + Repository
                                    ↓
                          TelegramBot.broadcast()
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

**Simplified Architecture (2024 Refactoring):**
- Removed unnecessary abstractions (Protocols for single implementations)
- Consolidated Telegram classes (3 → 1)
- Direct service usage instead of orchestration layers
- 40% less code while maintaining SOLID principles

**Jinja2 for Templates:**
- Separates content from code
- HTML native (Telegram HTML tags)
- Powerful (loops, conditionals, filters)
- Easy for non-programmers to edit

**Simple Repository Pattern:**
- No Protocol overhead for single implementations
- Manages own database sessions
- Easy to test and understand
- Single Responsibility

**Focused Services:**
- Each service has one clear responsibility
- MessageFormatter: Only formatting
- SubscriptionService: Only subscriptions
- ExchangeRateService: Only rate fetching
- Testable independently without complex mocks

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
