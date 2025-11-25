"""
Detector error handler for StressSpec.

This module provides functionality for handling errors during detector execution.
It follows the Single Responsibility Principle by focusing only on error handling.

BEGINNER NOTES:
- This class handles errors that occur when detectors run
- It logs errors and can optionally return error risks
- It makes error handling consistent across the application
- It can be easily tested and mocked
"""

import logging
from typing import List
from src.models.requirement import Requirement
from src.models.risk import Risk
from src.detectors.base import RiskDetector

logger = logging.getLogger(__name__)


class DetectorErrorHandler:
    """
    Handles errors during detector execution.
    
    BEGINNER NOTES:
    - This class is like a "safety net" that catches errors from detectors
    - It logs errors so developers know what went wrong
    - It can optionally return error risks to notify users about detector failures
    - It makes error handling consistent and testable
    
    This class provides:
    - Error logging with context
    - Optional error risk generation
    - Configurable error handling behavior
    """
    
    def __init__(self, log_errors: bool = True, return_error_risks: bool = False):
        """
        Initialize the error handler.
        
        Args:
            log_errors: If True, log errors to the logger
            return_error_risks: If True, return error risks when detectors fail
        """
        self.log_errors = log_errors
        self.return_error_risks = return_error_risks
    
    def handle_detector_error(self, 
                              detector: RiskDetector,
                              requirement: Requirement,
                              error: Exception) -> List[Risk]:
        """
        Handle detector errors with logging and optional error risks.
        
        Args:
            detector: The detector that failed
            requirement: The requirement being analyzed when the error occurred
            error: The exception that was raised
            
        Returns:
            List of risks (empty list by default, or error risks if enabled)
        """
        if self.log_errors:
            logger.warning(
                f"Detector {detector.get_detector_name()} failed "
                f"for requirement {requirement.id}: {error}",
                exc_info=True
            )
        
        if self.return_error_risks:
            # Optionally return an error risk to notify users
            # This would require creating a special error risk
            # For now, we'll just return empty list
            # Future enhancement: create error risk with special category
            pass
        
        return []

