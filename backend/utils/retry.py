"""
Retry utilities with exponential backoff for Schema Validator Pro.

Provides decorators and utilities for implementing robust retry logic
with exponential backoff, jitter, and detailed logging.
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional
from enum import Enum

from backend.utils.logger import get_logger, RetryLogger
from backend.middleware.metrics import record_retry_attempt, record_retry_success, record_retry_failure

logger = get_logger(__name__)


class ErrorType(Enum):
    """Error classification for retry logic."""
    RETRYABLE = "retryable"  # Temporary errors that should be retried
    NON_RETRYABLE = "non_retryable"  # Permanent errors that should not be retried
    UNKNOWN = "unknown"  # Unknown errors, default to retry


def classify_error(exception: Exception) -> ErrorType:
    """
    Classify an exception as retryable or non-retryable.
    
    Args:
        exception: The exception to classify
        
    Returns:
        ErrorType indicating whether the error should be retried
    """
    # Non-retryable errors (client errors, validation errors)
    non_retryable = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
    )
    
    if isinstance(exception, non_retryable):
        return ErrorType.NON_RETRYABLE
    
    # Retryable errors (network errors, temporary failures)
    # Most exceptions are considered retryable by default
    return ErrorType.RETRYABLE


def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for retrying a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        jitter: Whether to add random jitter to delay (default: True)
        retryable_exceptions: Tuple of exception types to retry (default: all)
        on_retry: Callback function called on each retry (exception, attempt_number)
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @exponential_backoff(max_retries=3, base_delay=1.0)
        def fetch_data():
            # This will retry up to 3 times with exponential backoff
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is the last attempt
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Check if exception is retryable
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        logger.warning(
                            f"Function {func.__name__} raised non-retryable exception: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Classify error
                    error_type = classify_error(e)
                    if error_type == ErrorType.NON_RETRYABLE:
                        logger.warning(
                            f"Function {func.__name__} raised non-retryable error: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        import random
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def retry_with_timeout(
    max_retries: int = 3,
    timeout: float = 30.0,
    base_delay: float = 1.0,
):
    """
    Decorator for retrying a function with both retry limit and timeout.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout: Maximum total time in seconds for all attempts
        base_delay: Initial delay in seconds between retries
        
    Returns:
        Decorated function with retry and timeout logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.error(
                        f"Function {func.__name__} timed out after {elapsed:.2f} seconds "
                        f"({attempt} attempts)"
                    )
                    raise TimeoutError(
                        f"Operation timed out after {elapsed:.2f} seconds"
                    )
                
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise
                    
                    # Calculate remaining time
                    remaining_time = timeout - elapsed
                    delay = min(base_delay * (2 ** attempt), remaining_time / 2)
                    
                    if delay <= 0:
                        logger.error(
                            f"Function {func.__name__} timed out before retry"
                        )
                        raise TimeoutError("Operation timed out before retry")
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds (remaining: {remaining_time:.2f}s)..."
                    )
                    
                    time.sleep(delay)
            
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        timeout: Optional[float] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.timeout = timeout
    
    def to_dict(self):
        """Convert config to dictionary."""
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "exponential_base": self.exponential_base,
            "jitter": self.jitter,
            "timeout": self.timeout,
        }


# Default retry configuration for schema operations
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True,
)

