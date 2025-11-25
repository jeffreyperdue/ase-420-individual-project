"""
Reporter factory module for StressSpec.

This module implements the Factory Method pattern for creating reporters
based on report format. This follows the Open/Closed Principle by allowing
new report formats to be added without modifying existing code.

BEGINNER NOTES:
- This factory creates different types of reporters (Markdown, CSV, JSON, HTML)
- It uses the Factory Method pattern - you ask for a reporter by format, it creates the right one
- It's like a restaurant where you order "pizza" and the kitchen makes the right type of pizza
- All reporters are created through this factory, making it easy to add new ones
"""

from typing import Dict, Type
from src.reporting import ReportFormat, Reporter, MarkdownReporter, CsvReporter, JsonReporter, HtmlReporter


class ReporterFactory:
    """
    Factory for creating reporters based on format.
    
    BEGINNER NOTES:
    - This factory is like a "reporter store" that knows how to make different reporters
    - You ask for a reporter by format (like "md", "csv"), and it creates the right one
    - It uses the Factory Method pattern - the factory method creates the right object
    - It makes it easy to add new reporters without changing existing code
    
    This factory can create:
    - MarkdownReporter: Creates .md files
    - CsvReporter: Creates .csv files
    - JsonReporter: Creates .json files
    - HtmlReporter: Creates .html files
    """
    
    # Registry of available reporters
    _reporters: Dict[ReportFormat, Type[Reporter]] = {
        ReportFormat.MD: MarkdownReporter,
        ReportFormat.CSV: CsvReporter,
        ReportFormat.JSON: JsonReporter,
        ReportFormat.HTML: HtmlReporter,
    }
    
    def create_reporter(self, format: ReportFormat) -> Reporter:
        """
        Create a reporter for the specified format.
        
        BEGINNER NOTES:
        - This is the main "factory method" that creates reporters
        - It's like ordering food - you say what you want, it makes it for you
        - If you ask for an unknown format, it tells you what's available
        
        Args:
            format: Report format (e.g., ReportFormat.MD, ReportFormat.CSV)
            
        Returns:
            Reporter instance of the requested format
            
        Raises:
            ValueError: If format is not supported
        """
        reporter_class = self._reporters.get(format)
        if not reporter_class:
            available_formats = ', '.join([f.value for f in self._reporters.keys()])
            raise ValueError(
                f"Unsupported report format: {format}. "
                f"Available formats: {available_formats}"
            )
        return reporter_class()
    
    def register_reporter(self, format: ReportFormat, reporter_class: Type[Reporter]) -> None:
        """
        Register a new reporter type with the factory.
        
        BEGINNER NOTES:
        - This allows you to add new reporter types to the factory
        - It's like adding a new item to the restaurant menu
        - This makes the factory extensible without changing existing code
        
        Args:
            format: Report format to register
            reporter_class: Class that implements Reporter interface
            
        Raises:
            ValueError: If reporter_class does not implement Reporter interface
        """
        if not issubclass(reporter_class, Reporter):
            raise ValueError(f"Reporter class must implement Reporter interface")
        
        self._reporters[format] = reporter_class
    
    def get_available_formats(self) -> list[ReportFormat]:
        """
        Get list of available report formats.
        
        Returns:
            List of available ReportFormat values
        """
        return list(self._reporters.keys())

