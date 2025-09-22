# Prompts and Context for AI Assistant

## Project Context
This is an exchange rate bot that should:
- Fetch updated exchange rates
- Provide currency conversions
- Handle multiple data sources
- Be reliable and efficient

## Specific Instructions for AI

### When writing code:
- Always ask for clarifications before assuming functionality
- Use descriptive variable names in English
- Implement robust input validation
- Consider edge cases and error handling

### When suggesting architecture:
- Prefer simple and maintainable patterns
- Suggest clear separation of responsibilities
- Consider future scalability
- Document important architectural decisions

### When working with APIs:
- Implement retry logic for failed calls
- Use appropriate rate limiting
- Cache responses when beneficial
- Handle timeouts and network errors gracefully

## Examples of Preferred Responses

### ✅ Good:
```python
async def get_exchange_rate(source_currency: str, target_currency: str) -> float:
    """
    Gets the exchange rate between two currencies.
    
    Args:
        source_currency: ISO code of source currency (e.g., 'USD')
        target_currency: ISO code of target currency (e.g., 'EUR')
        
    Returns:
        Exchange rate as float
        
    Raises:
        ValueError: If currencies are not valid
        APIError: If there are problems with external API
    """
```

### ❌ Avoid:
```python
def get_rate(from_curr, to_curr):
    # No documentation, no type hints, non-descriptive names
```
