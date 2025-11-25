"""
Risk ID generator for StressSpec.

This module provides functionality for generating unique risk IDs
based on requirement IDs and risk categories.

BEGINNER NOTES:
- This class handles the generation of unique risk IDs
- It tracks counters per requirement-category combination
- It follows the Single Responsibility Principle - only handles ID generation
"""

from typing import Dict
from src.models.risk import RiskCategory


class RiskIdGenerator:
    """
    Generates unique risk IDs.
    
    BEGINNER NOTES:
    - This class is like a "numbering machine" that creates unique IDs
    - It keeps track of how many risks have been created for each requirement-category pair
    - It ensures each risk gets a unique ID like "R001-AMB-001", "R001-AMB-002", etc.
    
    This class provides:
    - Unique ID generation per requirement-category combination
    - Counter tracking for sequential numbering
    - Reset functionality for testing
    """
    
    def __init__(self):
        """Initialize the risk ID generator with empty counters."""
        self._counters: Dict[str, int] = {}
    
    def generate_id(self, requirement_id: str, category: RiskCategory) -> str:
        """
        Generate unique risk ID for requirement and category.
        
        Args:
            requirement_id: ID of the requirement (e.g., "R001")
            category: Risk category enum value
            
        Returns:
            Unique risk ID in format "{requirement_id}-{CATEGORY}-{counter:03d}"
            Example: "R001-AMB-001", "R001-SEC-001", "R002-AMB-001"
        """
        # Create a key from requirement ID and category
        key = f"{requirement_id}-{category.value}"
        
        # Increment counter for this key
        self._counters[key] = self._counters.get(key, 0) + 1
        counter = self._counters[key]
        
        # Generate ID: R001-AMB-001, R001-AMB-002, etc.
        category_prefix = category.value.upper()[:3]  # First 3 letters, uppercase
        return f"{requirement_id}-{category_prefix}-{counter:03d}"
    
    def reset(self) -> None:
        """
        Reset all counters (useful for testing).
        
        BEGINNER NOTES:
        - This clears all the counters so ID generation starts fresh
        - Mainly used in tests to ensure consistent behavior
        """
        self._counters.clear()
    
    def get_counter(self, requirement_id: str, category: RiskCategory) -> int:
        """
        Get current counter value for a requirement-category combination.
        
        Args:
            requirement_id: ID of the requirement
            category: Risk category
            
        Returns:
            Current counter value (0 if never used)
        """
        key = f"{requirement_id}-{category.value}"
        return self._counters.get(key, 0)

