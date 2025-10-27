"""
Schema Validator Pro - FastAPI Backend
Simple and focused backend for WordPress schema generation and validation.
"""

import os
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.services.schema_generator import SchemaGenerator
from backend.routers.schema import router as schema_router
from backend.middleware.auth import APIKeyMiddleware
from backend.middleware.metrics import MetricsMiddleware, get_metrics, get_metrics_content_type, set_health_status
from backend.utils.logger import get_logger, setup_logging
from starlette.responses import Response

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize Sentry (if DSN is configured)
SENTRY_DSN = os.getenv("SENTRY_DSN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0" if ENVIRONMENT == "production" else "0.0"))

if SENTRY_DSN:
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        traces_sample_rate=SENTRY_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_SAMPLE_RATE,
        enable_tracing=True,
        integrations=[
            StarletteIntegration(),
        ],
        # Don't send PII
        send_default_pii=False,
        # Set release version
        release=f"schema-validator-pro@1.0.0",
    )
    logger.info("sentry_initialized", environment=ENVIRONMENT, sample_rate=SENTRY_SAMPLE_RATE)
else:
    logger.warning("sentry_not_configured", message="SENTRY_DSN not set, error tracking disabled")

# Initialize FastAPI app
app = FastAPI(
    title="Schema Validator Pro API",
    description="WordPress Schema.org Auto-Injection Tool",
    version="1.0.0",
)


# Request body size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent abuse."""
    from fastapi import HTTPException, status

    # Maximum request body size: 10MB
    MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB default

    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            logger.warning(
                "request_too_large",
                content_length=content_length,
                max_size=MAX_REQUEST_SIZE,
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum size: {MAX_REQUEST_SIZE} bytes"
            )

    response = await call_next(request)
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing and status."""
    import time
    import uuid

    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log request start
    start_time = time.time()
    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )

    # Process request
    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log request completion
        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log request error
        logger.error(
            "request_failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


# Add metrics middleware (if enabled)
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
if ENABLE_METRICS:
    app.add_middleware(MetricsMiddleware)
    logger.info("metrics_enabled", message="Prometheus metrics enabled at /metrics")

# Add API Key authentication middleware (optional, enabled via API_KEY env var)
app.add_middleware(APIKeyMiddleware)

# Add CORS middleware - SECURITY: Use environment variable for allowed origins
# Default to localhost for development, MUST be configured for production
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# Include routers
app.include_router(schema_router)


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Schema Validator Pro",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    # Update health metrics
    set_health_status("api", True)
    set_health_status("schema_generator", True)

    return {
        "status": "healthy",
        "services": {"schema_generator": "ok", "schema_validator": "ok"},
        "supported_types": SchemaGenerator().get_supported_types(),
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.
    """
    if not ENABLE_METRICS:
        return {"error": "Metrics disabled"}

    return Response(
        content=get_metrics(),
        media_type=get_metrics_content_type(),
    )


def main():
    """
    Main entry point for the CLI.

    Starts the FastAPI server with uvicorn.
    """
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(
        description="Schema Validator Pro - Production-ready Schema.org JSON-LD validator and generator"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Schema Validator Pro 1.0.0"
    )

    args = parser.parse_args()

    logger.info(
        "starting_server",
        host=args.host,
        port=args.port,
        reload=args.reload,
        version="1.0.0"
    )

    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()

