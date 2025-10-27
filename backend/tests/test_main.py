"""
Comprehensive tests for main.py - FastAPI application initialization and endpoints.

Target: 90%+ coverage for main.py (currently 0%)
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestFastAPIApp:
    """Test FastAPI application initialization"""

    @pytest.fixture
    def client(self):
        """Create test client with clean environment"""
        # Clear environment variables
        env_vars = ["SENTRY_DSN", "ENABLE_METRICS", "ALLOWED_ORIGINS", "API_KEY"]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Import app after clearing env vars
        from backend.main import app
        return TestClient(app)

    @pytest.fixture
    def client_with_metrics(self):
        """Create test client with metrics enabled"""
        os.environ["ENABLE_METRICS"] = "true"
        from backend.main import app
        return TestClient(app)

    @pytest.fixture
    def client_without_metrics(self):
        """Create test client with metrics disabled"""
        os.environ["ENABLE_METRICS"] = "false"
        # Need to reload the module to pick up new env var
        import importlib
        import backend.main
        importlib.reload(backend.main)
        return TestClient(backend.main.app)

    def test_app_initialization(self, client):
        """Test that FastAPI app initializes correctly"""
        from backend.main import app
        
        assert app is not None
        assert app.title == "Schema Validator Pro API"
        assert app.description == "WordPress Schema.org Auto-Injection Tool"
        assert app.version == "1.0.0"

    def test_root_endpoint(self, client):
        """Test root health check endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Schema Validator Pro"
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self, client):
        """Test detailed health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert data["services"]["schema_generator"] == "ok"
        assert data["services"]["schema_validator"] == "ok"
        assert "supported_types" in data
        assert len(data["supported_types"]) > 0

    def test_health_endpoint_sets_health_status(self, client):
        """Test that health endpoint updates health metrics"""
        with patch("backend.main.set_health_status") as mock_set_health:
            response = client.get("/health")
            
            assert response.status_code == 200
            # Should call set_health_status twice
            assert mock_set_health.call_count == 2
            mock_set_health.assert_any_call("api", True)
            mock_set_health.assert_any_call("schema_generator", True)

    def test_metrics_endpoint_enabled(self, client_with_metrics):
        """Test metrics endpoint when metrics are enabled"""
        response = client_with_metrics.get("/metrics")
        
        assert response.status_code == 200
        # Metrics should be in Prometheus text format
        assert response.headers["content-type"].startswith("text/plain")

    def test_metrics_endpoint_disabled(self, client_without_metrics):
        """Test metrics endpoint when metrics are disabled"""
        response = client_without_metrics.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Metrics disabled"

    def test_cors_middleware_configured(self, client):
        """Test that CORS middleware is properly configured"""
        # Make an OPTIONS request to check CORS headers
        response = client.options("/", headers={"Origin": "http://localhost"})
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers

    def test_cors_allowed_origins_default(self):
        """Test default CORS allowed origins"""
        # Clear ALLOWED_ORIGINS env var
        if "ALLOWED_ORIGINS" in os.environ:
            del os.environ["ALLOWED_ORIGINS"]
        
        from backend.main import app
        client = TestClient(app)
        
        # Test with localhost origin
        response = client.get("/", headers={"Origin": "http://localhost"})
        assert response.status_code == 200

    def test_cors_allowed_origins_custom(self):
        """Test custom CORS allowed origins"""
        os.environ["ALLOWED_ORIGINS"] = "https://example.com,https://test.com"
        
        # Reload module to pick up new env var
        import importlib
        import backend.main
        importlib.reload(backend.main)
        
        client = TestClient(backend.main.app)
        response = client.get("/", headers={"Origin": "https://example.com"})
        assert response.status_code == 200

    def test_request_logging_middleware(self, client):
        """Test that request logging middleware adds request ID"""
        response = client.get("/")
        
        # Should have X-Request-ID header
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0

    def test_request_logging_middleware_on_error(self, client):
        """Test request logging middleware handles errors"""
        # Make request to non-existent endpoint
        response = client.get("/nonexistent")
        
        # Should still have request ID even on error
        assert "x-request-id" in response.headers

    def test_api_key_middleware_added(self, client):
        """Test that API key middleware is added to app"""
        from backend.main import app
        from backend.middleware.auth import APIKeyMiddleware

        # Check that APIKeyMiddleware is in the middleware stack
        # FastAPI wraps middleware in Middleware objects, check middleware_class attribute
        middleware_classes = [m.cls.__name__ if hasattr(m, 'cls') else type(m).__name__
                             for m in app.user_middleware]
        assert "APIKeyMiddleware" in middleware_classes

    def test_metrics_middleware_added_when_enabled(self):
        """Test that metrics middleware is added when enabled"""
        os.environ["ENABLE_METRICS"] = "true"

        import importlib
        import backend.main
        importlib.reload(backend.main)

        # FastAPI wraps middleware in Middleware objects, check middleware_class attribute
        middleware_classes = [m.cls.__name__ if hasattr(m, 'cls') else type(m).__name__
                             for m in backend.main.app.user_middleware]
        assert "MetricsMiddleware" in middleware_classes

    def test_schema_router_included(self, client):
        """Test that schema router is included"""
        # Test a schema endpoint exists (correct prefix is /api/v1/schema)
        response = client.post(
            "/api/v1/schema/generate",
            json={
                "content": "Test content",
                "schema_type": "Article",
                "url": "https://example.com/test"
            }
        )

        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

    @patch.dict(os.environ, {"SENTRY_DSN": "https://test@sentry.io/123"})
    def test_sentry_initialization_with_dsn(self):
        """Test Sentry initialization when DSN is configured"""
        with patch("sentry_sdk.init") as mock_sentry_init:
            import importlib
            import backend.main
            importlib.reload(backend.main)

            # Sentry should be initialized
            mock_sentry_init.assert_called_once()
            call_kwargs = mock_sentry_init.call_args[1]
            assert call_kwargs["dsn"] == "https://test@sentry.io/123"
            assert call_kwargs["environment"] == "development"
            assert call_kwargs["send_default_pii"] is False

    def test_sentry_not_initialized_without_dsn(self):
        """Test Sentry is not initialized when DSN is not configured"""
        # Clear SENTRY_DSN
        if "SENTRY_DSN" in os.environ:
            del os.environ["SENTRY_DSN"]

        with patch("sentry_sdk.init") as mock_sentry_init:
            import importlib
            import backend.main
            importlib.reload(backend.main)

            # Sentry should NOT be initialized
            mock_sentry_init.assert_not_called()

    @patch.dict(os.environ, {"SENTRY_DSN": "https://test@sentry.io/123", "ENVIRONMENT": "production"})
    def test_sentry_production_sample_rate(self):
        """Test Sentry uses correct sample rate in production"""
        with patch("sentry_sdk.init") as mock_sentry_init:
            import importlib
            import backend.main
            importlib.reload(backend.main)

            call_kwargs = mock_sentry_init.call_args[1]
            assert call_kwargs["environment"] == "production"
            assert call_kwargs["traces_sample_rate"] == 1.0
            assert call_kwargs["profiles_sample_rate"] == 1.0

    @patch.dict(os.environ, {"SENTRY_DSN": "https://test@sentry.io/123", "ENVIRONMENT": "development"})
    def test_sentry_development_sample_rate(self):
        """Test Sentry uses correct sample rate in development"""
        with patch("sentry_sdk.init") as mock_sentry_init:
            import importlib
            import backend.main
            importlib.reload(backend.main)

            call_kwargs = mock_sentry_init.call_args[1]
            assert call_kwargs["environment"] == "development"
            assert call_kwargs["traces_sample_rate"] == 0.0
            assert call_kwargs["profiles_sample_rate"] == 0.0

    def test_logging_setup_called(self):
        """Test that logging setup is called on module import"""
        # Need to patch before importing
        with patch("backend.utils.logger.setup_logging") as mock_setup:
            import importlib
            import sys

            # Remove module from cache to force reimport
            if "backend.main" in sys.modules:
                del sys.modules["backend.main"]

            import backend.main

            # setup_logging should have been called during module import
            mock_setup.assert_called_once()

    def test_supported_http_methods(self, client):
        """Test that only allowed HTTP methods are supported"""
        # GET should work
        response = client.get("/")
        assert response.status_code == 200
        
        # POST should work for schema endpoints
        response = client.post(
            "/api/schema/generate",
            json={"content": "test", "schema_type": "Article", "title": "Test"}
        )
        assert response.status_code != 405  # Not "Method Not Allowed"
        
        # OPTIONS should work (CORS preflight)
        response = client.options("/")
        assert response.status_code in [200, 405]  # Depends on endpoint

    def test_request_id_unique_per_request(self, client):
        """Test that each request gets a unique request ID"""
        response1 = client.get("/")
        response2 = client.get("/")
        
        request_id1 = response1.headers.get("x-request-id")
        request_id2 = response2.headers.get("x-request-id")
        
        assert request_id1 != request_id2

    def test_request_logging_includes_client_ip(self, client):
        """Test that request logging includes client IP"""
        with patch("backend.main.logger.info") as mock_log:
            response = client.get("/")
            
            # Check that logger.info was called with client_ip
            assert mock_log.called
            # Find the request_started log call
            for call in mock_log.call_args_list:
                if call[0][0] == "request_started":
                    assert "client_ip" in call[1]

    def test_request_logging_includes_duration(self, client):
        """Test that request logging includes duration"""
        with patch("backend.main.logger.info") as mock_log:
            response = client.get("/")

            # Find the request_completed log call
            for call in mock_log.call_args_list:
                if call[0][0] == "request_completed":
                    assert "duration_ms" in call[1]
                    assert call[1]["duration_ms"] >= 0

    def test_request_logging_middleware_exception_handling(self, client):
        """Test that middleware logs exceptions properly"""
        from backend.main import app

        # Add a route that raises an exception
        @app.get("/test-exception")
        async def test_exception():
            raise ValueError("Test exception")

        # Make request that will raise exception
        with pytest.raises(ValueError):
            client.get("/test-exception")

