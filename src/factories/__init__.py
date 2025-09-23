"""
Factories package for StressSpec.

Contains factory classes for creating objects using the Factory Method pattern.

BEGINNER NOTES:
- This file makes the 'factories' directory a Python package
- It imports the factory classes
- __all__ defines what gets imported when someone does "from src.factories import *"
- This is like a "menu" that shows what factories are available
"""

from .detector_factory import RiskDetectorFactory

# Define what gets imported when someone does "from src.factories import *"
__all__ = ['RiskDetectorFactory']
