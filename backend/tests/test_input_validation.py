"""
Tests for input validation and security constraints.

Verifies that:
1. Pydantic models enforce field constraints (max_length, etc.)
2. Request body size limits are enforced
3. Metadata size limits are enforced
4. Schema size limits are enforced
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from pydantic import ValidationError
from backend.models.schema import SchemaGenerateRequest, SchemaValidateRequest


class TestInputValidation:
    """Test input validation and security constraints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_schema_type_max_length_enforced(self):
        """Test that schema_type has max_length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            SchemaGenerateRequest(
                schema_type="A" * 101,  # Exceeds max_length=100
                content="Test content"
            )
        
        errors = exc_info.value.errors()
        assert any("schema_type" in str(e) for e in errors)
        assert any("100" in str(e) or "length" in str(e).lower() for e in errors)

    def test_content_min_length_enforced(self):
        """Test that content has min_length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            SchemaGenerateRequest(
                schema_type="Article",
                content=""  # Empty content violates min_length=1
            )
        
        errors = exc_info.value.errors()
        assert any("content" in str(e) for e in errors)

    def test_content_max_length_enforced(self):
        """Test that content has max_length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            SchemaGenerateRequest(
                schema_type="Article",
                content="A" * 1000001  # Exceeds max_length=1000000
            )
        
        errors = exc_info.value.errors()
        assert any("content" in str(e) for e in errors)
        assert any("1000000" in str(e) or "length" in str(e).lower() for e in errors)

    def test_url_max_length_enforced(self):
        """Test that url has max_length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            SchemaGenerateRequest(
                schema_type="Article",
                content="Test content",
                url="https://example.com/" + "a" * 2049  # Exceeds max_length=2048
            )
        
        errors = exc_info.value.errors()
        assert any("url" in str(e) for e in errors)

    def test_metadata_max_keys_enforced(self):
        """Test that metadata has max keys constraint."""
        large_metadata = {f"key_{i}": f"value_{i}" for i in range(51)}  # 51 keys > 50 limit
        
        with pytest.raises(ValidationError) as exc_info:
            SchemaGenerateRequest(
                schema_type="Article",
                content="Test content",
                metadata=large_metadata
            )
        
        errors = exc_info.value.errors()
        assert any("metadata" in str(e) for e in errors)
        assert any("50" in str(e) for e in errors)

    def test_metadata_within_limit_accepted(self):
        """Test that metadata within limit is accepted."""
        valid_metadata = {f"key_{i}": f"value_{i}" for i in range(50)}  # Exactly 50 keys
        
        request = SchemaGenerateRequest(
            schema_type="Article",
            content="Test content",
            metadata=valid_metadata
        )
        
        assert request.metadata == valid_metadata

    def test_schema_max_keys_enforced(self):
        """Test that schema has max top-level keys constraint."""
        large_schema = {f"field_{i}": f"value_{i}" for i in range(101)}  # 101 keys > 100 limit
        
        with pytest.raises(ValidationError) as exc_info:
            SchemaValidateRequest(schema=large_schema)
        
        errors = exc_info.value.errors()
        assert any("schema" in str(e) for e in errors)
        assert any("100" in str(e) for e in errors)

    def test_schema_within_limit_accepted(self):
        """Test that schema within limit is accepted."""
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test"
        }
        
        request = SchemaValidateRequest(schema=valid_schema)
        assert request.schema == valid_schema

    def test_api_rejects_oversized_content(self):
        """Test that API rejects content exceeding max_length."""
        response = self.client.post(
            "/api/v1/schema/generate",
            json={
                "schema_type": "Article",
                "content": "A" * 1000001  # Exceeds max_length
            }
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_api_rejects_oversized_metadata(self):
        """Test that API rejects metadata with too many keys."""
        large_metadata = {f"key_{i}": f"value_{i}" for i in range(51)}
        
        response = self.client.post(
            "/api/v1/schema/generate",
            json={
                "schema_type": "Article",
                "content": "Test content",
                "metadata": large_metadata
            }
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_api_accepts_valid_input(self):
        """Test that API accepts valid input within all constraints."""
        response = self.client.post(
            "/api/v1/schema/generate",
            json={
                "schema_type": "Article",
                "content": "This is a test article about technology.",
                "url": "https://example.com/article",
                "metadata": {"author": "John Doe", "category": "Tech"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "schema" in data
        assert "completeness_score" in data

    def test_api_rejects_empty_content(self):
        """Test that API rejects empty content."""
        response = self.client.post(
            "/api/v1/schema/generate",
            json={
                "schema_type": "Article",
                "content": ""
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_api_rejects_oversized_schema(self):
        """Test that API rejects schema with too many top-level keys."""
        large_schema = {f"field_{i}": f"value_{i}" for i in range(101)}
        
        response = self.client.post(
            "/api/v1/schema/validate",
            json={"schema": large_schema}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_valid_schema_types_accepted(self):
        """Test that valid schema types are accepted."""
        valid_types = ["Article", "Product", "Recipe", "Event", "Organization", "Person"]
        
        for schema_type in valid_types:
            request = SchemaGenerateRequest(
                schema_type=schema_type,
                content="Test content"
            )
            assert request.schema_type == schema_type

    def test_long_but_valid_content_accepted(self):
        """Test that long but valid content is accepted."""
        # 100KB content (well within 1MB limit)
        long_content = "A" * 100000
        
        request = SchemaGenerateRequest(
            schema_type="Article",
            content=long_content
        )
        
        assert len(request.content) == 100000

    def test_url_validation_accepts_valid_urls(self):
        """Test that valid URLs are accepted."""
        valid_urls = [
            "https://example.com",
            "https://example.com/path/to/article",
            "https://subdomain.example.com/article?id=123",
        ]
        
        for url in valid_urls:
            request = SchemaGenerateRequest(
                schema_type="Article",
                content="Test",
                url=url
            )
            assert request.url == url

    def test_none_values_accepted_for_optional_fields(self):
        """Test that None values are accepted for optional fields."""
        request = SchemaGenerateRequest(
            schema_type="Article",
            content="Test content",
            url=None,
            metadata=None
        )
        
        assert request.url is None
        assert request.metadata is None

