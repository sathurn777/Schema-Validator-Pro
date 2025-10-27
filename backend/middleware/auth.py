"""
API Authentication Middleware
Provides optional API key authentication for production environments.
"""

import os
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


# API Key header name
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate API key for all requests.
    
    If API_KEY environment variable is set, all requests must include
    a valid X-API-Key header. If not set, authentication is disabled.
    """
    
    def __init__(self, app, api_key: Optional[str] = None):
        super().__init__(app)
        self.api_key = api_key or os.getenv("API_KEY")
        self.enabled = bool(self.api_key)
        
        # Public endpoints that don't require authentication
        self.public_endpoints = {
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Validate API key before processing request."""
        
        # Skip authentication if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip authentication for public endpoints
        if request.url.path in self.public_endpoints:
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        # Validate API key
        if not api_key or api_key != self.api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"},
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Process request
        return await call_next(request)


def get_api_key_from_env() -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv("API_KEY")


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key against environment variable.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    expected_key = get_api_key_from_env()
    if not expected_key:
        # Authentication disabled
        return True
    return api_key == expected_key

