"""
Logging Configuration for StressSpec Web UI

This module provides comprehensive logging configuration for the StressSpec web application.
It includes structured logging, error tracking, and monitoring capabilities.

BEGINNER NOTES:
- This module sets up logging for the entire application
- It provides different log levels for different types of information
- It helps with debugging and monitoring application behavior
- It creates log files for different purposes (errors, access, performance)
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
import traceback

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured logging.
    
    BEGINNER NOTES:
    - This creates structured log entries that are easy to parse
    - It includes additional context like request IDs and user info
    - It makes logs more useful for monitoring and debugging
    """
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, default=str)

class RequestContextFilter(logging.Filter):
    """
    Filter to add request context to log records.
    
    BEGINNER NOTES:
    - This adds information about the current request to log entries
    - It helps track requests across different parts of the application
    - It makes debugging easier by providing context
    """
    
    def filter(self, record):
        # Add request context if available
        if hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', 'unknown')
        
        if hasattr(record, 'user_id'):
            record.user_id = getattr(record, 'user_id', 'anonymous')
        
        if hasattr(record, 'ip_address'):
            record.ip_address = getattr(record, 'ip_address', 'unknown')
        
        return True

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Set up comprehensive logging for the application.
    
    BEGINNER NOTES:
    - This function configures all the logging for the application
    - It creates different log files for different purposes
    - It sets up both file and console logging
    - It provides structured logging for better monitoring
    """
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    structured_formatter = StructuredFormatter()
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    console_handler.addFilter(RequestContextFilter())
    root_logger.addHandler(console_handler)
    
    # Application log file (all logs)
    app_log_file = log_path / "application.log"
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(structured_formatter)
    app_handler.addFilter(RequestContextFilter())
    root_logger.addHandler(app_handler)
    
    # Error log file (errors only)
    error_log_file = log_path / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(structured_formatter)
    error_handler.addFilter(RequestContextFilter())
    root_logger.addHandler(error_handler)
    
    # Access log file (requests)
    access_log_file = log_path / "access.log"
    access_handler = logging.handlers.RotatingFileHandler(
        access_log_file,
        maxBytes=20*1024*1024,  # 20MB
        backupCount=3,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(structured_formatter)
    access_handler.addFilter(RequestContextFilter())
    
    # Create access logger
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False
    
    # Performance log file (timing and metrics)
    perf_log_file = log_path / "performance.log"
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(structured_formatter)
    perf_handler.addFilter(RequestContextFilter())
    
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.setLevel(logging.INFO)
    perf_logger.addHandler(perf_handler)
    perf_logger.propagate = False
    
    # Security log file (security events)
    security_log_file = log_path / "security.log"
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(structured_formatter)
    security_handler.addFilter(RequestContextFilter())
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    security_logger.addHandler(security_handler)
    security_logger.propagate = False
    
    # Configure specific loggers
    configure_third_party_loggers()
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized", extra={
        'extra_fields': {
            'log_level': log_level,
            'log_directory': str(log_path),
            'handlers': [h.__class__.__name__ for h in root_logger.handlers]
        }
    })

def configure_third_party_loggers():
    """
    Configure logging for third-party libraries.
    
    BEGINNER NOTES:
    - This reduces noise from third-party libraries
    - It sets appropriate log levels for external dependencies
    - It helps focus on application-specific logs
    """
    
    # Reduce noise from third-party libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    logging.getLogger('starlette').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Keep our application loggers at INFO level
    logging.getLogger('web').setLevel(logging.INFO)
    logging.getLogger('src').setLevel(logging.INFO)

def log_request(request_id: str, method: str, path: str, status_code: int, 
                duration: float, user_agent: str = None, ip_address: str = None):
    """
    Log HTTP request details.
    
    BEGINNER NOTES:
    - This logs information about each HTTP request
    - It helps with monitoring and debugging
    - It provides metrics for performance analysis
    """
    
    access_logger = logging.getLogger('access')
    access_logger.info(
        f"{method} {path} {status_code}",
        extra={
            'extra_fields': {
                'request_id': request_id,
                'method': method,
                'path': path,
                'status_code': status_code,
                'duration_ms': duration * 1000,
                'user_agent': user_agent,
                'ip_address': ip_address
            }
        }
    )

def log_performance(operation: str, duration: float, **kwargs):
    """
    Log performance metrics.
    
    BEGINNER NOTES:
    - This logs performance information for operations
    - It helps identify slow operations
    - It provides data for performance optimization
    """
    
    perf_logger = logging.getLogger('performance')
    perf_logger.info(
        f"Performance: {operation}",
        extra={
            'extra_fields': {
                'operation': operation,
                'duration_ms': duration * 1000,
                **kwargs
            }
        }
    )

def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "INFO"):
    """
    Log security-related events.
    
    BEGINNER NOTES:
    - This logs security events for monitoring
    - It helps detect potential security issues
    - It provides audit trail for security analysis
    """
    
    security_logger = logging.getLogger('security')
    
    if severity.upper() == "CRITICAL":
        security_logger.critical(f"Security: {event_type}", extra={'extra_fields': details})
    elif severity.upper() == "WARNING":
        security_logger.warning(f"Security: {event_type}", extra={'extra_fields': details})
    else:
        security_logger.info(f"Security: {event_type}", extra={'extra_fields': details})

def log_error_with_context(error: Exception, context: Dict[str, Any] = None, 
                          request_id: str = None):
    """
    Log errors with additional context.
    
    BEGINNER NOTES:
    - This logs errors with extra context information
    - It helps with debugging by providing more details
    - It makes error tracking more effective
    """
    
    logger = logging.getLogger(__name__)
    context = context or {}
    
    if request_id:
        context['request_id'] = request_id
    
    logger.error(
        f"Error: {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra={'extra_fields': context}
    )

class LoggingMiddleware:
    """
    Middleware for request logging.
    
    BEGINNER NOTES:
    - This middleware logs all HTTP requests
    - It adds request context to logs
    - It measures request duration
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_id = scope.get("request_id", "unknown")
        method = scope["method"]
        path = scope["path"]
        start_time = datetime.utcnow()
        
        # Add request context to logging
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        # Process request
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Log request
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Get client info if available
            client = scope.get("client")
            ip_address = client[0] if client else "unknown"
            
            # Get user agent from headers
            headers = dict(scope.get("headers", []))
            user_agent = headers.get(b"user-agent", b"").decode("utf-8", errors="ignore")
            
            log_request(request_id, method, path, status_code, duration, user_agent, ip_address)
            
            # Restore old factory
            logging.setLogRecordFactory(old_factory)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    BEGINNER NOTES:
    - This creates loggers for different parts of the application
    - It ensures consistent logging configuration
    - It makes logging easy to use throughout the application
    """
    
    return logging.getLogger(name)

# Performance monitoring decorator
def monitor_performance(operation_name: str):
    """
    Decorator to monitor function performance.
    
    BEGINNER NOTES:
    - This decorator automatically logs performance metrics
    - It measures how long functions take to execute
    - It helps identify performance bottlenecks
    """
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                log_performance(operation_name, duration, success=True)
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                log_performance(operation_name, duration, success=False, error=str(e))
                raise
        return wrapper
    return decorator

# Error tracking decorator
def track_errors(func):
    """
    Decorator to automatically track errors.
    
    BEGINNER NOTES:
    - This decorator automatically logs errors from functions
    - It provides context about where errors occurred
    - It helps with debugging and error monitoring
    """
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error_with_context(e, {
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            })
            raise
    return wrapper
