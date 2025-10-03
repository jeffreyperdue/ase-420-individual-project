"""
Comprehensive Error Handling Tests for StressSpec Web UI

This module tests all error handling functionality including:
- Custom exception classes
- Error handling middleware
- API error responses
- Client-side error handling
- Recovery mechanisms
- Logging and monitoring

BEGINNER NOTES:
- This module tests all the error handling features we've implemented
- It ensures that errors are handled gracefully and consistently
- It helps maintain quality and reliability of the error handling system
- It provides examples of how to test error scenarios
"""

import pytest
import asyncio
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

# Import our error handling modules
from web.api.exceptions import (
    StressSpecException, FileValidationError, AnalysisError,
    ConfigurationError, ReportGenerationError, ResourceNotFoundError,
    ValidationError, RateLimitError, TimeoutError, DatabaseError,
    ExternalServiceError, create_error_response, handle_validation_error,
    handle_http_exception, handle_generic_exception
)
from web.api.middleware import (
    ErrorHandlingMiddleware, RequestLoggingMiddleware, 
    RateLimitMiddleware, SecurityHeadersMiddleware
)
from web.api.recovery import (
    RetryManager, RetryConfig, RetryStrategy, CircuitBreaker,
    CircuitBreakerConfig, CircuitState, TimeoutManager, HealthChecker
)
from web.api.logging_config import setup_logging, get_logger
from web.main import app

class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_stressspec_exception_basic(self):
        """Test basic StressSpec exception creation."""
        exc = StressSpecException("Test error")
        assert exc.message == "Test error"
        assert exc.error_code == "STRESSSPEC_ERROR"
        assert exc.status_code == 500
        assert exc.details == {}
    
    def test_stressspec_exception_with_details(self):
        """Test StressSpec exception with custom details."""
        details = {"field": "value", "number": 42}
        exc = StressSpecException("Test error", "CUSTOM_ERROR", details, 400)
        assert exc.message == "Test error"
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.status_code == 400
        assert exc.details == details
    
    def test_file_validation_error(self):
        """Test file validation error."""
        exc = FileValidationError("Invalid file", {"size": "too_large"})
        assert exc.message == "Invalid file"
        assert exc.error_code == "FILE_VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.details == {"size": "too_large"}
    
    def test_analysis_error(self):
        """Test analysis error."""
        exc = AnalysisError("Analysis failed", "analysis_123", {"step": "parsing"})
        assert exc.message == "Analysis failed"
        assert exc.error_code == "ANALYSIS_ERROR"
        assert exc.status_code == 500
        assert exc.details == {"analysis_id": "analysis_123", "step": "parsing"}
    
    def test_resource_not_found_error(self):
        """Test resource not found error."""
        exc = ResourceNotFoundError("File", "file_123")
        assert "File with ID 'file_123' not found" in exc.message
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.status_code == 404
        assert exc.details["resource_type"] == "File"
        assert exc.details["resource_id"] == "file_123"
    
    def test_validation_error(self):
        """Test validation error."""
        field_errors = [{"field": "email", "message": "Invalid format"}]
        exc = ValidationError("Validation failed", field_errors)
        assert exc.message == "Validation failed"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.details["field_errors"] == field_errors
    
    def test_rate_limit_error(self):
        """Test rate limit error."""
        exc = RateLimitError("Too many requests", 60)
        assert exc.message == "Too many requests"
        assert exc.error_code == "RATE_LIMIT_ERROR"
        assert exc.status_code == 429
        assert exc.details["retry_after"] == 60
    
    def test_timeout_error(self):
        """Test timeout error."""
        exc = TimeoutError("Operation timed out", 30)
        assert exc.message == "Operation timed out"
        assert exc.error_code == "TIMEOUT_ERROR"
        assert exc.status_code == 408
        assert exc.details["timeout_seconds"] == 30

class TestErrorHandlers:
    """Test error handler functions."""
    
    def test_create_error_response(self):
        """Test error response creation."""
        exc = StressSpecException("Test error", "TEST_ERROR", {"key": "value"})
        request = Mock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"
        
        response = create_error_response(exc, request)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = json.loads(response.body.decode())
        assert content["success"] is False
        assert content["error"]["code"] == "TEST_ERROR"
        assert content["error"]["message"] == "Test error"
        assert content["error"]["details"]["key"] == "value"
        assert "request" in content["error"]
    
    def test_handle_validation_error(self):
        """Test validation error handler."""
        from pydantic import ValidationError as PydanticValidationError
        
        # Create a mock Pydantic validation error
        errors = [
            {"loc": ("field1",), "msg": "Invalid value", "type": "value_error"},
            {"loc": ("field2",), "msg": "Missing field", "type": "missing"}
        ]
        exc = PydanticValidationError(errors, Mock())
        
        response = handle_validation_error(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        
        content = json.loads(response.body.decode())
        assert content["success"] is False
        assert content["error"]["code"] == "VALIDATION_ERROR"
        assert len(content["error"]["details"]["field_errors"]) == 2
    
    def test_handle_http_exception(self):
        """Test HTTP exception handler."""
        exc = HTTPException(status_code=404, detail="Not found")
        
        response = handle_http_exception(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        
        content = json.loads(response.body.decode())
        assert content["success"] is False
        assert content["error"]["code"] == "HTTP_404"
        assert content["error"]["message"] == "Not found"
    
    def test_handle_generic_exception(self):
        """Test generic exception handler."""
        exc = Exception("Generic error")
        
        response = handle_generic_exception(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = json.loads(response.body.decode())
        assert content["success"] is False
        assert content["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "unexpected error occurred" in content["error"]["message"]

class TestRetryManager:
    """Test retry manager functionality."""
    
    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Test retry manager with immediate success."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        retry_manager = RetryManager(config)
        
        async def success_func():
            return "success"
        
        result = await retry_manager.retry(success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test retry manager with eventual success."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        retry_manager = RetryManager(config)
        
        attempts = 0
        
        async def flaky_func():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = await retry_manager.retry(flaky_func)
        assert result == "success"
        assert attempts == 3
    
    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test retry manager when max attempts exceeded."""
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        retry_manager = RetryManager(config)
        
        async def failing_func():
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError, match="Persistent failure"):
            await retry_manager.retry(failing_func)
    
    @pytest.mark.asyncio
    async def test_retry_delay_calculation(self):
        """Test retry delay calculation strategies."""
        # Test exponential backoff
        config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_multiplier=2.0,
            jitter=False
        )
        retry_manager = RetryManager(config)
        
        # Delay should be 1.0, 2.0, 4.0
        delays = []
        for attempt in range(3):
            delay = retry_manager._calculate_delay(attempt)
            delays.append(delay)
        
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        
        # Test fixed delay
        config.strategy = RetryStrategy.FIXED
        delays = []
        for attempt in range(3):
            delay = retry_manager._calculate_delay(attempt)
            delays.append(delay)
        
        assert all(delay == 1.0 for delay in delays)
        
        # Test linear delay
        config.strategy = RetryStrategy.LINEAR
        delays = []
        for attempt in range(3):
            delay = retry_manager._calculate_delay(attempt)
            delays.append(delay)
        
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 3.0

class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state (normal operation)."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        cb = CircuitBreaker(config)
        
        # Should work normally
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        cb = CircuitBreaker(config)
        
        async def failing_func():
            raise ValueError("Service unavailable")
        
        # First failure
        with pytest.raises(ValueError):
            await cb.call(failing_func)
        assert cb.state == CircuitState.CLOSED
        
        # Second failure should open circuit
        with pytest.raises(ValueError):
            await cb.call(failing_func)
        assert cb.state == CircuitState.OPEN
        
        # Third call should fail fast
        with pytest.raises(StressSpecException, match="Circuit breaker.*is OPEN"):
            await cb.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0.1,
            success_threshold=2
        )
        cb = CircuitBreaker(config)
        
        async def failing_func():
            raise ValueError("Service unavailable")
        
        # Open the circuit
        with pytest.raises(ValueError):
            await cb.call(failing_func)
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        async def success_func():
            return "success"
        
        # First success should move to half-open
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.HALF_OPEN
        
        # Second success should close circuit
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

class TestTimeoutManager:
    """Test timeout manager functionality."""
    
    @pytest.mark.asyncio
    async def test_timeout_decorator_success(self):
        """Test timeout decorator with successful operation."""
        @TimeoutManager.timeout(1.0)
        async def quick_operation():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await quick_operation()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_timeout_decorator_timeout(self):
        """Test timeout decorator with timeout."""
        @TimeoutManager.timeout(0.1)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "success"
        
        with pytest.raises(TimeoutError, match="timed out after 0.1 seconds"):
            await slow_operation()
    
    @pytest.mark.asyncio
    async def test_timeout_decorator_sync_function(self):
        """Test timeout decorator with synchronous function."""
        @TimeoutManager.timeout(1.0)
        def sync_operation():
            import time
            time.sleep(0.1)
            return "success"
        
        result = await sync_operation()
        assert result == "success"

class TestHealthChecker:
    """Test health checker functionality."""
    
    @pytest.mark.asyncio
    async def test_health_checker_registration(self):
        """Test health checker service registration."""
        health_checker = HealthChecker()
        
        async def check_func():
            return True
        
        await health_checker.register_service("test_service", check_func, 10.0)
        
        assert "test_service" in health_checker.health_status
        assert health_checker.health_status["test_service"]["check_func"] == check_func
        assert health_checker.health_status["test_service"]["interval"] == 10.0
    
    @pytest.mark.asyncio
    async def test_health_checker_service_check(self):
        """Test individual service health check."""
        health_checker = HealthChecker()
        
        async def healthy_check():
            return True
        
        async def unhealthy_check():
            return False
        
        await health_checker.register_service("healthy_service", healthy_check)
        await health_checker.register_service("unhealthy_service", unhealthy_check)
        
        # Check healthy service
        result = await health_checker.check_service("healthy_service")
        assert result is True
        assert health_checker.health_status["healthy_service"]["healthy"] is True
        
        # Check unhealthy service
        result = await health_checker.check_service("unhealthy_service")
        assert result is False
        assert health_checker.health_status["unhealthy_service"]["healthy"] is False
    
    @pytest.mark.asyncio
    async def test_health_checker_exception_handling(self):
        """Test health checker exception handling."""
        health_checker = HealthChecker()
        
        async def failing_check():
            raise Exception("Service check failed")
        
        await health_checker.register_service("failing_service", failing_check)
        
        result = await health_checker.check_service("failing_service")
        assert result is False
        assert health_checker.health_status["failing_service"]["healthy"] is False
        assert "Service check failed" in health_checker.health_status["failing_service"]["last_error"]

class TestMiddleware:
    """Test middleware functionality."""
    
    @pytest.mark.asyncio
    async def test_error_handling_middleware(self):
        """Test error handling middleware."""
        app = FastAPI()
        middleware = ErrorHandlingMiddleware(app)
        
        # Mock request and response
        request = Mock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"
        
        async def failing_call_next(request):
            raise ValueError("Test error")
        
        # Should catch the error and return error response
        response = await middleware.dispatch(request, failing_call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = json.loads(response.body.decode())
        assert content["success"] is False
        assert "unexpected error occurred" in content["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_rate_limit_middleware(self):
        """Test rate limit middleware."""
        app = FastAPI()
        middleware = RateLimitMiddleware(app, requests_per_minute=2)
        
        # Mock request
        request = Mock()
        request.client.host = "127.0.0.1"
        
        async def success_call_next(request):
            return JSONResponse(content={"success": True})
        
        # First two requests should succeed
        response1 = await middleware.dispatch(request, success_call_next)
        assert response1.status_code == 200
        
        response2 = await middleware.dispatch(request, success_call_next)
        assert response2.status_code == 200
        
        # Third request should be rate limited
        response3 = await middleware.dispatch(request, success_call_next)
        assert response3.status_code == 429
        
        content = json.loads(response3.body.decode())
        assert "Rate limit exceeded" in content["error"]["message"]

class TestIntegration:
    """Test integration of error handling components."""
    
    def test_fastapi_app_error_handling(self):
        """Test FastAPI app error handling integration."""
        client = TestClient(app)
        
        # Test 404 error
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_api_error_responses(self):
        """Test API error responses."""
        client = TestClient(app)
        
        # Test invalid file upload
        response = client.post("/api/upload/", files={"file": ("test.txt", b"content")})
        # This should work, but we can test with invalid file types
        response = client.post("/api/upload/", files={"file": ("test.exe", b"content")})
        assert response.status_code == 400
        
        # Test invalid analysis ID
        response = client.get("/api/analysis/status/invalid_id")
        assert response.status_code == 400
    
    def test_debug_endpoints(self):
        """Test debug endpoints."""
        client = TestClient(app)
        
        # Test debug info endpoint
        response = client.get("/api/debug/info")
        assert response.status_code == 200
        data = response.json()
        assert "system_info" in data
        assert "application_info" in data
        
        # Test health check endpoint
        response = client.get("/api/debug/health-check")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        
        # Test performance metrics endpoint
        response = client.get("/api/debug/performance")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "application" in data

class TestLogging:
    """Test logging functionality."""
    
    def test_logging_setup(self):
        """Test logging setup."""
        # This test verifies that logging can be set up without errors
        try:
            setup_logging(log_level="DEBUG", log_dir="test_logs")
            logger = get_logger("test_logger")
            logger.info("Test log message")
            
            # Clean up
            import shutil
            if os.path.exists("test_logs"):
                shutil.rmtree("test_logs")
                
        except Exception as e:
            pytest.fail(f"Logging setup failed: {e}")
    
    def test_structured_logging(self):
        """Test structured logging functionality."""
        # This test would require more complex setup to capture log output
        # For now, we just verify the logger can be created
        logger = get_logger("test_structured_logger")
        assert logger is not None
        assert logger.name == "test_structured_logger"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
