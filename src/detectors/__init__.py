"""
Detectors package for StressSpec.

Contains risk detection modules that analyze requirements for various types of risks.

BEGINNER NOTES:
- This file makes the 'detectors' directory a Python package
- It imports the base classes and detector implementations
- __all__ defines what gets imported when someone does "from src.detectors import *"
- This is like a "menu" that shows what detectors are available
"""

from .base import BaseRiskDetector, RiskDetector
from .ambiguity_detector import AmbiguityDetector
from .missing_detail_detector import MissingDetailDetector
from .security_detector import SecurityDetector
from .conflict_detector import ConflictDetector

# Define what gets imported when someone does "from src.detectors import *"
__all__ = [
    'BaseRiskDetector',
    'RiskDetector', 
    'AmbiguityDetector',
    'MissingDetailDetector',
    'SecurityDetector',
    'ConflictDetector'
]
