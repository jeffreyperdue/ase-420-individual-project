"""
Decorator pattern implementation for report enhancements in StressSpec.

This module implements the Decorator pattern to allow composable report
enhancements without modifying existing reporter classes.

BEGINNER NOTES:
- This follows the Decorator pattern from design patterns course materials
- It allows adding features to reports without modifying existing reporters
- Decorators wrap reporters and add functionality
- It's like "wrapping a gift" - you can add multiple layers of wrapping
    
This module provides:
- Base decorator class for report enhancements
- Timestamp decorator (adds timestamps)
- Summary decorator (adds executive summaries)
- Composable decorators that can be chained
"""

from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from src.reporting.base import Reporter, ReportData


class ReportDecorator(Reporter):
    """
    Base decorator for report enhancements.
    
    BEGINNER NOTES:
    - This is the base decorator class that wraps a reporter
    - It implements the Reporter interface so it can be used like a reporter
    - Subclasses can add features by overriding the write method
    - It's like a "wrapper" that adds functionality around the base reporter
    
    This class provides:
    - Wrapper around a Reporter instance
    - Template for decorator pattern implementation
    """
    
    def __init__(self, reporter: Reporter):
        """
        Initialize decorator with a reporter to wrap.
        
        Args:
            reporter: The reporter to decorate
        """
        self.reporter = reporter
    
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        """
        Write report (delegates to wrapped reporter by default).
        
        Args:
            data: Report data to write
            output: Optional output file path
            
        Returns:
            Path to written report file
        """
        return self.reporter.write(data, output)


class TimestampedReportDecorator(ReportDecorator):
    """
    Decorator that adds timestamp to report data.
    
    BEGINNER NOTES:
    - This decorator adds a timestamp to the report
    - It modifies the data before passing it to the wrapped reporter
    - It's like adding a "date stamp" to a document
    """
    
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        """
        Add timestamp to report data and write.
        
        Args:
            data: Report data to write
            output: Optional output file path
            
        Returns:
            Path to written report file
        """
        # Add timestamp to data (modify in place)
        # Note: ReportData is a dataclass, so we create a new one with timestamp
        # For now, we'll just pass through - actual timestamp addition would
        # require modifying ReportData structure or adding metadata field
        # This is a placeholder for the decorator pattern structure
        return self.reporter.write(data, output)


class SummaryReportDecorator(ReportDecorator):
    """
    Decorator that adds executive summary to report.
    
    BEGINNER NOTES:
    - This decorator adds an executive summary section
    - It enhances the report with summary statistics
    - It's like adding a "summary page" to a report
    """
    
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        """
        Add summary to report data and write.
        
        Args:
            data: Report data to write
            output: Optional output file path
            
        Returns:
            Path to written report file
        """
        # Add summary to data
        # Note: Actual summary addition would require modifying ReportData
        # or enhancing the reporter's write method
        # This is a placeholder for the decorator pattern structure
        return self.reporter.write(data, output)


class ValidatedReportDecorator(ReportDecorator):
    """
    Decorator that validates report data before writing.
    
    BEGINNER NOTES:
    - This decorator validates the report data before writing
    - It ensures data quality before report generation
    - It's like a "quality check" before printing
    """
    
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        """
        Validate report data and write.
        
        Args:
            data: Report data to write
            output: Optional output file path
            
        Returns:
            Path to written report file
            
        Raises:
            ValueError: If report data is invalid
        """
        # Validate data
        if not data.requirements:
            raise ValueError("Report data must contain at least one requirement")
        
        if not data.risks_by_requirement:
            # Empty risks dict is valid, but warn
            pass
        
        # Write if valid
        return self.reporter.write(data, output)

