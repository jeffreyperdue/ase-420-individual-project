"""
Requirement parser module for StressSpec.

This module handles parsing of raw requirement lines into structured Requirement objects.
Follows Single Responsibility Principle by focusing only on parsing logic.

BEGINNER NOTES:
- This is like a "translator" who converts plain text into structured data
- It takes clean text lines and turns them into Requirement objects with IDs
- It's like a factory worker who takes raw materials and makes finished products
- It only cares about parsing - it doesn't read files or display results
"""

from typing import List  # For type hints (makes code more readable)
from src.models.requirement import Requirement  # The data structure we're creating


class RequirementParser:
    """
    Parses raw requirement lines into structured Requirement objects.
    
    BEGINNER NOTES:
    - This class is like a "factory" that makes Requirement objects
    - It takes plain text and adds structure (IDs, line numbers, etc.)
    - It's like a label maker that puts ID stickers on products
    
    This class is responsible for:
    - Assigning unique IDs to requirements (R001, R002, R003, etc.)
    - Tracking line numbers (which line in the file each requirement came from)
    - Creating Requirement objects (the finished products)
    """
    
    def __init__(self):
        """
        Initialize the parser.
        
        BEGINNER NOTES:
        - This sets up the "factory" when it's first created
        - _id_counter keeps track of what ID to assign next
        - The underscore (_) means "this is private - don't use it from outside"
        """
        self._id_counter = 0  # Start counting from 0, first requirement will be R001
    
    def parse_requirements(self, lines: List[str]) -> List[Requirement]:
        """
        Parse a list of requirement lines into Requirement objects.
        
        BEGINNER NOTES:
        - This is the main "work" function of the parser
        - It's like an assembly line: take text → add ID → add line number → create object
        - enumerate() gives us both the position (line_number) and the content (line_text)
        
        Args:
            lines: List of processed requirement lines (clean text from FileLoader)
            
        Returns:
            List of Requirement objects with assigned IDs and line numbers
        """
        requirements = []  # Start with empty list - we'll add Requirement objects here
        
        # Go through each line and convert it to a Requirement object
        # enumerate(lines, start=1) gives us: (1, "first line"), (2, "second line"), etc.
        for line_number, line_text in enumerate(lines, start=1):
            # Step 1: Generate a unique ID for this requirement
            requirement_id = self._generate_id()
            
            # Step 2: Create a Requirement object with all the information
            requirement = Requirement(
                id=requirement_id,        # Unique ID like "R001"
                line_number=line_number,  # Which line this came from (1, 2, 3, etc.)
                text=line_text           # The actual requirement text
            )
            
            # Step 3: Add the new Requirement to our list
            requirements.append(requirement)
        
        return requirements  # Return the list of finished Requirement objects
    
    def _generate_id(self) -> str:
        """
        Generate a unique requirement ID.
        
        BEGINNER NOTES:
        - This is a "helper" function (starts with _) - used internally
        - It's like a number stamp that prints the next ID in sequence
        - :03d means "format as 3 digits with leading zeros" (001, 002, 003, etc.)
        
        Returns:
            Unique ID in format R001, R002, R003, etc.
        """
        self._id_counter += 1  # Increment counter (0→1, 1→2, 2→3, etc.)
        return f"R{self._id_counter:03d}"  # Format as "R001", "R002", etc.
    
    def reset_counter(self) -> None:
        """
        Reset the ID counter (useful for testing).
        
        BEGINNER NOTES:
        - This is like resetting a counter to start over
        - Mainly used in tests to make sure each test starts fresh
        - In real use, we usually want IDs to keep incrementing
        """
        self._id_counter = 0  # Start counting from 0 again
