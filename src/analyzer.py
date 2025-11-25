"""
Analyzer orchestrates running risk detectors against requirements and aggregating results.

BEGINNER NOTES:
- Think of this like the "work coordinator". It hands each requirement to
  each detector and collects all the risks in one place.
- It returns a dictionary so it's easy to find the risks for any requirement id.
"""

from typing import Dict, List, Optional

from src.models.requirement import Requirement
from src.models.risk import Risk
from src.detectors.base import RiskDetector
from src.utils.detector_error_handler import DetectorErrorHandler
from src.patterns.chain_of_responsibility import RiskFilter


def analyze_requirements(
    requirements: List[Requirement],
    detectors: List[RiskDetector],
    error_handler: Optional[DetectorErrorHandler] = None,
    risk_filter: Optional[RiskFilter] = None
) -> Dict[str, List[Risk]]:
    """
    Run all detectors against each requirement and return risks grouped by requirement id.
    
    Args:
        requirements: List of requirements to analyze
        detectors: List of detectors to run
        error_handler: Optional error handler (defaults to DetectorErrorHandler with logging)
        risk_filter: Optional risk filter chain (Chain of Responsibility pattern)
        
    Returns:
        Dictionary mapping requirement ID to list of risks
    """
    error_handler = error_handler or DetectorErrorHandler()
    risks_by_requirement: Dict[str, List[Risk]] = {req.id: [] for req in requirements}

    for requirement in requirements:
        for detector in detectors:
            try:
                risks = detector.detect_risks(requirement)
            except Exception as e:
                # Use error handler to handle the error
                risks = error_handler.handle_detector_error(detector, requirement, e)
            
            # Apply risk filter chain if provided (Chain of Responsibility pattern)
            if risks and risk_filter:
                risks = risk_filter.filter(risks)
            
            if risks:
                risks_by_requirement[requirement.id].extend(risks)

    return risks_by_requirement


