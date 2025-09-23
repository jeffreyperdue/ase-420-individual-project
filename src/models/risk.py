"""
Risk model for StressSpec.

This module defines the Risk class that represents a detected risk
with its metadata and severity information.

BEGINNER NOTES:
- This is a "data model" that represents a risk found in a requirement
- Think of it like a "warning label" that describes what's wrong
- It uses @dataclass for clean, immutable data structures
- It validates data to ensure risk information is complete and correct
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for detected risks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    BLOCKER = 5


class RiskCategory(Enum):
    """Categories of risks that can be detected."""
    AMBIGUITY = "ambiguity"
    MISSING_DETAIL = "missing_detail"
    SECURITY = "security"
    CONFLICT = "conflict"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"


@dataclass
class Risk:
    """
    Represents a detected risk in a requirement.
    
    BEGINNER NOTES:
    - This is like a "warning ticket" that describes a problem found
    - Each risk has several pieces of information: what, where, how serious
    - @dataclass automatically creates useful methods for us
    - This follows the "Single Responsibility Principle" - it only handles risk data
    
    Attributes:
        id: Unique identifier for the risk (e.g., R001-AMB-001)
        category: Type of risk (ambiguity, security, etc.)
        severity: How serious the risk is (1-5 scale)
        description: Human-readable description of the risk
        requirement_id: ID of the requirement where risk was found
        line_number: Line number in the original file
        evidence: Specific text or pattern that triggered the risk
        suggestion: Optional suggestion for fixing the risk
    """
    id: str                    # Unique ID like "R001-AMB-001"
    category: RiskCategory     # Type of risk (ambiguity, security, etc.)
    severity: SeverityLevel    # How serious (1-5 scale)
    description: str          # Human-readable description
    requirement_id: str       # ID of the requirement (e.g., "R001")
    line_number: int         # Line number in original file
    evidence: str            # Specific text that triggered the risk
    suggestion: Optional[str] = None  # Optional fix suggestion
    
    def __post_init__(self) -> None:
        """
        Validate the risk data after initialization.
        
        BEGINNER NOTES:
        - This runs automatically after the object is created
        - It's like a quality check to make sure the risk data is valid
        - If data is invalid, it raises an error (stops the program)
        - This prevents bugs later by catching problems early
        """
        # Check if ID is empty
        if not self.id:
            raise ValueError("Risk ID cannot be empty")
        
        # Check if category is valid
        if not isinstance(self.category, RiskCategory):
            raise ValueError("Risk category must be a RiskCategory enum")
        
        # Check if severity is valid
        if not isinstance(self.severity, SeverityLevel):
            raise ValueError("Risk severity must be a SeverityLevel enum")
        
        # Check if description is empty
        if not self.description or not self.description.strip():
            raise ValueError("Risk description cannot be empty")
        
        # Check if requirement_id is empty
        if not self.requirement_id:
            raise ValueError("Requirement ID cannot be empty")
        
        # Check if line number is positive
        if self.line_number <= 0:
            raise ValueError("Line number must be positive")
        
        # Check if evidence is empty
        if not self.evidence or not self.evidence.strip():
            raise ValueError("Risk evidence cannot be empty")
    
    def __str__(self) -> str:
        """
        String representation of the risk.
        
        BEGINNER NOTES:
        - This defines what happens when you print() a Risk object
        - It's like a "warning message" - shows the most important info
        - Example: "HIGH: Ambiguity detected in R001 - vague term 'should' found"
        """
        return f"{self.severity.name}: {self.description} in {self.requirement_id}"
    
    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.
        
        BEGINNER NOTES:
        - This is for developers when debugging code
        - It shows ALL the information about the risk
        - It's like a "detailed incident report" vs the "warning message" above
        """
        return (f"Risk(id='{self.id}', category={self.category.value}, "
                f"severity={self.severity.name}, req='{self.requirement_id}', "
                f"line={self.line_number})")
    
    def to_dict(self) -> dict:
        """
        Convert risk to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the risk
        """
        return {
            "id": self.id,
            "category": self.category.value,
            "severity": self.severity.value,
            "severity_name": self.severity.name,
            "description": self.description,
            "requirement_id": self.requirement_id,
            "line_number": self.line_number,
            "evidence": self.evidence,
            "suggestion": self.suggestion
        }
    
    def get_severity_score(self) -> int:
        """
        Get numeric severity score for calculations.
        
        Returns:
            Integer severity score (1-5)
        """
        return self.severity.value
    
    def is_critical(self) -> bool:
        """
        Check if risk is critical or higher.
        
        Returns:
            True if severity is HIGH, CRITICAL, or BLOCKER
        """
        return self.severity.value >= SeverityLevel.HIGH.value
