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

## SOLID Principles
- **Single Responsibility**: Each class should have only one reason to change
- **Open/Closed**: Classes should be open for extension, closed for modification
- **Liskov Substitution**: Derived classes must be substitutable for their base classes
- **Interface Segregation**: Clients should not depend on interfaces they don't use
- **Dependency Inversion**: Depend on abstractions, not concretions

## Design Patterns
- Suggest appropriate design patterns when beneficial:
  - **Strategy Pattern**: For different exchange rate providers
  - **Factory Pattern**: For creating API clients or handlers
  - **Observer Pattern**: For rate change notifications
  - **Command Pattern**: For bot command handling
  - **Repository Pattern**: For data access abstraction
  - **Dependency Injection**: For loose coupling and testability
- Always explain why a pattern is recommended
- Prefer composition over inheritance
- Use Protocol classes for defining interfaces in Python

## Documentation
- README.md should include installation instructions
- Document API endpoints if applicable
- Include usage examples