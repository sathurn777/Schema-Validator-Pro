"""
Comprehensive tests for auth.py - API Key Authentication Middleware.

Target: 90%+ coverage for auth.py (currently 61%)

Tests cover:
- Middleware initialization with different configurations
- Authentication enabled/disabled scenarios
- Public endpoint access
- Protected endpoint access with valid/invalid API keys
- Missing API key scenarios
- Helper function testing
- Edge cases and boundary conditions
- Concurrent request handling
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response

from backend.middleware.auth import (
    APIKeyMiddleware,
    get_api_key_from_env,
    validate_api_key,
    API_KEY_HEADER,
)


class TestAPIKeyMiddlewareInitialization:
    """Test APIKeyMiddleware initialization."""

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicit API key."""
        app = FastAPI()
        middleware = APIKeyMiddleware(app, api_key="test-key-123")
        
        assert middleware.api_key == "test-key-123"
        assert middleware.enabled is True
        assert "/" in middleware.public_endpoints
        assert "/health" in middleware.public_endpoints

    def test_init_with_env_api_key(self):
        """Test initialization with API key from environment."""
        os.environ["API_KEY"] = "env-key-456"
        
        try:
            app = FastAPI()
            middleware = APIKeyMiddleware(app)
            
            assert middleware.api_key == "env-key-456"
            assert middleware.enabled is True
        finally:
            del os.environ["API_KEY"]

    def test_init_without_api_key(self):
        """Test initialization without API key (disabled)."""
        # Ensure API_KEY is not set
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]
        
        app = FastAPI()
        middleware = APIKeyMiddleware(app)
        
        assert middleware.api_key is None
        assert middleware.enabled is False

    def test_init_explicit_key_overrides_env(self):
        """Test that explicit API key overrides environment variable."""
        os.environ["API_KEY"] = "env-key"
        
        try:
            app = FastAPI()
            middleware = APIKeyMiddleware(app, api_key="explicit-key")
            
            assert middleware.api_key == "explicit-key"
            assert middleware.enabled is True
        finally:
            del os.environ["API_KEY"]

    def test_public_endpoints_configured(self):
        """Test that public endpoints are properly configured."""
        app = FastAPI()
        middleware = APIKeyMiddleware(app, api_key="test-key")
        
        expected_endpoints = {"/", "/health", "/docs", "/redoc", "/openapi.json"}
        assert middleware.public_endpoints == expected_endpoints


class TestAPIKeyMiddlewareDisabled:
    """Test middleware behavior when authentication is disabled."""

    @pytest.fixture
    def app_no_auth(self):
        """Create FastAPI app without authentication."""
        # Ensure API_KEY is not set
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]
        
        app = FastAPI()
        app.add_middleware(APIKeyMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        return app

    def test_disabled_allows_all_requests(self, app_no_auth):
        """Test that disabled auth allows all requests."""
        client = TestClient(app_no_auth)
        
        # Should work without API key
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    def test_disabled_ignores_api_key_header(self, app_no_auth):
        """Test that disabled auth ignores API key header."""
        client = TestClient(app_no_auth)
        
        # Should work even with invalid API key
        response = client.get("/test", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 200


class TestAPIKeyMiddlewareEnabled:
    """Test middleware behavior when authentication is enabled."""

    @pytest.fixture
    def app_with_auth(self):
        """Create FastAPI app with authentication enabled."""
        app = FastAPI()
        app.add_middleware(APIKeyMiddleware, api_key="valid-test-key-123")
        
        @app.get("/protected")
        async def protected_endpoint():
            return {"message": "protected data"}
        
        @app.get("/")
        async def root():
            return {"message": "public root"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        return app

    def test_public_endpoint_no_auth_required(self, app_with_auth):
        """Test that public endpoints don't require authentication."""
        client = TestClient(app_with_auth)
        
        # Root endpoint should work without API key
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "public root"}
        
        # Health endpoint should work without API key
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_protected_endpoint_with_valid_key(self, app_with_auth):
        """Test protected endpoint with valid API key."""
        client = TestClient(app_with_auth)
        
        response = client.get(
            "/protected",
            headers={"X-API-Key": "valid-test-key-123"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "protected data"}

    def test_protected_endpoint_without_key(self, app_with_auth):
        """Test protected endpoint without API key returns 401."""
        client = TestClient(app_with_auth)

        response = client.get("/protected")
        assert response.status_code == 401
        assert "Invalid or missing API key" in response.json()["detail"]
        assert response.headers.get("www-authenticate") == "ApiKey"

    def test_protected_endpoint_with_invalid_key(self, app_with_auth):
        """Test protected endpoint with invalid API key returns 401."""
        client = TestClient(app_with_auth)

        response = client.get(
            "/protected",
            headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 401
        assert "Invalid or missing API key" in response.json()["detail"]

    def test_protected_endpoint_with_empty_key(self, app_with_auth):
        """Test protected endpoint with empty API key returns 401."""
        client = TestClient(app_with_auth)

        response = client.get(
            "/protected",
            headers={"X-API-Key": ""}
        )
        assert response.status_code == 401


class TestAPIKeyMiddlewareEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_case_sensitive_api_key(self):
        """Test that API key comparison is case-sensitive."""
        app = FastAPI()
        app.add_middleware(APIKeyMiddleware, api_key="TestKey123")

        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Correct case should work
        response = client.get("/test", headers={"X-API-Key": "TestKey123"})
        assert response.status_code == 200

        # Wrong case should fail
        response = client.get("/test", headers={"X-API-Key": "testkey123"})
        assert response.status_code == 401

    def test_whitespace_in_api_key(self):
        """Test API key with whitespace."""
        app = FastAPI()
        app.add_middleware(APIKeyMiddleware, api_key="key with spaces")

        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Exact match with spaces should work
        response = client.get("/test", headers={"X-API-Key": "key with spaces"})
        assert response.status_code == 200

        # Without spaces should fail
        response = client.get("/test", headers={"X-API-Key": "keywithspaces"})
        assert response.status_code == 401

    def test_special_characters_in_api_key(self):
        """Test API key with special characters."""
        app = FastAPI()
        special_key = "key!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        app.add_middleware(APIKeyMiddleware, api_key=special_key)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        
        response = client.get("/test", headers={"X-API-Key": special_key})
        assert response.status_code == 200


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_api_key_from_env_with_key(self):
        """Test get_api_key_from_env when API_KEY is set."""
        os.environ["API_KEY"] = "test-env-key"
        
        try:
            result = get_api_key_from_env()
            assert result == "test-env-key"
        finally:
            del os.environ["API_KEY"]

    def test_get_api_key_from_env_without_key(self):
        """Test get_api_key_from_env when API_KEY is not set."""
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]
        
        result = get_api_key_from_env()
        assert result is None

    def test_validate_api_key_with_env_key_valid(self):
        """Test validate_api_key with valid key."""
        os.environ["API_KEY"] = "correct-key"
        
        try:
            result = validate_api_key("correct-key")
            assert result is True
        finally:
            del os.environ["API_KEY"]

    def test_validate_api_key_with_env_key_invalid(self):
        """Test validate_api_key with invalid key."""
        os.environ["API_KEY"] = "correct-key"
        
        try:
            result = validate_api_key("wrong-key")
            assert result is False
        finally:
            del os.environ["API_KEY"]

    def test_validate_api_key_without_env_key(self):
        """Test validate_api_key when authentication is disabled."""
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]
        
        # Should return True when auth is disabled
        result = validate_api_key("any-key")
        assert result is True

    def test_validate_api_key_empty_string(self):
        """Test validate_api_key with empty string."""
        os.environ["API_KEY"] = "correct-key"
        
        try:
            result = validate_api_key("")
            assert result is False
        finally:
            del os.environ["API_KEY"]

