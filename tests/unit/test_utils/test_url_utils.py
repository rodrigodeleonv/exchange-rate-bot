"""Unit tests for URL utilities."""

import pytest

from src.utils.url_utils import build_url, validate_url


class TestValidateUrl:
    """Test cases for validate_url function."""

    def test_validate_url_valid_http(self):
        """Test validation of valid HTTP URL."""
        url = "http://example.com"
        result = validate_url(url)
        assert result == url

    def test_validate_url_valid_https(self):
        """Test validation of valid HTTPS URL."""
        url = "https://example.com"
        result = validate_url(url)
        assert result == url

    def test_validate_url_with_path(self):
        """Test validation of URL with path."""
        url = "https://example.com/api/v1/data"
        result = validate_url(url)
        assert result == url

    def test_validate_url_with_query_params(self):
        """Test validation of URL with query parameters."""
        url = "https://example.com/api?param=value&other=123"
        result = validate_url(url)
        assert result == url

    def test_validate_url_with_port(self):
        """Test validation of URL with port."""
        url = "https://example.com:8080/api"
        result = validate_url(url)
        assert result == url

    def test_validate_url_invalid_no_scheme(self):
        """Test validation fails for URL without scheme."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("example.com")

    def test_validate_url_invalid_no_netloc(self):
        """Test validation fails for URL without netloc."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("https://")

    def test_validate_url_invalid_empty(self):
        """Test validation fails for empty URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("")

    def test_validate_url_invalid_malformed(self):
        """Test validation fails for malformed URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("not-a-url")


class TestBuildUrl:
    """Test cases for build_url function."""

    def test_build_url_basic(self):
        """Test basic URL building."""
        result = build_url("https://api.example.com", "path")
        assert result == "https://api.example.com/path"

    def test_build_url_base_with_trailing_slash(self):
        """Test URL building when base has trailing slash."""
        result = build_url("https://api.example.com/", "path")
        assert result == "https://api.example.com/path"

    def test_build_url_path_with_leading_slash(self):
        """Test URL building when path has leading slash."""
        result = build_url("https://api.example.com", "/path")
        assert result == "https://api.example.com/path"

    def test_build_url_both_with_slashes(self):
        """Test URL building when both base and path have slashes."""
        result = build_url("https://api.example.com/", "/path")
        assert result == "https://api.example.com/path"

    def test_build_url_nested_path(self):
        """Test URL building with nested path."""
        result = build_url("https://api.example.com", "v1/users/123")
        assert result == "https://api.example.com/v1/users/123"

    def test_build_url_empty_path(self):
        """Test URL building with empty path."""
        result = build_url("https://api.example.com", "")
        assert result == "https://api.example.com/"

    def test_build_url_path_with_query(self):
        """Test URL building with path containing query parameters."""
        result = build_url("https://api.example.com", "search?q=test")
        assert result == "https://api.example.com/search?q=test"

    def test_build_url_complex_path(self):
        """Test URL building with complex path."""
        result = build_url("https://api.example.com/v1", "users/123/posts")
        assert result == "https://api.example.com/v1/users/123/posts"

    def test_build_url_invalid_base(self):
        """Test URL building fails with invalid base URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            build_url("not-a-url", "path")

    def test_build_url_base_without_scheme(self):
        """Test URL building fails when base URL has no scheme."""
        with pytest.raises(ValueError, match="Invalid URL"):
            build_url("example.com", "path")

    def test_build_url_multiple_slashes(self):
        """Test URL building normalizes multiple slashes correctly."""
        result = build_url("https://api.example.com//", "//path//to//resource")
        assert result == "https://api.example.com/path/to/resource"

    def test_build_url_preserves_port(self):
        """Test URL building preserves port number."""
        result = build_url("https://localhost:8080", "api/v1")
        assert result == "https://localhost:8080/api/v1"

    def test_build_url_docstring_examples(self):
        """Test the examples from the docstring work correctly."""
        # Example 1
        result1 = build_url("https://api.example.com", "/path")
        assert result1 == "https://api.example.com/path"

        # Example 2
        result2 = build_url("https://api.example.com/", "path")
        assert result2 == "https://api.example.com/path"

        # Example 3
        result3 = build_url("https://api.example.com", "path")
        assert result3 == "https://api.example.com/path"
