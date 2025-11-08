from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from src.models.requirement import Requirement
from src.models.risk import Risk


class ReportFormat(str, Enum):
    """Supported output formats for reports."""
    MD = "md"
    CSV = "csv"
    JSON = "json"


@dataclass
class ReportData:
    """
    Container for everything a reporter needs to write a file.

    BEGINNER NOTES:
    - `requirements`: the list of parsed requirements (with id, line, text)
    - `risks_by_requirement`: a dictionary mapping requirement id → list of risks
    - `source_file`: the original input file path for traceability
    - `top_5_riskiest`: optional list of top 5 riskiest requirements with scores (for Week 8 feature)
    """
    requirements: List[Requirement]
    risks_by_requirement: Dict[str, List[Risk]]
    source_file: str
    top_5_riskiest: Optional[List[Dict]] = None


class Reporter:
    """
    Simple interface (contract) for all reporters.

    BEGINNER NOTES:
    - Any reporter must implement `write(data, output)` and return the file path
    - This allows the main program to treat all reporters the same way
    """
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        raise NotImplementedError


