# Development Rules for Exchange Rate Bot

## Code Style
- Use Python 3.13+
- Use ruff for code formatting and linting
- Use pyright for type checking
- Use type hints in all functions
- Document functions with English docstrings

## Architecture
- Separate business logic from presentation
- Use async/await for network operations
- Implement robust error handling
- Use logging instead of print statements

## Package Management
- Use uv as package manager
- Run commands with `uv run <COMMAND>`
- Use uv for dependency management and virtual environments

## APIs and Dependencies
- Use httpx for HTTP calls
- Implement rate limiting for external APIs
- Cache responses when appropriate
- Use environment variables for API keys

## Testing
- Write unit tests for critical functions
- Use pytest as testing framework
- Run tests with `uv run pytest`
- Mock external API calls in tests

## Code Quality
- Use ruff for linting and formatting
- Use pyright for static type checking
- Run quality checks with `uv run ruff check` and `uv run pyright`
- Fix formatting with `uv run ruff format`

## Documentation
- README.md should include installation instructions
- Document API endpoints if applicable
- Include usage examples