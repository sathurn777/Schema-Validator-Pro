"""
Unit tests for WordPressAdapter

Tests WordPress REST API integration with mocked HTTP requests.
Uses pytest and requests_mock to simulate WordPress API responses.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from backend.adapters.wordpress_adapter import WordPressAdapter


@pytest.fixture
def wp_adapter():
    """Create a WordPressAdapter instance for testing."""
    return WordPressAdapter(
        site_url="https://example.com",
        username="testuser",
        app_password="test_app_password_1234"
    )


@pytest.fixture
def sample_schema():
    """Sample Schema.org JSON-LD for testing."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article",
        "author": {
            "@type": "Person",
            "name": "Test Author"
        }
    }


@pytest.fixture
def sample_post():
    """Sample WordPress post data."""
    return {
        "id": 123,
        "title": {"rendered": "Test Post"},
        "content": {"rendered": "<p>Test content</p>"},
        "link": "https://example.com/test-post",
        "author": 1,
        "date": "2025-10-22T00:00:00"
    }


class TestWordPressAdapterInit:
    """Test WordPressAdapter initialization."""
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from site_url."""
        adapter = WordPressAdapter(
            site_url="https://example.com/",
            username="user",
            app_password="pass"
        )
        assert adapter.site_url == "https://example.com"
        assert adapter.api_base == "https://example.com/wp-json/wp/v2"
    
    def test_init_sets_auth(self, wp_adapter):
        """Test that HTTP Basic Auth is configured."""
        assert wp_adapter._session.auth is not None
        assert wp_adapter.username == "testuser"
        assert wp_adapter.app_password == "test_app_password_1234"


class TestConnectionMethods:
    """Test connection and authentication methods."""
    
    def test_test_connection_success(self, wp_adapter):
        """Test successful connection to WordPress."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = wp_adapter.test_connection()
            
            assert result is True
            mock_get.assert_called_once_with(
                "https://example.com/wp-json",
                timeout=10
            )
    
    def test_test_connection_failure(self, wp_adapter):
        """Test connection failure (non-200 status)."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            result = wp_adapter.test_connection()
            
            assert result is False
    
    def test_test_connection_network_error(self, wp_adapter):
        """Test connection failure due to network error."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            result = wp_adapter.test_connection()
            
            assert result is False
    
    def test_test_authentication_success(self, wp_adapter):
        """Test successful authentication."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = wp_adapter.test_authentication()
            
            assert result is True
            mock_get.assert_called_once_with(
                "https://example.com/wp-json/wp/v2/users/me",
                timeout=10
            )
    
    def test_test_authentication_failure_401(self, wp_adapter):
        """Test authentication failure (401 Unauthorized)."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            result = wp_adapter.test_authentication()
            
            assert result is False
    
    def test_test_authentication_network_error(self, wp_adapter):
        """Test authentication failure due to network error."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")
            
            result = wp_adapter.test_authentication()
            
            assert result is False


class TestInjectSchema:
    """Test schema injection method."""
    
    def test_inject_schema_success(self, wp_adapter, sample_schema):
        """Test successful schema injection."""
        with patch.object(wp_adapter._session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = wp_adapter.inject_schema(123, sample_schema)
            
            assert result is True
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://example.com/wp-json/wp/v2/posts/123"
            assert "meta" in call_args[1]["json"]
    
    def test_inject_schema_failure_404(self, wp_adapter, sample_schema):
        """Test schema injection failure (post not found)."""
        with patch.object(wp_adapter._session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_post.return_value = mock_response
            
            result = wp_adapter.inject_schema(999, sample_schema)
            
            assert result is False
    
    def test_inject_schema_network_error(self, wp_adapter, sample_schema):
        """Test schema injection failure due to network error."""
        with patch.object(wp_adapter._session, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Network error")
            
            result = wp_adapter.inject_schema(123, sample_schema)
            
            assert result is False


class TestGetPost:
    """Test get_post method."""
    
    def test_get_post_success(self, wp_adapter, sample_post):
        """Test successful post retrieval."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_post
            mock_get.return_value = mock_response
            
            result = wp_adapter.get_post(123)
            
            assert result == sample_post
            mock_get.assert_called_once_with(
                "https://example.com/wp-json/wp/v2/posts/123",
                timeout=10
            )
    
    def test_get_post_not_found(self, wp_adapter):
        """Test post retrieval when post doesn't exist."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            result = wp_adapter.get_post(999)
            
            assert result is None
    
    def test_get_post_network_error(self, wp_adapter):
        """Test post retrieval failure due to network error."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            result = wp_adapter.get_post(123)
            
            assert result is None


class TestGetPosts:
    """Test get_posts method."""
    
    def test_get_posts_success(self, wp_adapter, sample_post):
        """Test successful posts retrieval."""
        posts = [sample_post, {**sample_post, "id": 124}]
        
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = posts
            mock_get.return_value = mock_response
            
            result = wp_adapter.get_posts(per_page=10, page=1)
            
            assert result == posts
            assert len(result) == 2
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["per_page"] == 10
            assert call_args[1]["params"]["page"] == 1
    
    def test_get_posts_empty(self, wp_adapter):
        """Test posts retrieval when no posts exist."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = wp_adapter.get_posts()
            
            assert result == []
    
    def test_get_posts_max_per_page(self, wp_adapter):
        """Test that per_page is capped at 100."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            wp_adapter.get_posts(per_page=200)
            
            call_args = mock_get.call_args
            assert call_args[1]["params"]["per_page"] == 100
    
    def test_get_posts_network_error(self, wp_adapter):
        """Test posts retrieval failure due to network error."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")

            result = wp_adapter.get_posts()

            assert result == []

    def test_get_posts_non_200_status(self, wp_adapter):
        """Test posts retrieval with non-200 status code (e.g., 500)."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            result = wp_adapter.get_posts()

            assert result == []


class TestSearchPosts:
    """Test search_posts method."""
    
    def test_search_posts_success(self, wp_adapter, sample_post):
        """Test successful post search."""
        matching_posts = [sample_post]
        
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = matching_posts
            mock_get.return_value = mock_response
            
            result = wp_adapter.search_posts("test query", per_page=10)
            
            assert result == matching_posts
            call_args = mock_get.call_args
            assert call_args[1]["params"]["search"] == "test query"
            assert call_args[1]["params"]["per_page"] == 10

    def test_search_posts_no_results(self, wp_adapter):
        """Test post search with no matching results."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            result = wp_adapter.search_posts("nonexistent")

            assert result == []

    def test_search_posts_network_error(self, wp_adapter):
        """Test post search failure due to network error."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Error")

            result = wp_adapter.search_posts("test")

            assert result == []

    def test_search_posts_non_200_status(self, wp_adapter):
        """Test post search with non-200 status code (e.g., 503)."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_get.return_value = mock_response

            result = wp_adapter.search_posts("test")

            assert result == []


class TestGetSchema:
    """Test get_schema method."""

    def test_get_schema_success(self, wp_adapter, sample_schema):
        """Test successful schema retrieval from post meta."""
        post_with_schema = {
            "id": 123,
            "meta": {
                "_geo_schema": '{"@context": "https://schema.org", "@type": "Article"}'
            }
        }

        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = post_with_schema
            mock_get.return_value = mock_response

            result = wp_adapter.get_schema(123)

            assert result is not None
            assert result["@type"] == "Article"

    def test_get_schema_no_meta(self, wp_adapter):
        """Test schema retrieval when post has no schema meta."""
        post_without_schema = {
            "id": 123,
            "meta": {}
        }

        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = post_without_schema
            mock_get.return_value = mock_response

            result = wp_adapter.get_schema(123)

            assert result is None

    def test_get_schema_invalid_json(self, wp_adapter):
        """Test schema retrieval when meta contains invalid JSON."""
        post_with_invalid_schema = {
            "id": 123,
            "meta": {
                "_geo_schema": "invalid json {"
            }
        }

        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = post_with_invalid_schema
            mock_get.return_value = mock_response

            result = wp_adapter.get_schema(123)

            assert result is None

    def test_get_schema_post_not_found(self, wp_adapter):
        """Test schema retrieval when post doesn't exist."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = wp_adapter.get_schema(999)

            assert result is None

    def test_get_schema_already_dict(self, wp_adapter):
        """Test schema retrieval when meta contains dict (not JSON string)."""
        schema_dict = {"@context": "https://schema.org", "@type": "Article"}
        post_with_dict_schema = {
            "id": 123,
            "meta": {
                "_geo_schema": schema_dict  # Already a dict, not a string
            }
        }

        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = post_with_dict_schema
            mock_get.return_value = mock_response

            result = wp_adapter.get_schema(123)

            assert result == schema_dict
            assert result["@type"] == "Article"


class TestHelperMethods:
    """Test helper methods for extracting post data."""

    def test_extract_content(self, wp_adapter, sample_post):
        """Test extracting content from post."""
        content = wp_adapter.extract_content(sample_post)
        assert "Test Post" in content
        assert "Test content" in content

    def test_extract_content_missing_fields(self, wp_adapter):
        """Test extracting content from post with missing fields."""
        post = {"id": 123}
        content = wp_adapter.extract_content(post)
        assert content == "\n\n"

    def test_extract_content_strips_html(self, wp_adapter):
        """Test that HTML tags are stripped from content."""
        post = {
            "title": {"rendered": "Test Title"},
            "content": {"rendered": "<p>Test <strong>content</strong> with <a href='#'>link</a></p>"}
        }
        content = wp_adapter.extract_content(post)
        assert "<p>" not in content
        assert "<strong>" not in content
        assert "<a" not in content
        assert "Test content with link" in content

    def test_extract_content_title_as_string(self, wp_adapter):
        """Test extracting content when title is a string (not dict)."""
        post = {
            "title": "Plain String Title",
            "content": {"rendered": "Test content"}
        }
        content = wp_adapter.extract_content(post)
        assert "Plain String Title" in content
        assert "Test content" in content

    def test_extract_content_content_as_string(self, wp_adapter):
        """Test extracting content when content is a string (not dict)."""
        post = {
            "title": {"rendered": "Test Title"},
            "content": "Plain String Content"
        }
        content = wp_adapter.extract_content(post)
        assert "Test Title" in content
        assert "Plain String Content" in content

    def test_extract_content_both_as_strings(self, wp_adapter):
        """Test extracting content when both title and content are strings."""
        post = {
            "title": "String Title",
            "content": "String Content"
        }
        content = wp_adapter.extract_content(post)
        assert "String Title" in content
        assert "String Content" in content

    def test_get_post_url(self, wp_adapter, sample_post):
        """Test extracting post URL."""
        url = wp_adapter.get_post_url(sample_post)
        assert url == "https://example.com/test-post"

    def test_get_post_url_missing(self, wp_adapter):
        """Test extracting URL from post without link."""
        post = {"id": 123}
        url = wp_adapter.get_post_url(post)
        assert url == ""

    def test_get_post_author_success(self, wp_adapter, sample_post):
        """Test extracting post author name."""
        user_data = {"id": 1, "name": "John Doe"}

        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = user_data
            mock_get.return_value = mock_response

            author = wp_adapter.get_post_author(sample_post)

            assert author == "John Doe"
            mock_get.assert_called_once_with(
                "https://example.com/wp-json/wp/v2/users/1",
                timeout=10
            )

    def test_get_post_author_no_author_id(self, wp_adapter):
        """Test extracting author when post has no author ID."""
        post = {"id": 123}
        author = wp_adapter.get_post_author(post)
        assert author == "Unknown"

    def test_get_post_author_api_error(self, wp_adapter, sample_post):
        """Test extracting author when user API fails."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            author = wp_adapter.get_post_author(sample_post)

            assert author == "Unknown"

    def test_get_post_author_network_error(self, wp_adapter, sample_post):
        """Test extracting author when network error occurs."""
        with patch.object(wp_adapter._session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Error")

            author = wp_adapter.get_post_author(sample_post)

            assert author == "Unknown"


class TestSessionManagement:
    """Test session management methods."""

    def test_close_session(self, wp_adapter):
        """Test closing the session."""
        with patch.object(wp_adapter._session, 'close') as mock_close:
            wp_adapter.close()
            mock_close.assert_called_once()


