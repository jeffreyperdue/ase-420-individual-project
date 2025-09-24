"""
Analyzer orchestrates running risk detectors against requirements and aggregating results.

BEGINNER NOTES:
- Think of this like the "work coordinator". It hands each requirement to
  each detector and collects all the risks in one place.
- It returns a dictionary so it's easy to find the risks for any requirement id.
"""

from typing import Dict, List

from src.models.requirement import Requirement
from src.models.risk import Risk
from src.detectors.base import RiskDetector


def analyze_requirements(
    requirements: List[Requirement],
    detectors: List[RiskDetector],
) -> Dict[str, List[Risk]]:
    """
    Run all detectors against each requirement and return risks grouped by requirement id.
    """
    risks_by_requirement: Dict[str, List[Risk]] = {req.id: [] for req in requirements}

    for requirement in requirements:
        for detector in detectors:
            try:
                risks = detector.detect_risks(requirement)
            except Exception:
                # If a detector fails, we skip it to keep the app running
                risks = []
            if risks:
                risks_by_requirement[requirement.id].extend(risks)

    return risks_by_requirement


