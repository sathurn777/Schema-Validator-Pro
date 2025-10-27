"""
Error models for Schema Validator Pro API.

Provides standardized error response format with retry guidance.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""
    
    # Client errors (4xx) - Non-retryable
    INVALID_REQUEST = "invalid_request"
    INVALID_SCHEMA_TYPE = "invalid_schema_type"
    VALIDATION_ERROR = "validation_error"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_FIELD_VALUE = "invalid_field_value"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    
    # Server errors (5xx) - Retryable
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT = "timeout"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Unknown errors
    UNKNOWN_ERROR = "unknown_error"


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Specific error code")
    value: Optional[Any] = Field(None, description="Invalid value that caused the error")


class ErrorResponse(BaseModel):
    """
    Standardized error response format.
    
    Provides consistent error structure with retry guidance.
    """
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    retryable: bool = Field(..., description="Whether the error is retryable")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    request_id: Optional[str] = Field(None, description="Request ID for debugging")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "invalid_schema_type",
                "message": "Unsupported schema type: BlogPost. Supported types: Article, Product, Organization, Event, Person, Recipe, FAQPage, HowTo, Course",
                "details": [
                    {
                        "field": "schema_type",
                        "message": "Invalid schema type",
                        "code": "invalid_value",
                        "value": "BlogPost"
                    }
                ],
                "retryable": False,
                "retry_after": None,
                "request_id": "req_123456",
                "timestamp": "2025-10-22T10:30:00Z"
            }
        }


def is_retryable_error(error_code: ErrorCode) -> bool:
    """
    Determine if an error code represents a retryable error.
    
    Args:
        error_code: The error code to check
        
    Returns:
        True if the error is retryable, False otherwise
    """
    retryable_codes = {
        ErrorCode.INTERNAL_ERROR,
        ErrorCode.SERVICE_UNAVAILABLE,
        ErrorCode.TIMEOUT,
        ErrorCode.RATE_LIMIT_EXCEEDED,
    }
    return error_code in retryable_codes


def get_retry_delay(error_code: ErrorCode) -> Optional[int]:
    """
    Get recommended retry delay for an error code.
    
    Args:
        error_code: The error code
        
    Returns:
        Recommended delay in seconds, or None if not retryable
    """
    retry_delays = {
        ErrorCode.RATE_LIMIT_EXCEEDED: 60,  # Wait 1 minute
        ErrorCode.SERVICE_UNAVAILABLE: 30,  # Wait 30 seconds
        ErrorCode.TIMEOUT: 10,  # Wait 10 seconds
        ErrorCode.INTERNAL_ERROR: 5,  # Wait 5 seconds
    }
    return retry_delays.get(error_code)


def create_error_response(
    error_code: ErrorCode,
    message: str,
    details: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """
    Create a standardized error response.
    
    Args:
        error_code: The error code
        message: Human-readable error message
        details: Optional detailed error information
        request_id: Optional request ID for debugging
        
    Returns:
        ErrorResponse object
    """
    from datetime import datetime
    
    return ErrorResponse(
        error=error_code.value,
        message=message,
        details=details,
        retryable=is_retryable_error(error_code),
        retry_after=get_retry_delay(error_code),
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


class ValidationErrorResponse(BaseModel):
    """Response for validation errors with field-level details."""
    
    error: str = Field(default="validation_error", description="Error code")
    message: str = Field(..., description="Human-readable error message")
    errors: List[ErrorDetail] = Field(..., description="List of validation errors")
    retryable: bool = Field(default=False, description="Validation errors are not retryable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Request validation failed",
                "errors": [
                    {
                        "field": "schema_type",
                        "message": "Field required",
                        "code": "missing_field"
                    },
                    {
                        "field": "content",
                        "message": "String should have at least 1 character",
                        "code": "string_too_short",
                        "value": ""
                    }
                ],
                "retryable": False
            }
        }

