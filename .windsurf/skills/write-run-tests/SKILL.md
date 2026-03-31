---
name: write-run-tests
description: Use when writing, running, or modifying tests for the Exchange Rate Bot. Provides test conventions, structure, mocking patterns, and concrete examples.
---

# Testing Guide — Exchange Rate Bot

## Running tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific file
uv run pytest tests/test_exchange_rate_service.py

# Run a specific test
uv run pytest tests/test_exchange_rate_service.py::test_get_all_rates_success

# Run with coverage (if pytest-cov is installed)
uv run pytest --cov=src
```

## Test configuration

Already configured in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = ["-ra", "--strict-markers"]
asyncio_mode = "auto"
```

Key: `asyncio_mode = "auto"` means **all async test functions are automatically detected** — no need for `@pytest.mark.asyncio` decorators.

## Test structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_exchange_rate_service.py
├── test_bot_service.py
├── scrapers/
│   ├── test_banguat_client.py
│   ├── test_banrural_scraper.py
│   └── test_nexa_scraper.py
└── repositories/
    └── test_notification_subscription.py
```

## Conventions

- **File naming:** `test_<module_name>.py`
- **Function naming:** `test_<what_it_does>` — use plain functions, not classes, unless grouping is needed
- **Always mock external calls:** Never hit real APIs or databases in unit tests
- **Use `unittest.mock`** for mocking (`patch`, `AsyncMock`, `MagicMock`)
- **Test one behavior per test function**
- **Use descriptive assertion messages** when the failure reason isn't obvious

## Mocking patterns for this project

### Mocking an async scraper (aiohttp)

Scrapers use `aiohttp.ClientSession`. Mock at the session level:

```python
from unittest.mock import AsyncMock, MagicMock, patch

from src.scrapers.banrural_scraper import BanruralScraper


async def test_banrural_scraper_returns_rate():
    """Test that BanruralScraper parses the API JSON correctly."""
    mock_json = {
        "compra_dolares_docto_bv": "7.59",
        "venta_dolares_docto_bv": "7.77",
    }

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_json)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        scraper = BanruralScraper()
        rate = await scraper.get_usd_buy_rate()

    assert rate == 7.59


async def test_banrural_scraper_returns_none_on_error():
    """Test that BanruralScraper returns None when API fails."""
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.get = MagicMock(side_effect=Exception("Connection error"))

    with patch("aiohttp.ClientSession", return_value=mock_session):
        scraper = BanruralScraper()
        rate = await scraper.get_usd_buy_rate()

    assert rate is None
```

### Mocking ExchangeRateService (for BotService tests)

```python
from unittest.mock import AsyncMock

from src.services.bot_service import BotService
from src.services.exchange_rate_service import ExchangeRateService


async def test_get_rates_response_formats_correctly():
    """Test that rates response includes all banks."""
    mock_exchange = AsyncMock(spec=ExchangeRateService)
    mock_exchange.get_all_rates.return_value = {
        "banguat": 7.75,
        "banrural": 7.59,
        "nexa": 7.60,
    }

    service = BotService(exchange_service=mock_exchange)
    response = await service.get_rates_response()

    assert "7.75" in response
    assert "7.59" in response
```

### Mocking database (for repository tests)

Use an in-memory SQLite database:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base


@pytest.fixture
async def db_session():
    """Create an in-memory database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()
```

## What to test first (priority)

1. **Scrapers** — They break most often (external APIs change). Test parsing logic with mocked responses.
2. **ExchangeRateService** — Test concurrent aggregation, error handling per scraper.
3. **BotService** — Test message formatting, best bank logic.
4. **Repositories** — Test CRUD operations with in-memory DB.
