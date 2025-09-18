"""URL manipulation utilities."""

from urllib.parse import urljoin, urlparse


def validate_url(url: str) -> str:
    """
    Validates if a URL has the correct format.
    If it's invalid, raises a ValueError.

    Args:
        url: URL to validate

    Returns:
        The URL itself if valid.

    Raises:
        ValueError: If the URL is invalid.
    """
    result = urlparse(url)
    if all([result.scheme, result.netloc]):
        return url
    raise ValueError(f"Invalid URL: {url}")


def build_url(base_url: str, path: str) -> str:
    """
    Builds a URL by combining base_url and endpoint, avoiding double '/' or missing separators.

    Args:
        base_url: Base URL (e.g. "https://api.example.com")
        path: Endpoint to append (e.g. "/mypath" or "mypath")

    Returns:
        Complete and correctly formatted URL

    Examples:
        >>> build_url("https://api.example.com", "/path")
        'https://api.example.com/path'
        >>> build_url("https://api.example.com/", "path")
        'https://api.example.com/path'
        >>> build_url("https://api.example.com", "path")
        'https://api.example.com/path'
    """
    return validate_url(urljoin(base_url.rstrip("/") + "/", path.lstrip("/")))
