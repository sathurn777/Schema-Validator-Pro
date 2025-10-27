"""
Prometheus metrics middleware for Schema Validator Pro.

Collects and exposes performance metrics:
- Request count by endpoint, method, status
- Request duration (p50, p95, p99)
- Retry rate
- Cache hit rate
- Schema generation time by type
- Error rate
"""

import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# Create custom registry to avoid conflicts
registry = CollectorRegistry()

# Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
    registry=registry,
)

# Schema generation metrics
schema_generation_total = Counter(
    "schema_generation_total",
    "Total schema generation requests",
    ["schema_type", "status"],
    registry=registry,
)

schema_generation_duration_seconds = Histogram(
    "schema_generation_duration_seconds",
    "Schema generation duration in seconds",
    ["schema_type"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=registry,
)

schema_completeness_score = Histogram(
    "schema_completeness_score",
    "Schema completeness score distribution",
    ["schema_type"],
    buckets=(0, 20, 40, 60, 80, 90, 95, 100),
    registry=registry,
)

# Retry metrics
retry_attempts_total = Counter(
    "retry_attempts_total",
    "Total retry attempts",
    ["operation", "error_type"],
    registry=registry,
)

retry_success_total = Counter(
    "retry_success_total",
    "Total successful retries",
    ["operation"],
    registry=registry,
)

retry_failure_total = Counter(
    "retry_failure_total",
    "Total failed retries (exhausted)",
    ["operation"],
    registry=registry,
)

# Cache metrics
cache_requests_total = Counter(
    "cache_requests_total",
    "Total cache requests",
    ["operation", "result"],
    registry=registry,
)

cache_hit_rate = Gauge(
    "cache_hit_rate",
    "Cache hit rate (0-1)",
    registry=registry,
)

# Error metrics
errors_total = Counter(
    "errors_total",
    "Total errors",
    ["error_type", "error_code"],
    registry=registry,
)

# Health metrics
health_status = Gauge(
    "health_status",
    "Health status (1=healthy, 0=unhealthy)",
    ["component"],
    registry=registry,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all HTTP requests.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and collect metrics.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
        
        Returns:
            Response from handler
        """
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Extract endpoint and method
        endpoint = request.url.path
        method = request.method
        
        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            status_code = response.status_code
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)
            
            return response
        
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500,
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)
            
            errors_total.labels(
                error_type=type(e).__name__,
                error_code="internal_error",
            ).inc()
            
            raise
        
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


def record_schema_generation(
    schema_type: str,
    duration: float,
    completeness: float,
    success: bool,
):
    """
    Record schema generation metrics.
    
    Args:
        schema_type: Type of schema (Article, Product, etc.)
        duration: Generation duration in seconds
        completeness: Completeness score (0-100)
        success: Whether generation was successful
    """
    status = "success" if success else "failure"
    
    schema_generation_total.labels(
        schema_type=schema_type,
        status=status,
    ).inc()
    
    if success:
        schema_generation_duration_seconds.labels(
            schema_type=schema_type,
        ).observe(duration)
        
        schema_completeness_score.labels(
            schema_type=schema_type,
        ).observe(completeness)


def record_retry_attempt(operation: str, error_type: str):
    """
    Record a retry attempt.
    
    Args:
        operation: Operation being retried
        error_type: Type of error that triggered retry
    """
    retry_attempts_total.labels(
        operation=operation,
        error_type=error_type,
    ).inc()


def record_retry_success(operation: str):
    """
    Record successful retry.
    
    Args:
        operation: Operation that succeeded after retry
    """
    retry_success_total.labels(operation=operation).inc()


def record_retry_failure(operation: str):
    """
    Record failed retry (all attempts exhausted).
    
    Args:
        operation: Operation that failed after all retries
    """
    retry_failure_total.labels(operation=operation).inc()


def record_cache_access(operation: str, hit: bool):
    """
    Record cache access.
    
    Args:
        operation: Cache operation
        hit: Whether cache was hit
    """
    result = "hit" if hit else "miss"
    cache_requests_total.labels(
        operation=operation,
        result=result,
    ).inc()
    
    # Update hit rate (simple moving average)
    # In production, use a proper time-windowed calculation
    total_hits = cache_requests_total.labels(operation=operation, result="hit")._value.get()
    total_misses = cache_requests_total.labels(operation=operation, result="miss")._value.get()
    total = total_hits + total_misses
    
    if total > 0:
        hit_rate = total_hits / total
        cache_hit_rate.set(hit_rate)


def record_error(error_type: str, error_code: str):
    """
    Record an error.
    
    Args:
        error_type: Type of error (ValueError, RuntimeError, etc.)
        error_code: Error code (invalid_request, internal_error, etc.)
    """
    errors_total.labels(
        error_type=error_type,
        error_code=error_code,
    ).inc()


def set_health_status(component: str, healthy: bool):
    """
    Set health status for a component.
    
    Args:
        component: Component name (api, database, cache, etc.)
        healthy: Whether component is healthy
    """
    health_status.labels(component=component).set(1 if healthy else 0)


def get_metrics() -> bytes:
    """
    Get Prometheus metrics in text format.
    
    Returns:
        Metrics in Prometheus text format
    """
    return generate_latest(registry)


def get_metrics_content_type() -> str:
    """
    Get content type for metrics response.
    
    Returns:
        Content type string
    """
    return CONTENT_TYPE_LATEST

