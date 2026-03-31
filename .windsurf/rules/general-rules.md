---
trigger: always_on
---

# Development Rules for Exchange Rate Bot

## Code Style
- Use Python 3.13+
- Use ruff for code formatting and linting
- Use pyright for type checking
- Use type hints in all functions
- Document functions with English docstrings

## Logging
- Use logging module instead of print statements
- Use string interpolation with %s instead of f-strings in logging calls
- Example: `logger.info("Processing %s items", count)` instead of `logger.info(f"Processing {count} items")`
- This prevents unnecessary string formatting when logging is disabled

## Package Management
- Use uv as package manager
- Run commands with `uv run <COMMAND>`
- Use uv for dependency management and virtual environments

## Process Management
- Before running long-running applications (like `uv run python main.py`, `uv run python manage.py`, etc.), always check for and terminate existing processes first
- Use `pkill -f "python main.py"` or similar to kill existing processes
- This prevents port conflicts and ensures clean application restarts
- Example workflow:
  1. `pkill -f "python main.py"` (kill existing)
  2. `uv run python main.py` (start new instance)
- Apply this rule for any command that starts a server, bot, or long-running process

## Code Quality
- Run quality checks with `uv run ruff check` and `uv run pyright`
- Fix formatting with `uv run ruff format`
- Run tests with `uv run pytest`

## General Principles
- Favor readability over abstraction
- Use async/await for network operations
- Prefer composition over inheritance
- Use environment variables for API keys and secrets
- When in doubt, prefer a simple function over a new class