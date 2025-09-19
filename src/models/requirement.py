"""
Requirement model for StressSpec.

This module defines the Requirement class that represents a single requirement
with its metadata and content.

BEGINNER NOTES:
- This is a "data model" - it defines what a requirement looks like
- Think of it like a form with specific fields that must be filled out
- It uses @dataclass which automatically creates useful methods for us
- It validates data to make sure it's correct (like a bouncer at a club)
"""

from dataclasses import dataclass  # Makes creating classes with data fields easier
from typing import Optional        # For type hints (makes code more readable)


@dataclass
class Requirement:
    """
    Represents a single requirement with its metadata.
    
    BEGINNER NOTES:
    - This is like a blueprint for what a requirement should contain
    - Each requirement has 3 pieces of information: ID, line number, and text
    - @dataclass automatically creates __init__, __str__, __eq__, etc. for us
    - This follows the "Single Responsibility Principle" - it only handles requirement data
    
    Attributes:
        id: Unique identifier for the requirement (e.g., R001, R002)
        line_number: Line number in the original file (for traceability)
        text: The actual requirement text (what the requirement says)
    """
    id: str          # Unique ID like "R001", "R002", etc.
    line_number: int # Which line in the file this came from
    text: str        # The actual requirement text
    
    def __post_init__(self) -> None:
        """
        Validate the requirement data after initialization.
        
        BEGINNER NOTES:
        - This runs automatically after the object is created
        - It's like a quality check to make sure the data is valid
        - If data is invalid, it raises an error (stops the program)
        - This prevents bugs later by catching problems early
        """
        # Check if ID is empty
        if not self.id:
            raise ValueError("Requirement ID cannot be empty")
        
        # Check if line number is positive (1, 2, 3, etc.)
        if self.line_number <= 0:
            raise ValueError("Line number must be positive")
        
        # Check if text is empty or just whitespace
        if not self.text or not self.text.strip():
            raise ValueError("Requirement text cannot be empty")
    
    def __str__(self) -> str:
        """
        String representation of the requirement.
        
        BEGINNER NOTES:
        - This defines what happens when you print() a Requirement object
        - It's like a "business card" - shows the most important info
        - Example: "R001: The system shall allow users to login"
        """
        return f"{self.id}: {self.text}"
    
    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.
        
        BEGINNER NOTES:
        - This is for developers when debugging code
        - It shows ALL the information about the object
        - It's like a "detailed report" vs the "business card" above
        - [:50] means "only show first 50 characters" to keep it readable
        """
        return f"Requirement(id='{self.id}', line={self.line_number}, text='{self.text[:50]}...')"
