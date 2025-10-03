"""
Error Handling Middleware for StressSpec Web UI

This module provides middleware for comprehensive error handling,
logging, and monitoring in the StressSpec web application.

BEGINNER NOTES:
- This middleware runs before and after requests
- It catches errors and provides consistent error handling
- It logs errors for debugging and monitoring
- It provides security by not exposing sensitive information
"""

import time
import traceback
import uuid
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from .exceptions import (
    StressSpecException, create_error_response, handle_validation_error,
    handle_http_exception, handle_generic_exception, log_error, ErrorSeverity
)

# Configure logging
logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive error handling and logging.
    
    BEGINNER NOTES:
    - This middleware catches all errors in the application
    - It provides consistent error responses
    - It logs errors for debugging and monitoring
    - It adds request context to error logs
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process requests and handle errors.
        
        BEGINNER NOTES:
        - This function runs for every request
        - It measures request time and logs errors
        - It provides consistent error handling
        - It adds request tracking for debugging
        """
        # Generate unique request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Increment request counter
        self.request_count += 1
        
        # Log request start
        start_time = time.time()
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Log successful response
            process_time = time.time() - start_time
            logger.info(f"Request {request_id}: {response.status_code} ({process_time:.3f}s)")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except StressSpecException as e:
            # Handle custom StressSpec exceptions
            self.error_count += 1
            log_error(e, ErrorSeverity.MEDIUM, {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_code": e.error_code
            })
            
            return create_error_response(e, request)
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            self.error_count += 1
            log_error(e, ErrorSeverity.LOW, {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": e.status_code
            })
            
            return handle_http_exception(e)
            
        except Exception as e:
            # Handle all other exceptions
            self.error_count += 1
            log_error(e, ErrorSeverity.HIGH, {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "exception_type": type(e).__name__
            })
            
            return handle_generic_exception(e)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request logging and monitoring.
    
    BEGINNER NOTES:
    - This middleware logs detailed information about requests
    - It helps with debugging and performance monitoring
    - It can be used to track API usage patterns
    - It provides insights into application behavior
    """
    
    def __init__(self, app: ASGIApp, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0,
            "response_times": []
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log detailed request information."""
        start_time = time.time()
        
        # Log request details
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
        
        # Log request body if enabled (be careful with large bodies)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body and len(body) < 1000:  # Only log small bodies
                    request_info["body"] = body.decode("utf-8")
            except Exception:
                request_info["body"] = "[Unable to read body]"
        
        logger.debug(f"Request details: {request_info}")
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update statistics
            self.stats["total_requests"] += 1
            if response.status_code < 400:
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            # Update average response time
            self.stats["response_times"].append(response_time)
            if len(self.stats["response_times"]) > 100:  # Keep only last 100
                self.stats["response_times"] = self.stats["response_times"][-100:]
            
            self.stats["average_response_time"] = sum(self.stats["response_times"]) / len(self.stats["response_times"])
            
            # Log response details
            logger.info(f"Response: {response.status_code} ({response_time:.3f}s)")
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Request failed: {type(e).__name__}: {str(e)} ({response_time:.3f}s)")
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    
    BEGINNER NOTES:
    - This middleware prevents abuse by limiting request rates
    - It tracks requests per IP address
    - It returns 429 status when limits are exceeded
    - It helps protect the application from overload
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits for each request."""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.request_counts[client_ip] = []
        
        # Check if limit exceeded
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                        "details": {
                            "limit": self.requests_per_minute,
                            "retry_after": 60
                        }
                    }
                },
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    
    BEGINNER NOTES:
    - This middleware adds security headers to all responses
    - It helps protect against common web vulnerabilities
    - It's a security best practice for web applications
    - It provides defense in depth
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to all responses."""
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response

class HealthCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware for health check endpoints.
    
    BEGINNER NOTES:
    - This middleware provides health check functionality
    - It can be used by load balancers and monitoring systems
    - It returns system status and statistics
    - It helps with application monitoring
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle health check requests."""
        if request.url.path == "/health":
            uptime = time.time() - self.start_time
            health_data = {
                "status": "healthy",
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": self.error_count / max(self.request_count, 1),
                "timestamp": time.time()
            }
            
            return JSONResponse(content=health_data)
        
        # Track requests for health check
        self.request_count += 1
        
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                self.error_count += 1
            return response
        except Exception:
            self.error_count += 1
            raise
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

def setup_error_handling_middleware(app: ASGIApp) -> None:
    """
    Set up all error handling middleware for the application.
    
    BEGINNER NOTES:
    - This function configures all the middleware
    - It sets up error handling, logging, rate limiting, and security
    - It should be called when setting up the FastAPI application
    - It provides comprehensive error handling for the entire application
    """
    # Add middleware in reverse order (last added is first executed)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(HealthCheckMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    app.add_middleware(RequestLoggingMiddleware, log_body=False)
    app.add_middleware(ErrorHandlingMiddleware)
    
    logger.info("Error handling middleware configured successfully")
