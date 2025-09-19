"""
Models package for StressSpec.

Contains data models and structures used throughout the application.

BEGINNER NOTES:
- This file makes the 'models' directory a Python package
- It imports the Requirement class so other modules can use it easily
- __all__ defines what gets imported when someone does "from src.models import *"
- This is like a "menu" that shows what's available in this package
"""

from .requirement import Requirement  # Import our Requirement data model

# Define what gets imported when someone does "from src.models import *"
__all__ = ['Requirement']
