"""
Error Recovery and Retry Logic for StressSpec Web UI

This module provides comprehensive error recovery mechanisms and retry logic
for the StressSpec web application.

BEGINNER NOTES:
- This module handles automatic retry of failed operations
- It provides circuit breaker patterns for preventing cascading failures
- It implements exponential backoff for retry delays
- It helps make the application more resilient to temporary failures
"""

import asyncio
import time
import random
from typing import Callable, Any, Optional, Dict, List, Union
from functools import wraps
from enum import Enum
import logging

from .exceptions import StressSpecException, TimeoutError
from .logging_config import get_logger, log_performance, log_error_with_context

logger = get_logger(__name__)

class RetryStrategy(Enum):
    """Different retry strategies."""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CUSTOM = "custom"

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
                 jitter: bool = True,
                 backoff_multiplier: float = 2.0,
                 retry_on_exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.jitter = jitter
        self.backoff_multiplier = backoff_multiplier
        self.retry_on_exceptions = retry_on_exceptions

class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 30.0,
                 expected_exception: tuple = (Exception,),
                 success_threshold: int = 2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

class CircuitBreaker:
    """
    Circuit breaker implementation.
    
    BEGINNER NOTES:
    - This prevents cascading failures by temporarily stopping requests to failing services
    - It has three states: closed (normal), open (failing fast), half-open (testing)
    - It helps protect the application from overwhelming failing services
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.name = "default"
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker."""
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        
        return wrapper
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
            else:
                raise StressSpecException(
                    message=f"Circuit breaker {self.name} is OPEN",
                    error_code="CIRCUIT_BREAKER_OPEN",
                    details={"state": self.state.value, "last_failure": self.last_failure_time}
                )
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} reset to CLOSED")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} opened again after HALF_OPEN")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker {self.name} opened after {self.failure_count} failures")

class RetryManager:
    """
    Manages retry logic with different strategies.
    
    BEGINNER NOTES:
    - This handles automatic retry of failed operations
    - It supports different retry strategies (exponential backoff, fixed delay, etc.)
    - It helps make operations more resilient to temporary failures
    """
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for retry logic."""
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.retry(func, *args, **kwargs)
        
        return wrapper
    
    async def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                if attempt > 0:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{self.config.max_attempts})")
                    await asyncio.sleep(delay)
                
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                
                return result
                
            except self.config.retry_on_exceptions as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                
                if attempt == self.config.max_attempts - 1:
                    logger.error(f"All {self.config.max_attempts} attempts failed for {func.__name__}")
                    break
        
        # All retries failed
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * (attempt + 1)
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        else:
            delay = self.config.base_delay
        
        # Apply max delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)

class TimeoutManager:
    """
    Manages operation timeouts.
    
    BEGINNER NOTES:
    - This prevents operations from running indefinitely
    - It helps prevent resource exhaustion
    - It provides better user experience with predictable response times
    """
    
    @staticmethod
    def timeout(seconds: float):
        """Decorator to add timeout to operations."""
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else asyncio.to_thread(func, *args, **kwargs),
                        timeout=seconds
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(
                        message=f"Operation {func.__name__} timed out after {seconds} seconds",
                        timeout_seconds=seconds,
                        details={"function": func.__name__}
                    )
            
            return wrapper
        return decorator

class HealthChecker:
    """
    Health checking for services and dependencies.
    
    BEGINNER NOTES:
    - This monitors the health of external services and dependencies
    - It helps detect when services become unavailable
    - It provides data for circuit breakers and retry logic
    """
    
    def __init__(self):
        self.health_status: Dict[str, Dict] = {}
        self.check_interval = 30.0  # seconds
        self._running = False
    
    async def start(self):
        """Start health checking."""
        if self._running:
            return
        
        self._running = True
        logger.info("Starting health checker")
        
        # Start background health checking
        asyncio.create_task(self._health_check_loop())
    
    async def stop(self):
        """Stop health checking."""
        self._running = False
        logger.info("Health checker stopped")
    
    async def register_service(self, name: str, check_func: Callable, interval: float = None):
        """Register a service for health checking."""
        self.health_status[name] = {
            'check_func': check_func,
            'interval': interval or self.check_interval,
            'last_check': 0,
            'healthy': True,
            'last_error': None
        }
        logger.info(f"Registered health check for service: {name}")
    
    async def check_service(self, name: str) -> bool:
        """Check health of a specific service."""
        if name not in self.health_status:
            return False
        
        service_info = self.health_status[name]
        
        try:
            result = await service_info['check_func']() if asyncio.iscoroutinefunction(service_info['check_func']) else service_info['check_func']()
            service_info['healthy'] = bool(result)
            service_info['last_error'] = None
        except Exception as e:
            service_info['healthy'] = False
            service_info['last_error'] = str(e)
            logger.warning(f"Health check failed for {name}: {str(e)}")
        
        service_info['last_check'] = time.time()
        return service_info['healthy']
    
    async def _health_check_loop(self):
        """Background health checking loop."""
        while self._running:
            for name in list(self.health_status.keys()):
                service_info = self.health_status[name]
                current_time = time.time()
                
                # Check if it's time for next check
                if current_time - service_info['last_check'] >= service_info['interval']:
                    await self.check_service(name)
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    def get_status(self) -> Dict[str, Dict]:
        """Get current health status of all services."""
        return self.health_status.copy()
    
    def is_healthy(self, name: str) -> bool:
        """Check if a service is currently healthy."""
        if name not in self.health_status:
            return False
        
        return self.health_status[name]['healthy']

# Global instances
_health_checker = HealthChecker()

# Convenience decorators
def retry(config: RetryConfig = None):
    """Decorator for retry logic."""
    if config is None:
        config = RetryConfig()
    
    retry_manager = RetryManager(config)
    return retry_manager

def circuit_breaker(config: CircuitBreakerConfig = None, name: str = "default"):
    """Decorator for circuit breaker."""
    if config is None:
        config = CircuitBreakerConfig()
    
    cb = CircuitBreaker(config)
    cb.name = name
    return cb

def timeout(seconds: float):
    """Decorator for operation timeout."""
    return TimeoutManager.timeout(seconds)

# Health checking functions
async def start_health_monitoring():
    """Start global health monitoring."""
    await _health_checker.start()

async def stop_health_monitoring():
    """Stop global health monitoring."""
    await _health_checker.stop()

def register_health_check(name: str, check_func: Callable, interval: float = None):
    """Register a health check."""
    return _health_checker.register_service(name, check_func, interval)

def is_service_healthy(name: str) -> bool:
    """Check if a service is healthy."""
    return _health_checker.is_healthy(name)

def get_health_status() -> Dict[str, Dict]:
    """Get health status of all services."""
    return _health_checker.get_status()

# Example health check functions
async def check_file_system():
    """Check if file system is accessible."""
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(b"test")
        return True
    except Exception:
        return False

async def check_memory():
    """Check available memory."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return memory.percent < 90  # Consider unhealthy if >90% memory used
    except ImportError:
        return True  # Skip check if psutil not available
    except Exception:
        return False

async def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_percent = (free / total) * 100
        return free_percent > 10  # Consider unhealthy if <10% free space
    except Exception:
        return False
