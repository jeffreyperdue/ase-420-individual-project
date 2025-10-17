"""
Custom Exception Classes for StressSpec Web UI

This module defines custom exception classes and error handling utilities
for the StressSpec web application.

BEGINNER NOTES:
- This defines custom error types for our web application
- It helps provide consistent error messages and handling
- It makes debugging easier by having specific error types
- It provides better user experience with meaningful error messages
"""

import traceback
from typing import Any, Dict, Optional, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging

# Configure logging
logger = logging.getLogger(__name__)

class StressSpecException(Exception):
    """Base exception class for StressSpec application."""
    
    def __init__(self, message: str, error_code: str = "STRESSSPEC_ERROR", 
                 details: Optional[Dict[str, Any]] = None, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class FileValidationError(StressSpecException):
    """Exception raised when file validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FILE_VALIDATION_ERROR",
            details=details,
            status_code=400
        )

class AnalysisError(StressSpecException):
    """Exception raised when analysis fails."""
    
    def __init__(self, message: str, analysis_id: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if analysis_id:
            details["analysis_id"] = analysis_id
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details=details,
            status_code=500
        )

class ConfigurationError(StressSpecException):
    """Exception raised when configuration operations fail."""
    
    def __init__(self, message: str, config_path: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if config_path:
            details["config_path"] = config_path
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            status_code=500
        )

class ReportGenerationError(StressSpecException):
    """Exception raised when report generation fails."""
    
    def __init__(self, message: str, report_id: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if report_id:
            details["report_id"] = report_id
        super().__init__(
            message=message,
            error_code="REPORT_GENERATION_ERROR",
            details=details,
            status_code=500
        )

class ResourceNotFoundError(StressSpecException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str, 
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["resource_type"] = resource_type
        details["resource_id"] = resource_id
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details=details,
            status_code=404
        )

class ValidationError(StressSpecException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, field_errors: Optional[List[Dict[str, Any]]] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field_errors:
            details["field_errors"] = field_errors
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=400
        )

class RateLimitError(StressSpecException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            status_code=429
        )

class TimeoutError(StressSpecException):
    """Exception raised when an operation times out."""
    
    def __init__(self, message: str = "Operation timed out", 
                 timeout_seconds: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details=details,
            status_code=408
        )

class DatabaseError(StressSpecException):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=500
        )

class ExternalServiceError(StressSpecException):
    """Exception raised when external service calls fail."""
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if service_name:
            details["service_name"] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            status_code=502
        )

def create_error_response(exception: StressSpecException, 
                         request: Optional[Request] = None) -> JSONResponse:
    """
    Create a standardized error response for StressSpec exceptions.
    
    BEGINNER NOTES:
    - This function creates a consistent error response format
    - It includes error code, message, details, and request information
    - It helps with debugging and user feedback
    - It ensures all errors follow the same format
    """
    error_response = {
        "success": False,
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "details": exception.details,
            "timestamp": str(datetime.now().isoformat())
        }
    }
    
    # Add request information if available
    if request:
        error_response["error"]["request"] = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
    
    # Add traceback in development mode
    if logger.level <= logging.DEBUG:
        error_response["error"]["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=exception.status_code,
        content=error_response
    )

def handle_validation_error(validation_error: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    BEGINNER NOTES:
    - This handles errors from Pydantic model validation
    - It formats the error messages in a user-friendly way
    - It helps users understand what went wrong with their input
    """
    field_errors = []
    
    # Try to get errors via the standard API first
    errors_list = []
    try:
        errors_list = validation_error.errors()  # type: ignore[attr-defined]
    except Exception:
        errors_list = []
    
    # Fallbacks for different Pydantic versions or construction styles used in tests
    if not errors_list:
        # Some ValidationError instances may carry the raw errors in args[0]
        if getattr(validation_error, "args", None):
            first_arg = validation_error.args[0]
            if isinstance(first_arg, list):
                errors_list = first_arg
        # As another fallback, check common internal attributes
        if not errors_list:
            for attr_name in ("_errors", "raw_errors", "error_list"):
                possible = getattr(validation_error, attr_name, None)
                if isinstance(possible, list) and possible:
                    errors_list = possible
                    break
    
    for error in errors_list:
        # Normalize structures between pydantic v1 and v2
        loc = error.get("loc") if isinstance(error, dict) else getattr(error, "loc", ())
        msg = error.get("msg") if isinstance(error, dict) else getattr(error, "msg", "Validation error")
        err_type = error.get("type") if isinstance(error, dict) else getattr(error, "type", "value_error")
        inp = error.get("input") if isinstance(error, dict) else getattr(error, "input", None)
        field_errors.append({
            "field": ".".join(str(part) for part in (loc or ())) if loc is not None else "",
            "message": msg,
            "type": err_type,
            "input": inp
        })
    
    error_response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": {
                "field_errors": field_errors,
                "total_errors": len(field_errors)
            },
            "timestamp": str(datetime.now().isoformat())
        }
    }
    
    return JSONResponse(
        status_code=400,
        content=error_response
    )

def handle_http_exception(exception: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    
    BEGINNER NOTES:
    - This handles standard HTTP exceptions from FastAPI
    - It provides consistent error formatting
    - It includes additional context when available
    """
    error_response = {
        "success": False,
        "error": {
            "code": f"HTTP_{exception.status_code}",
            "message": exception.detail,
            "details": {
                "status_code": exception.status_code
            },
            "timestamp": str(datetime.now().isoformat())
        }
    }
    
    return JSONResponse(
        status_code=exception.status_code,
        content=error_response
    )

def handle_generic_exception(exception: Exception) -> JSONResponse:
    """
    Handle generic exceptions that aren't caught by specific handlers.
    
    BEGINNER NOTES:
    - This is a catch-all for unexpected errors
    - It logs the error for debugging
    - It provides a generic error message to users
    - It prevents sensitive information from being exposed
    """
    # Log the full error for debugging
    logger.error(f"Unhandled exception: {type(exception).__name__}: {str(exception)}")
    logger.error(traceback.format_exc())
    
    error_response = {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "details": {
                "exception_type": type(exception).__name__
            },
            "timestamp": str(datetime.now().isoformat())
        }
    }
    
    # Add more details in development mode
    if logger.level <= logging.DEBUG:
        error_response["error"]["details"]["exception_message"] = str(exception)
        error_response["error"]["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

# Error severity levels for logging
class ErrorSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

def log_error(exception: Exception, severity: str = ErrorSeverity.MEDIUM, 
              context: Optional[Dict[str, Any]] = None):
    """
    Log errors with appropriate severity and context.
    
    BEGINNER NOTES:
    - This helps with debugging and monitoring
    - It categorizes errors by severity
    - It includes additional context when available
    - It helps identify patterns in errors
    """
    context = context or {}
    
    log_message = f"Error: {type(exception).__name__}: {str(exception)}"
    if context:
        log_message += f" | Context: {context}"
    
    if severity == ErrorSeverity.CRITICAL:
        logger.critical(log_message)
    elif severity == ErrorSeverity.HIGH:
        logger.error(log_message)
    elif severity == ErrorSeverity.MEDIUM:
        logger.warning(log_message)
    else:
        logger.info(log_message)

# Import datetime for timestamp generation
from datetime import datetime
