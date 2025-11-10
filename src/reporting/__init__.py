"""
Reporting package for StressSpec.

BEGINNER NOTES:
- This folder contains everything related to writing reports to files.
- Think of it like a "printing department" with different printers:
  - Markdown printer (pretty for humans)
  - CSV printer (good for spreadsheets)
  - JSON printer (good for other programs)
  - HTML printer (web-friendly with styling)
- The `base.py` file defines a simple interface (contract) that all printers follow.
"""

from .base import ReportFormat, ReportData, Reporter
from .markdown_reporter import MarkdownReporter
from .csv_reporter import CsvReporter
from .json_reporter import JsonReporter
from .html_reporter import HtmlReporter

__all__ = [
    "ReportFormat",
    "ReportData",
    "Reporter",
    "MarkdownReporter",
    "CsvReporter",
    "JsonReporter",
    "HtmlReporter",
]


