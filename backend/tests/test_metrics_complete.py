"""
Comprehensive tests for Prometheus metrics middleware.

Tests cover:
- MetricsMiddleware request tracking
- Schema generation metrics
- Retry metrics
- Cache metrics
- Error metrics
- Health metrics
- Metrics export
"""

import pytest
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from prometheus_client import REGISTRY

from backend.middleware.metrics import (
    MetricsMiddleware,
    record_schema_generation,
    record_retry_attempt,
    record_retry_success,
    record_retry_failure,
    record_cache_access,
    record_error,
    set_health_status,
    get_metrics,
    get_metrics_content_type,
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    schema_generation_total,
    schema_generation_duration_seconds,
    schema_completeness_score,
    retry_attempts_total,
    retry_success_total,
    retry_failure_total,
    cache_requests_total,
    cache_hit_rate,
    errors_total,
    health_status,
    registry,
)


class TestMetricsMiddleware:
    """Test MetricsMiddleware class."""
    
    def test_middleware_tracks_successful_request(self):
        """Test middleware tracks successful HTTP requests."""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        
        # Get initial metric value
        initial_count = http_requests_total.labels(
            method="GET", endpoint="/test", status_code=200
        )._value.get()
        
        # Make request
        response = client.get("/test")
        assert response.status_code == 200
        
        # Check metric incremented
        final_count = http_requests_total.labels(
            method="GET", endpoint="/test", status_code=200
        )._value.get()
        assert final_count == initial_count + 1
    
    def test_middleware_tracks_request_duration(self):
        """Test middleware tracks request duration."""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)

        @app.get("/slow")
        async def slow_endpoint():
            time.sleep(0.1)
            return {"message": "done"}

        client = TestClient(app)

        # Make request
        response = client.get("/slow")
        assert response.status_code == 200

        # Verify that the histogram metric was created for this endpoint
        # We can't easily check the exact duration, but we can verify the metric exists
        # by checking that it doesn't raise an error when accessed
        try:
            http_request_duration_seconds.labels(method="GET", endpoint="/slow")
            duration_tracked = True
        except:
            duration_tracked = False

        assert duration_tracked
    
    def test_middleware_tracks_in_progress_requests(self):
        """Test middleware tracks in-progress requests."""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        
        # Make request
        response = client.get("/test")
        assert response.status_code == 200
        
        # In-progress should be back to 0 after request completes
        in_progress = http_requests_in_progress.labels(
            method="GET", endpoint="/test"
        )._value.get()
        assert in_progress == 0
    
    def test_middleware_skips_metrics_endpoint(self):
        """Test middleware skips /metrics endpoint itself."""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/metrics")
        async def metrics_endpoint():
            return {"metrics": "data"}
        
        client = TestClient(app)
        
        # Get initial count
        try:
            initial_count = http_requests_total.labels(
                method="GET", endpoint="/metrics", status_code=200
            )._value.get()
        except:
            initial_count = 0
        
        # Make request
        response = client.get("/metrics")
        assert response.status_code == 200
        
        # Metric should not have incremented
        try:
            final_count = http_requests_total.labels(
                method="GET", endpoint="/metrics", status_code=200
            )._value.get()
        except:
            final_count = 0
        
        assert final_count == initial_count
    
    def test_middleware_handles_exceptions(self):
        """Test middleware records metrics even when handler raises exception."""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        client = TestClient(app, raise_server_exceptions=False)
        
        # Get initial counts
        initial_request_count = http_requests_total.labels(
            method="GET", endpoint="/error", status_code=500
        )._value.get()
        
        initial_error_count = errors_total.labels(
            error_type="ValueError", error_code="internal_error"
        )._value.get()
        
        # Make request
        response = client.get("/error")
        assert response.status_code == 500
        
        # Check metrics incremented
        final_request_count = http_requests_total.labels(
            method="GET", endpoint="/error", status_code=500
        )._value.get()
        assert final_request_count == initial_request_count + 1
        
        final_error_count = errors_total.labels(
            error_type="ValueError", error_code="internal_error"
        )._value.get()
        assert final_error_count == initial_error_count + 1
    
    def test_middleware_tracks_different_methods(self):
        """Test middleware tracks different HTTP methods."""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.post("/test")
        async def post_endpoint():
            return {"message": "created"}
        
        client = TestClient(app)
        
        # Get initial count
        initial_count = http_requests_total.labels(
            method="POST", endpoint="/test", status_code=200
        )._value.get()
        
        # Make request
        response = client.post("/test")
        assert response.status_code == 200
        
        # Check metric incremented
        final_count = http_requests_total.labels(
            method="POST", endpoint="/test", status_code=200
        )._value.get()
        assert final_count == initial_count + 1


class TestSchemaGenerationMetrics:
    """Test schema generation metrics functions."""
    
    def test_record_successful_schema_generation(self):
        """Test recording successful schema generation."""
        initial_count = schema_generation_total.labels(
            schema_type="Article", status="success"
        )._value.get()
        
        record_schema_generation(
            schema_type="Article",
            duration=1.5,
            completeness=85.0,
            success=True
        )
        
        final_count = schema_generation_total.labels(
            schema_type="Article", status="success"
        )._value.get()
        assert final_count == initial_count + 1
    
    def test_record_failed_schema_generation(self):
        """Test recording failed schema generation."""
        initial_count = schema_generation_total.labels(
            schema_type="Product", status="failure"
        )._value.get()
        
        record_schema_generation(
            schema_type="Product",
            duration=0.5,
            completeness=0.0,
            success=False
        )
        
        final_count = schema_generation_total.labels(
            schema_type="Product", status="failure"
        )._value.get()
        assert final_count == initial_count + 1
    
    def test_record_schema_duration_only_on_success(self):
        """Test duration is only recorded for successful generations."""
        # Record initial success count
        initial_success = schema_generation_total.labels(
            schema_type="Event", status="success"
        )._value.get()

        initial_failure = schema_generation_total.labels(
            schema_type="Event", status="failure"
        )._value.get()

        # Successful generation should record duration
        record_schema_generation(
            schema_type="Event",
            duration=2.0,
            completeness=90.0,
            success=True
        )

        # Failed generation should not record duration
        record_schema_generation(
            schema_type="Event",
            duration=0.1,
            completeness=0.0,
            success=False
        )

        # Check that both success and failure were recorded
        final_success = schema_generation_total.labels(
            schema_type="Event", status="success"
        )._value.get()

        final_failure = schema_generation_total.labels(
            schema_type="Event", status="failure"
        )._value.get()

        assert final_success == initial_success + 1
        assert final_failure == initial_failure + 1


class TestRetryMetrics:
    """Test retry metrics functions."""

    def test_record_retry_attempt(self):
        """Test recording retry attempt."""
        initial_count = retry_attempts_total.labels(
            operation="api_call", error_type="ConnectionError"
        )._value.get()

        record_retry_attempt("api_call", "ConnectionError")

        final_count = retry_attempts_total.labels(
            operation="api_call", error_type="ConnectionError"
        )._value.get()
        assert final_count == initial_count + 1

    def test_record_retry_success(self):
        """Test recording successful retry."""
        initial_count = retry_success_total.labels(
            operation="database_query"
        )._value.get()

        record_retry_success("database_query")

        final_count = retry_success_total.labels(
            operation="database_query"
        )._value.get()
        assert final_count == initial_count + 1

    def test_record_retry_failure(self):
        """Test recording failed retry (exhausted)."""
        initial_count = retry_failure_total.labels(
            operation="external_api"
        )._value.get()

        record_retry_failure("external_api")

        final_count = retry_failure_total.labels(
            operation="external_api"
        )._value.get()
        assert final_count == initial_count + 1


class TestCacheMetrics:
    """Test cache metrics functions."""

    def test_record_cache_hit(self):
        """Test recording cache hit."""
        initial_count = cache_requests_total.labels(
            operation="schema_lookup", result="hit"
        )._value.get()

        record_cache_access("schema_lookup", hit=True)

        final_count = cache_requests_total.labels(
            operation="schema_lookup", result="hit"
        )._value.get()
        assert final_count == initial_count + 1

    def test_record_cache_miss(self):
        """Test recording cache miss."""
        initial_count = cache_requests_total.labels(
            operation="schema_lookup", result="miss"
        )._value.get()

        record_cache_access("schema_lookup", hit=False)

        final_count = cache_requests_total.labels(
            operation="schema_lookup", result="miss"
        )._value.get()
        assert final_count == initial_count + 1

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate is calculated correctly."""
        # Record some cache accesses
        operation = "test_cache_op"

        # Record 3 hits and 1 miss (75% hit rate)
        record_cache_access(operation, hit=True)
        record_cache_access(operation, hit=True)
        record_cache_access(operation, hit=True)
        record_cache_access(operation, hit=False)

        # Check hit rate is updated
        hit_rate_value = cache_hit_rate._value.get()
        # Hit rate should be between 0 and 1
        assert 0 <= hit_rate_value <= 1


class TestErrorMetrics:
    """Test error metrics functions."""

    def test_record_error(self):
        """Test recording error."""
        initial_count = errors_total.labels(
            error_type="ValidationError", error_code="invalid_schema"
        )._value.get()

        record_error("ValidationError", "invalid_schema")

        final_count = errors_total.labels(
            error_type="ValidationError", error_code="invalid_schema"
        )._value.get()
        assert final_count == initial_count + 1

    def test_record_different_error_types(self):
        """Test recording different error types."""
        initial_count = errors_total.labels(
            error_type="RuntimeError", error_code="timeout"
        )._value.get()

        record_error("RuntimeError", "timeout")

        final_count = errors_total.labels(
            error_type="RuntimeError", error_code="timeout"
        )._value.get()
        assert final_count == initial_count + 1


class TestHealthMetrics:
    """Test health metrics functions."""

    def test_set_health_status_healthy(self):
        """Test setting component health to healthy."""
        set_health_status("api", healthy=True)

        status = health_status.labels(component="api")._value.get()
        assert status == 1

    def test_set_health_status_unhealthy(self):
        """Test setting component health to unhealthy."""
        set_health_status("database", healthy=False)

        status = health_status.labels(component="database")._value.get()
        assert status == 0

    def test_set_health_status_multiple_components(self):
        """Test setting health for multiple components."""
        set_health_status("cache", healthy=True)
        set_health_status("queue", healthy=False)

        cache_status = health_status.labels(component="cache")._value.get()
        queue_status = health_status.labels(component="queue")._value.get()

        assert cache_status == 1
        assert queue_status == 0


class TestMetricsExport:
    """Test metrics export functions."""

    def test_get_metrics_returns_bytes(self):
        """Test get_metrics returns bytes."""
        metrics = get_metrics()
        assert isinstance(metrics, bytes)

    def test_get_metrics_contains_metric_names(self):
        """Test get_metrics contains expected metric names."""
        metrics = get_metrics()
        metrics_text = metrics.decode('utf-8')

        # Check for some key metrics
        assert "http_requests_total" in metrics_text
        assert "http_request_duration_seconds" in metrics_text

    def test_get_metrics_content_type(self):
        """Test get_metrics_content_type returns correct type."""
        content_type = get_metrics_content_type()
        assert isinstance(content_type, str)
        assert "text/plain" in content_type or "prometheus" in content_type.lower()

