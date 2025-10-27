"""
Tests for retry utilities.
"""

import pytest
import time
from backend.utils.retry import (
    exponential_backoff,
    retry_with_timeout,
    classify_error,
    ErrorType,
    RetryConfig,
)


class TestErrorClassification:
    """Test error classification logic."""
    
    def test_classify_value_error_as_non_retryable(self):
        """ValueError should be classified as non-retryable."""
        error = ValueError("Invalid input")
        assert classify_error(error) == ErrorType.NON_RETRYABLE
    
    def test_classify_type_error_as_non_retryable(self):
        """TypeError should be classified as non-retryable."""
        error = TypeError("Wrong type")
        assert classify_error(error) == ErrorType.NON_RETRYABLE
    
    def test_classify_runtime_error_as_retryable(self):
        """RuntimeError should be classified as retryable."""
        error = RuntimeError("Temporary failure")
        assert classify_error(error) == ErrorType.RETRYABLE
    
    def test_classify_connection_error_as_retryable(self):
        """ConnectionError should be classified as retryable."""
        error = ConnectionError("Network failure")
        assert classify_error(error) == ErrorType.RETRYABLE


class TestExponentialBackoff:
    """Test exponential backoff decorator."""
    
    def test_successful_call_no_retry(self):
        """Successful call should not retry."""
        call_count = [0]
        
        @exponential_backoff(max_retries=3, base_delay=0.1)
        def successful_function():
            call_count[0] += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count[0] == 1
    
    def test_retry_on_retryable_error(self):
        """Should retry on retryable errors."""
        call_count = [0]
        
        @exponential_backoff(max_retries=2, base_delay=0.1, jitter=False)
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise RuntimeError("Temporary failure")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count[0] == 3  # Initial + 2 retries
    
    def test_no_retry_on_non_retryable_error(self):
        """Should not retry on non-retryable errors."""
        call_count = [0]
        
        @exponential_backoff(max_retries=3, base_delay=0.1)
        def failing_function():
            call_count[0] += 1
            raise ValueError("Invalid input")
        
        with pytest.raises(ValueError):
            failing_function()
        
        assert call_count[0] == 1  # No retries
    
    def test_max_retries_exceeded(self):
        """Should raise error after max retries."""
        call_count = [0]
        
        @exponential_backoff(max_retries=2, base_delay=0.1)
        def always_failing():
            call_count[0] += 1
            raise RuntimeError("Always fails")
        
        with pytest.raises(RuntimeError):
            always_failing()
        
        assert call_count[0] == 3  # Initial + 2 retries
    
    def test_exponential_delay(self):
        """Should use exponential backoff for delays."""
        call_times = []
        
        @exponential_backoff(max_retries=2, base_delay=0.1, jitter=False)
        def failing_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise RuntimeError("Temporary failure")
            return "success"
        
        failing_function()
        
        # Check delays are approximately exponential
        # First retry: ~0.1s, Second retry: ~0.2s
        assert len(call_times) == 3
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert 0.08 < delay1 < 0.15  # ~0.1s ±50%
        assert 0.15 < delay2 < 0.30  # ~0.2s ±50%
    
    def test_retry_callback(self):
        """Should call retry callback on each retry."""
        retry_info = []
        
        def on_retry(exception, attempt):
            retry_info.append((str(exception), attempt))
        
        @exponential_backoff(max_retries=2, base_delay=0.1, on_retry=on_retry)
        def failing_function():
            if len(retry_info) < 2:
                raise RuntimeError("Temporary failure")
            return "success"
        
        failing_function()
        
        assert len(retry_info) == 2
        assert retry_info[0][1] == 1  # First retry
        assert retry_info[1][1] == 2  # Second retry


class TestRetryWithTimeout:
    """Test retry with timeout decorator."""
    
    def test_successful_call_within_timeout(self):
        """Successful call within timeout should work."""
        @retry_with_timeout(max_retries=3, timeout=5.0, base_delay=0.1)
        def quick_function():
            return "success"
        
        result = quick_function()
        assert result == "success"
    
    def test_timeout_exceeded(self):
        """Should raise TimeoutError when timeout is exceeded."""
        @retry_with_timeout(max_retries=10, timeout=0.3, base_delay=0.1)
        def slow_function():
            time.sleep(0.15)
            raise RuntimeError("Slow failure")
        
        with pytest.raises(TimeoutError):
            slow_function()
    
    def test_retry_within_timeout(self):
        """Should retry within timeout limit."""
        call_count = [0]
        
        @retry_with_timeout(max_retries=5, timeout=1.0, base_delay=0.1)
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise RuntimeError("Temporary failure")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count[0] == 3


class TestRetryConfig:
    """Test RetryConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert config.timeout is None
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False,
            timeout=30.0,
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False
        assert config.timeout == 30.0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = RetryConfig(max_retries=5, base_delay=2.0)
        config_dict = config.to_dict()
        
        assert config_dict["max_retries"] == 5
        assert config_dict["base_delay"] == 2.0
        assert "max_delay" in config_dict
        assert "exponential_base" in config_dict
        assert "jitter" in config_dict
        assert "timeout" in config_dict


class TestIntegration:
    """Integration tests for retry functionality."""
    
    def test_retry_with_network_simulation(self):
        """Simulate network failures with retry."""
        attempts = [0]
        
        @exponential_backoff(max_retries=3, base_delay=0.1)
        def simulated_network_call():
            attempts[0] += 1
            if attempts[0] == 1:
                raise ConnectionError("Network timeout")
            elif attempts[0] == 2:
                raise RuntimeError("Server error 503")
            else:
                return {"status": "success", "data": "result"}
        
        result = simulated_network_call()
        assert result["status"] == "success"
        assert attempts[0] == 3
    
    def test_retry_with_validation_error(self):
        """Validation errors should not be retried."""
        attempts = [0]
        
        @exponential_backoff(max_retries=3, base_delay=0.1)
        def api_call_with_validation():
            attempts[0] += 1
            raise ValueError("Invalid schema type")
        
        with pytest.raises(ValueError):
            api_call_with_validation()
        
        assert attempts[0] == 1  # No retries for validation errors

