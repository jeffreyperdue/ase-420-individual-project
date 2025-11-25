"""
Core exception classes for StressSpec.

This module defines custom exception classes for the core StressSpec library.
These are separate from web API exceptions and are used throughout the CLI
and core analysis components.

BEGINNER NOTES:
- This defines custom error types for the core library
- It helps provide consistent error messages and handling
- It makes debugging easier by having specific error types
- It provides better error context for users
"""

from typing import Optional, Dict, Any


class StressSpecCoreException(Exception):
    """
    Base exception class for StressSpec core library.
    
    BEGINNER NOTES:
    - This is the base class for all core exceptions
    - It provides a consistent structure for error messages
    - It can include additional context information
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            details: Optional additional context information
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class FileLoadError(StressSpecCoreException, FileNotFoundError, ValueError):
    """
    Exception raised when file loading fails.
    
    BEGINNER NOTES:
    - This is raised when a file cannot be loaded
    - It includes the file path in the error message
    - It helps identify which file caused the problem
    - Inherits from FileNotFoundError and ValueError for backward compatibility
    """
    
    def __init__(self, file_path: str, reason: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize file load error.
        
        Args:
            file_path: Path to the file that failed to load
            reason: Reason for the failure
            details: Optional additional context
        """
        message = f"Failed to load file '{file_path}': {reason}"
        details = details or {}
        details['file_path'] = file_path
        details['reason'] = reason
        # Initialize both parent classes
        StressSpecCoreException.__init__(self, message, details)
        # Determine which standard exception to use based on reason
        if "not found" in reason.lower():
            FileNotFoundError.__init__(self, message)
        else:
            ValueError.__init__(self, message)


class RequirementParseError(StressSpecCoreException):
    """
    Exception raised when requirement parsing fails.
    
    BEGINNER NOTES:
    - This is raised when requirements cannot be parsed from text
    - It includes line number information when available
    - It helps identify which part of the file caused the problem
    """
    
    def __init__(self, message: str, line_number: Optional[int] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize requirement parse error.
        
        Args:
            message: Error message
            line_number: Optional line number where error occurred
            details: Optional additional context
        """
        if line_number:
            message = f"{message} (line {line_number})"
        details = details or {}
        if line_number:
            details['line_number'] = line_number
        super().__init__(message, details)


class DetectorError(StressSpecCoreException):
    """
    Exception raised when a detector fails.
    
    BEGINNER NOTES:
    - This is raised when a risk detector encounters an error
    - It includes detector name and requirement ID
    - It helps identify which detector and requirement caused the problem
    """
    
    def __init__(self, detector_name: str, requirement_id: str, 
                 message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize detector error.
        
        Args:
            detector_name: Name of the detector that failed
            requirement_id: ID of the requirement being analyzed
            message: Error message
            details: Optional additional context
        """
        error_message = f"Detector '{detector_name}' failed for requirement '{requirement_id}': {message}"
        details = details or {}
        details['detector_name'] = detector_name
        details['requirement_id'] = requirement_id
        super().__init__(error_message, details)


class ConfigurationError(StressSpecCoreException):
    """
    Exception raised when configuration operations fail.
    
    BEGINNER NOTES:
    - This is raised when configuration cannot be loaded or is invalid
    - It includes the configuration file path
    - It helps identify configuration problems
    """
    
    def __init__(self, message: str, config_file: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_file: Optional path to configuration file
            details: Optional additional context
        """
        if config_file:
            message = f"{message} (config file: {config_file})"
        details = details or {}
        if config_file:
            details['config_file'] = config_file
        super().__init__(message, details)


class ReportGenerationError(StressSpecCoreException):
    """
    Exception raised when report generation fails.
    
    BEGINNER NOTES:
    - This is raised when a report cannot be generated
    - It includes the report format and output path
    - It helps identify report generation problems
    """
    
    def __init__(self, message: str, report_format: Optional[str] = None,
                 output_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize report generation error.
        
        Args:
            message: Error message
            report_format: Optional report format
            output_path: Optional output file path
            details: Optional additional context
        """
        details = details or {}
        if report_format:
            details['report_format'] = report_format
        if output_path:
            details['output_path'] = output_path
        super().__init__(message, details)

