"""
Structured logging utilities for Schema Validator Pro.

This module provides structured JSON logging with:
- Request ID tracking
- Performance metrics
- Error context
- Log rotation
- Environment-based configuration
"""

import logging
import logging.handlers
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor


# Environment configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or console
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "schema-validator-pro.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 30))  # 30 files
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO 8601 timestamp to log entry."""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def add_environment(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add environment to log entry."""
    event_dict["environment"] = ENVIRONMENT
    return event_dict


def add_request_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add request ID if available in context."""
    # Request ID should be set in context by middleware
    if "request_id" not in event_dict:
        event_dict["request_id"] = str(uuid.uuid4())
    return event_dict


def censor_sensitive_data(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Remove sensitive data from logs."""
    sensitive_keys = ["password", "api_key", "token", "secret", "authorization"]
    
    def _censor_dict(d: Dict) -> Dict:
        """Recursively censor sensitive keys in dictionary."""
        censored = {}
        for key, value in d.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                censored[key] = "***REDACTED***"
            elif isinstance(value, dict):
                censored[key] = _censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [_censor_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                censored[key] = value
        return censored
    
    return _censor_dict(event_dict)


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    
    Sets up:
    - JSON or console output based on LOG_FORMAT
    - File rotation (10MB per file, 30 backups)
    - Environment-based log levels
    - Sensitive data censoring
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL),
    )
    
    # Create rotating file handler
    log_file_path = log_dir / LOG_FILE
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_timestamp,
        add_log_level,
        add_environment,
        add_request_id,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        censor_sensitive_data,
    ]
    
    # Add appropriate renderer based on format
    if LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, LOG_LEVEL)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured structlog logger
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)


class RequestLogger:
    """
    Context manager for logging API requests with timing.
    
    Example:
        >>> with RequestLogger("generate_schema", schema_type="Article") as log:
        >>>     result = generate_schema(...)
        >>>     log.add_context(completeness=95)
    """
    
    def __init__(self, operation: str, **context):
        """
        Initialize request logger.
        
        Args:
            operation: Operation name (e.g., "generate_schema")
            **context: Additional context to log
        """
        self.operation = operation
        self.context = context
        self.start_time = None
        self.logger = get_logger("request")
        self.request_id = str(uuid.uuid4())
    
    def __enter__(self):
        """Start timing and log request start."""
        self.start_time = time.time()
        self.logger.info(
            f"{self.operation}_started",
            request_id=self.request_id,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log request completion with duration."""
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"{self.operation}_completed",
                request_id=self.request_id,
                duration_ms=round(duration * 1000, 2),
                success=True,
                **self.context
            )
        else:
            self.logger.error(
                f"{self.operation}_failed",
                request_id=self.request_id,
                duration_ms=round(duration * 1000, 2),
                success=False,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                **self.context
            )
        
        return False  # Don't suppress exceptions
    
    def add_context(self, **kwargs):
        """Add additional context to be logged on completion."""
        self.context.update(kwargs)


class RetryLogger:
    """
    Logger for retry operations.
    
    Example:
        >>> retry_logger = RetryLogger("api_call")
        >>> retry_logger.log_attempt(1, delay=1.5, error="Connection timeout")
        >>> retry_logger.log_success(attempts=2, total_duration=3.2)
    """
    
    def __init__(self, operation: str, **context):
        """
        Initialize retry logger.
        
        Args:
            operation: Operation being retried
            **context: Additional context
        """
        self.operation = operation
        self.context = context
        self.logger = get_logger("retry")
        self.start_time = time.time()
    
    def log_attempt(self, attempt: int, delay: float, error: str, error_type: str = "unknown"):
        """
        Log a retry attempt.
        
        Args:
            attempt: Attempt number (1-based)
            delay: Delay before next retry in seconds
            error: Error message
            error_type: Type of error (retryable/non_retryable)
        """
        self.logger.warning(
            f"{self.operation}_retry_attempt",
            attempt=attempt,
            delay_seconds=round(delay, 2),
            error=error,
            error_type=error_type,
            **self.context
        )
    
    def log_success(self, attempts: int):
        """
        Log successful completion after retries.
        
        Args:
            attempts: Total number of attempts
        """
        duration = time.time() - self.start_time
        self.logger.info(
            f"{self.operation}_retry_success",
            total_attempts=attempts,
            total_duration_ms=round(duration * 1000, 2),
            **self.context
        )
    
    def log_failure(self, attempts: int, final_error: str):
        """
        Log final failure after all retries exhausted.
        
        Args:
            attempts: Total number of attempts
            final_error: Final error message
        """
        duration = time.time() - self.start_time
        self.logger.error(
            f"{self.operation}_retry_failed",
            total_attempts=attempts,
            total_duration_ms=round(duration * 1000, 2),
            final_error=final_error,
            **self.context
        )


# Initialize logging on module import
setup_logging()


# Export commonly used loggers
logger = get_logger(__name__)

