"""
Risk factory for StressSpec.

This module provides functionality for creating Risk objects with proper
ID generation and validation.

BEGINNER NOTES:
- This factory creates Risk objects with all required fields
- It uses RiskIdGenerator to ensure unique IDs
- It follows the Single Responsibility Principle - only handles risk creation
- It makes risk creation easier to test and mock
"""

from typing import Optional
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.utils.risk_id_generator import RiskIdGenerator


class RiskFactory:
    """
    Creates Risk objects with proper ID generation and validation.
    
    BEGINNER NOTES:
    - This factory is like a "risk object maker" that creates properly formatted risks
    - It ensures all risks have unique IDs and proper metadata
    - It can be used by detectors or any component that needs to create risks
    - It makes risk creation consistent across the application
    
    This factory provides:
    - Risk object creation with auto-generated IDs
    - Proper metadata assignment (requirement ID, line number, etc.)
    - Validation of risk data
    """
    
    def __init__(self, id_generator: Optional[RiskIdGenerator] = None):
        """
        Initialize the risk factory.
        
        Args:
            id_generator: Optional RiskIdGenerator instance (for dependency injection/testing)
        """
        self.id_generator = id_generator or RiskIdGenerator()
    
    def create_risk(self, 
                   requirement: Requirement,
                   category: RiskCategory,
                   description: str,
                   evidence: str,
                   severity: SeverityLevel,
                   suggestion: Optional[str] = None) -> Risk:
        """
        Create a Risk object with auto-generated ID.
        
        Args:
            requirement: The requirement where risk was found
            category: Type of risk (ambiguity, security, etc.)
            description: Human-readable description of the risk
            evidence: Specific text that triggered the risk
            severity: Severity level of the risk
            suggestion: Optional suggestion for fixing the risk
            
        Returns:
            Risk object with all metadata filled in and unique ID
        """
        # Generate unique risk ID
        risk_id = self.id_generator.generate_id(requirement.id, category)
        
        # Create and return Risk object
        return Risk(
            id=risk_id,
            category=category,
            severity=severity,
            description=description,
            requirement_id=requirement.id,
            line_number=requirement.line_number,
            evidence=evidence,
            suggestion=suggestion
        )

