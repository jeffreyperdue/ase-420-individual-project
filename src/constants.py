"""
Application-wide constants for StressSpec.

This module contains all application-wide constants to avoid magic numbers
and hard-coded strings throughout the codebase.
"""

from src.models.risk import SeverityLevel
from src.reporting import ReportFormat


class Constants:
    """Application-wide constants."""
    DEFAULT_RULES_FILE = "data/rules.json"
    DEFAULT_REPORT_FORMAT = ReportFormat.MD
    SUPPORTED_FILE_EXTENSIONS = {'.txt', '.md'}
    DEFAULT_SEVERITY = SeverityLevel.MEDIUM
    RISK_ID_FORMAT = "{requirement_id}-{category}-{counter:03d}"
    REQUIREMENT_ID_FORMAT = "R{counter:03d}"


class AnalysisProgress:
    """Constants for analysis progress stages."""
    LOADING = 10
    PARSING = 30
    DETECTING = 50
    SCORING = 70
    GENERATING = 80
    COMPLETE = 100

