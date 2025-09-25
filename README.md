# 🤖 Exchange Rate Bot

A Telegram bot that provides real-time USD/GTQ exchange rates from multiple banks with webhook support and scheduled notifications.

## 🚀 Deployment

### Prerequisites

- Docker & Docker Compose
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Domain with SSL certificate (for webhook mode)

### Automated Deployment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd exchange-rate-bot
   ```
1
2. **Configure environment variables:**
   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

3. **Deploy with automated script:**
   ```bash
   ./deploy.sh
   ```

   The deploy script automatically:
   - ✅ Creates volume structure (`.volumes/`)
   - ✅ Configures correct permissions
   - ✅ Detects current user UID/GID for cross-platform compatibility
   - ✅ Shows deployment status and logs

4. Always clean build when deploying. Use:
   ```bash
   docker system prune -f
   ```

### Manual Docker Commands

If you prefer manual Docker commands:

```bash
# Build with current user UID/GID
docker compose build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)

# Deploy services
docker compose up -d

# View logs
docker compose logs -f
```


#### Common Issues

1. **Bot not responding:**
   ```bash
   # Check if webhook is set correctly
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

   # Delete webhook if needed
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
   ```

2. **Database connection errors:**
   ```bash
   # Check database status
   uv run alembic current

   # Apply pending migrations
   uv run alembic upgrade head
   ```

3. **Port conflicts:**
   ```bash
   # Kill existing processes
   pkill -f "python main.py"

   # Check port usage
   lsof -i :23456
   ```

#### Health Checks

- **Bot health:** `curl http://localhost:23456/health`
- **Webhook status:** `curl http://localhost:23456/webhook` (should return 405)
- **Set webhook:** `curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" -d "url=https://<YOUR_DOMAIN>/webhook"`
- **Database:** `uv run alembic current`

## 🚀 Quick Start

### Run the Bot
```bash
# Start webhook server (default)
python main.py

# Start scheduler
python -m apps.scheduler_app

# Test scheduler (run once)
python -m apps.scheduler_app --run-once

# Show help
python main.py help
```

### Available Applications
- **🌐 Webhook Server**: FastAPI-based real-time bot interactions
- **⏰ Scheduler**: Automated daily notifications at 8:00 AM Guatemala time

## 🏗️ Architecture

Clean Architecture with layered design:

```
├── apps/                    # 📱 Applications Layer (Entry Points)
├── src/
│   ├── infrastructure/      # 🔧 Infrastructure (Telegram, HTTP)
│   ├── handlers/           # 🎯 Presentation (Bot Commands)
│   ├── services/           # ⚙️ Business Logic
│   ├── repositories/       # 📦 Data Access
│   └── database/          # 🗄️ Persistence
```

### Volume Structure

The deployment creates a centralized volume structure:

```
.volumes/
├── logs/                    # Application logs
│   ├── app.log             # General application logs
│   └── errors.log          # Error-specific logs
└── data/                    # Persistent data
    └── exchange_bot.db     # SQLite database
```

**Benefits:**
- ✅ Centralized data management
- ✅ Easy backup and restore
- ✅ Cross-platform permission handling
- ✅ Development and production consistency

## 🤖 Bot Commands

- `/start` - Welcome message
- `/help` - Show available commands
- `/ping` - Test bot responsiveness
- `/rates` - Get current exchange rates
- `/subscribe` - Subscribe to daily notifications
- `/unsubscribe` - Unsubscribe from notifications

## 💱 Supported Banks

- **Banguat** (Banco de Guatemala) - Official rates
- **Banrural** - Commercial rates
- **Nexa Banco** - Digital banking rates

## References

- [Nexa Banco](https://www.nexabanco.com/)

- [Pinggy](https://pinggy.io/)

```bash
ssh -p 443 -R0:127.0.0.1:8000 qr@free.pinggy.io
```

## Database Management

### Automatic Migrations

**Database migrations run automatically** when containers start:
- ✅ **Docker containers**: Migrations run via `docker-entrypoint.sh`
- ✅ **Always up-to-date**: Database schema stays current
- ✅ **Zero-downtime**: Migrations complete before app starts

### Manual Alembic Commands

#### Creating Migrations
```bash
# Create automatic migration (detects model changes)
uv run alembic revision --autogenerate -m "Description of change"

# Create empty migration (for manual changes)
uv run alembic revision -m "Description of change"
```

#### Running Migrations Manually
```bash
# Apply all pending migrations
uv run alembic upgrade head

# Apply up to a specific migration
uv run alembic upgrade <revision_id>

# Apply only the next migration
uv run alembic upgrade +1
```

#### Reverting Migrations
```bash
# Revert to previous migration
uv run alembic downgrade -1

# Revert to a specific migration
uv run alembic downgrade <revision_id>

# Revert all migrations
uv run alembic downgrade base
```

#### Information and Status
```bash
# View current migration
uv run alembic current

# View migration history
uv run alembic history

# View pending migrations
uv run alembic show head

# View details of a specific migration
uv run alembic show <revision_id>
```

#### Development Utilities
```bash
# Mark migration as applied (without executing)
uv run alembic stamp head

# View differences between database and models
uv run alembic check

# Generate SQL without executing
uv run alembic upgrade head --sql
```

### Typical Workflow

1. **Modify models** in `src/database/models.py`
2. **Create migration**: `uv run alembic revision --autogenerate -m "Add new field"`
3. **Review generated migration** in `alembic/versions/`
4. **Apply migration**: `uv run alembic upgrade head`

### ⚠️ Important Tips

- **Always review** autogenerated migrations before applying them
- **Backup database** before applying migrations in production
- **Use descriptive messages** for migrations
- **Test migrations** in development before production


## aiohttp

[aiohttp client quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)

Note
Don’t create a session per request. Most likely you need a session per application which performs all requests together.

More complex cases may require a session per site, e.g. one for Github and other one for Facebook APIs. Anyway making a session for every request is a very bad idea.

A session contains a connection pool inside. Connection reusage and keep-alive (both are on by default) may speed up total performance.

## Banrural API Discovery

### Summary

This document explains the step-by-step process of how Banrural's internal API was discovered and implemented to obtain USD exchange rates.

### Initial Problem

When attempting traditional web scraping of the Banrural website (https://www.banrural.com.gt/site/personas), the scraper could not find exchange rates in the initial HTML. The elements existed but were empty:

```html
<p id="efectivo-compra">Q</p>
<p id="documento-compra">Q</p>
<p id="banca-viarual-compra-mobile">Q</p>
```

### Discovery Process

#### 1. Initial HTML Analysis

First, the main page HTML was analyzed using `curl`:

```bash
curl -s "https://www.banrural.com.gt/site/personas" | grep -i "7\.59\|cambio\|dolar\|usd" -A 3 -B 3
```

**Result:** HTML elements with exchange rate-related IDs were found, but without values.

#### 2. Dynamic Loading Identification

The HTML showed that data is loaded dynamically via JavaScript:

```html
<script src="https://www.banrural.com.gt/hubfs/.../template_tipo_de_cambio.min.js"></script>
```

#### 3. JavaScript Analysis

The JavaScript file was downloaded and analyzed:

```bash
curl -s "https://www.banrural.com.gt/hubfs/hub_generated/template_assets/1/188510768808/1753208208135/template_tipo_de_cambio.js"
```

**Key finding:** The JavaScript contained code that populated HTML elements:

```javascript
$('#efectivo-compra').text('Q' + datosCompletos.compra_dolares);
$('#documento-compra').text('Q' + datosCompletos.compra_dolares_docto);
$('#banca-viarual-compra-mobile').text('Q' + datosCompletos.compra_dolares_docto_bv);
```

#### 4. API Discovery

Continuing the JavaScript analysis, the AJAX call was found:

```javascript
$.ajax({
  url: '/_hcms/api/site/banrural/tasadecambio',
  type: 'GET',
  contentType: 'application/json',
  data: JSON.stringify(),
```

**Eureka!** The internal API was: `/_hcms/api/site/banrural/tasadecambio`

#### 5. Initial API Test

First direct test:

```bash
curl -s "https://www.banrural.com.gt/_hcms/api/site/banrural/tasadecambio"
```

**Result:** `{"error":"Acceso no autorizado"}`

#### 6. Required Headers Analysis

To simulate a legitimate browser request, specific headers were added:

```bash
curl -s "https://www.banrural.com.gt/_hcms/api/site/banrural/tasadecambio" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.banrural.com.gt/site/personas" \
  -H "X-Requested-With: XMLHttpRequest"
```

**Success!** The API responded with complete JSON data:

```json
{
  "compra_dolares": "7.53",
  "venta_dolares": "7.80",
  "compra_euros": "8.36",
  "venta_euros": "9.75",
  "compra_dolares_docto": "7.56",
  "venta_dolares_docto": "7.80",
  "compra_dolares_docto_bv": "7.59",
  "venta_dolares_docto_bv": "7.77",
  "compra_euros_docto": "8.47",
  "venta_euros_docto": "9.75"
}
```

### Value Mapping

| API Field | Description | Value |
|-----------|-------------|-------|
| `compra_dolares` | Cash USD (Buy) | 7.53 |
| `compra_dolares_docto` | Document USD (Buy) | 7.56 |
| `compra_dolares_docto_bv` | **Virtual Banking APP (Buy)** | **7.59** |
| `venta_dolares` | Cash USD (Sell) | 7.80 |
| `venta_dolares_docto` | Document USD (Sell) | 7.80 |
| `venta_dolares_docto_bv` | Virtual Banking APP (Sell) | 7.77 |

### Final Implementation

#### Critical Headers

```python
api_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.banrural.com.gt/site/personas",
    "X-Requested-With": "XMLHttpRequest"
}
```

#### Specific Value Extraction

```python
if "compra_dolares_docto_bv" in data:
    rate = float(data["compra_dolares_docto_bv"])  # 7.59
    return rate
```

#### Authentication Headers
- `Referer`: Indicates where the request comes from
- `X-Requested-With: XMLHttpRequest`: Identifies AJAX requests
- `User-Agent`: Simulates a real browser

#### Hybrid Strategy
- API first (more reliable and faster)
- Fallback to web scraping if API fails

#### Tools Used

1. **curl** - For making HTTP requests and analyzing responses
2. **grep** - For searching patterns in HTML and JavaScript
3. **Manual analysis** - To understand JavaScript logic
4. **aiohttp** - To implement the asynchronous Python client

#### Final Result

The scraper now obtains the exchange rate for **Virtual Banking APP (Buy)** directly from Banrural's internal API, being much more efficient and reliable than traditional web scraping.
