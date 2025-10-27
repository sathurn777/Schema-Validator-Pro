"""
Tests for structured errors API feature.

Verifies that /validate endpoint supports both:
1. Default mode (structured=False): backward compatible string lists
2. Structured mode (structured=True): detailed error objects with path/code/severity
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


class TestStructuredErrorsAPI:
    """Test structured errors API functionality."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_validate_default_mode_returns_string_lists(self):
        """Test that default mode (structured=False) returns simple string lists."""
        # Invalid schema missing required fields
        invalid_schema = {
            "@context": "https://schema.org",
            "@type": "Article"
            # Missing required 'headline' field
        }

        response = self.client.post(
            "/api/v1/schema/validate",
            json={"schema": invalid_schema}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure matches SchemaValidateResponse
        assert "is_valid" in data
        assert "errors" in data
        assert "warnings" in data
        assert "completeness_score" in data
        assert "suggestions" in data

        # Verify errors are simple strings (backward compatible)
        assert isinstance(data["errors"], list)
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0
        assert all(isinstance(e, str) for e in data["errors"])

        # Verify warnings are simple strings
        assert isinstance(data["warnings"], list)
        assert all(isinstance(w, str) for w in data["warnings"])

    def test_validate_structured_false_explicit_returns_string_lists(self):
        """Test that structured=false explicitly returns simple string lists."""
        invalid_schema = {
            "@context": "https://schema.org",
            "@type": "Product"
            # Missing required 'name' field
        }

        response = self.client.post(
            "/api/v1/schema/validate?structured=false",
            json={"schema": invalid_schema}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify errors are simple strings
        assert isinstance(data["errors"], list)
        assert data["is_valid"] is False
        assert all(isinstance(e, str) for e in data["errors"])

    def test_validate_structured_true_returns_detailed_errors(self):
        """Test that structured=true returns detailed error objects."""
        invalid_schema = {
            "@context": "https://schema.org",
            "@type": "Article"
            # Missing required 'headline' field
        }

        response = self.client.post(
            "/api/v1/schema/validate?structured=true",
            json={"schema": invalid_schema}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure matches StructuredSchemaValidateResponse
        assert "is_valid" in data
        assert "errors" in data
        assert "warnings" in data
        assert "completeness_score" in data
        assert "suggestions" in data

        # Verify errors are structured objects
        assert isinstance(data["errors"], list)
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

        # Verify each error has required structured fields
        for error in data["errors"]:
            assert isinstance(error, dict)
            assert "path" in error
            assert "code" in error
            assert "message" in error
            assert "severity" in error
            assert error["severity"] == "ERROR"

        # Verify warnings are structured objects
        assert isinstance(data["warnings"], list)
        for warning in data["warnings"]:
            assert isinstance(warning, dict)
            assert "path" in warning
            assert "code" in warning
            assert "message" in warning
            assert "severity" in warning
            assert warning["severity"] == "WARNING"

    def test_validate_structured_mode_with_valid_schema(self):
        """Test structured mode with a valid schema."""
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {
                "@type": "Person",
                "name": "John Doe"
            },
            "datePublished": "2025-10-23"
        }

        response = self.client.post(
            "/api/v1/schema/validate?structured=true",
            json={"schema": valid_schema}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is True
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) == 0
        assert isinstance(data["warnings"], list)
        # May have warnings for missing recommended fields
        assert data["completeness_score"] >= 0

    def test_validate_default_mode_with_valid_schema(self):
        """Test default mode with a valid schema (backward compatibility)."""
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product"
        }

        response = self.client.post(
            "/api/v1/schema/validate",
            json={"schema": valid_schema}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is True
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) == 0
        assert isinstance(data["warnings"], list)
        # Warnings should be strings in default mode
        assert all(isinstance(w, str) for w in data["warnings"])

    def test_structured_errors_contain_correct_codes(self):
        """Test that structured errors contain appropriate error codes."""
        schema_missing_context = {
            "@type": "Article",
            "headline": "Test"
        }

        response = self.client.post(
            "/api/v1/schema/validate?structured=true",
            json={"schema": schema_missing_context}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

        # Should have MISSING_CONTEXT error
        error_codes = [e["code"] for e in data["errors"]]
        assert "MISSING_CONTEXT" in error_codes

    def test_structured_errors_contain_field_paths(self):
        """Test that structured errors contain correct field paths."""
        invalid_schema = {
            "@context": "https://schema.org",
            "@type": "Product"
            # Missing 'name' field
        }

        response = self.client.post(
            "/api/v1/schema/validate?structured=true",
            json={"schema": invalid_schema}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

        # Should have error with path pointing to missing field
        paths = [e["path"] for e in data["errors"]]
        assert any("/name" in path for path in paths)

    def test_backward_compatibility_existing_tests_still_work(self):
        """Test that existing API behavior is unchanged (100% backward compatible)."""
        # This test simulates existing client code that doesn't use structured parameter
        test_schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Test Recipe"
        }

        response = self.client.post(
            "/api/v1/schema/validate",
            json={"schema": test_schema}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify exact same response structure as before
        assert set(data.keys()) == {"is_valid", "errors", "warnings", "completeness_score", "suggestions"}
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["completeness_score"], (int, float))
        assert isinstance(data["is_valid"], bool)

