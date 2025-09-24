"""
Risk detector factory module for StressSpec.

This module implements the Factory Method pattern for creating risk detectors.
Follows the Factory Method pattern from design decisions.

BEGINNER NOTES:
- This is like a "detector store" that creates different types of risk detectors
- It uses the Factory Method pattern - you ask for a detector by name, it creates the right one
- It's like a restaurant where you order "pizza" and the kitchen makes the right type of pizza
- All detectors are created through this factory, making it easy to add new ones
"""

from typing import Dict, List, Type
from src.models.risk import RiskCategory
from src.detectors.base import RiskDetector
from src.detectors.ambiguity_detector import AmbiguityDetector
from src.detectors.missing_detail_detector import MissingDetailDetector
from src.detectors.security_detector import SecurityDetector
from src.detectors.conflict_detector import ConflictDetector
from src.detectors.performance_detector import PerformanceDetector
from src.detectors.availability_detector import AvailabilityDetector


class RiskDetectorFactory:
    """
    Factory for creating risk detector instances.
    
    BEGINNER NOTES:
    - This factory is like a "detector store" that knows how to make different detectors
    - You ask for a detector by name (like "ambiguity"), and it creates the right one
    - It uses the Factory Method pattern - the factory method creates the right object
    - It makes it easy to add new detectors without changing existing code
    
    This factory can create:
    - AmbiguityDetector: Finds vague language
    - MissingDetailDetector: Finds incomplete requirements
    - SecurityDetector: Finds missing security requirements
    - ConflictDetector: Finds duplicate/contradictory requirements
    """
    
    # Registry of available detectors
    _detector_registry: Dict[str, Type[RiskDetector]] = {
        'ambiguity': AmbiguityDetector,
        'missing_detail': MissingDetailDetector,
        'security': SecurityDetector,
        'conflict': ConflictDetector,
        'performance': PerformanceDetector,
        'availability': AvailabilityDetector,
    }
    
    def __init__(self, rules_file: str = "data/rules.json"):
        """
        Initialize the factory with configuration.
        
        Args:
            rules_file: Path to the rules configuration file
        """
        self.rules_file = rules_file
        self._detector_cache: Dict[str, RiskDetector] = {}
    
    def create_detector(self, detector_type: str) -> RiskDetector:
        """
        Create a risk detector of the specified type.
        
        BEGINNER NOTES:
        - This is the main "factory method" that creates detectors
        - It's like ordering food - you say what you want, it makes it for you
        - It uses caching so the same detector isn't created multiple times
        - If you ask for an unknown detector, it tells you what's available
        
        Args:
            detector_type: Type of detector to create (e.g., 'ambiguity', 'security')
            
        Returns:
            RiskDetector instance of the requested type
            
        Raises:
            ValueError: If detector_type is not supported
        """
        # Normalize detector type
        detector_type = detector_type.lower()
        
        # Check if detector type is supported
        if detector_type not in self._detector_registry:
            available_types = ', '.join(self._detector_registry.keys())
            raise ValueError(f"Unknown detector type: '{detector_type}'. "
                           f"Available types: {available_types}")
        
        # Use cached detector if available
        if detector_type in self._detector_cache:
            return self._detector_cache[detector_type]
        
        # Create new detector instance
        detector_class = self._detector_registry[detector_type]
        detector = detector_class(rules_file=self.rules_file)
        
        # Cache the detector for future use
        self._detector_cache[detector_type] = detector
        
        return detector
    
    def create_all_detectors(self) -> List[RiskDetector]:
        """
        Create all available risk detectors.
        
        BEGINNER NOTES:
        - This creates one of each type of detector
        - It's like ordering "one of everything" from the menu
        - Useful when you want to run all detectors on requirements
        
        Returns:
            List of all available RiskDetector instances
        """
        detectors = []
        
        for detector_type in self._detector_registry.keys():
            try:
                detector = self.create_detector(detector_type)
                detectors.append(detector)
            except Exception as e:
                # Log the error but continue with other detectors
                print(f"Warning: Could not create {detector_type} detector: {e}")
        
        return detectors
    
    def create_enabled_detectors(self) -> List[RiskDetector]:
        """
        Create only detectors that are enabled in the configuration.
        
        BEGINNER NOTES:
        - This checks the rules.json file to see which detectors are enabled
        - It only creates detectors that are turned on
        - It's like only making the dishes that are available today
        
        Returns:
            List of enabled RiskDetector instances
        """
        enabled_detectors = []
        
        # Load configuration to check which detectors are enabled
        import json
        from pathlib import Path
        
        try:
            rules_path = Path(self.rules_file)
            if not rules_path.exists():
                # If no rules file, return all detectors
                return self.create_all_detectors()
            
            with open(rules_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            detectors_config = config.get('detectors', {})
            
            for detector_type, detector_config in detectors_config.items():
                if detector_config.get('enabled', False):
                    try:
                        detector = self.create_detector(detector_type)
                        enabled_detectors.append(detector)
                    except Exception as e:
                        print(f"Warning: Could not create {detector_type} detector: {e}")
        
        except Exception as e:
            print(f"Warning: Could not load configuration, using all detectors: {e}")
            return self.create_all_detectors()
        
        return enabled_detectors
    
    def get_available_detector_types(self) -> List[str]:
        """
        Get list of available detector types.
        
        Returns:
            List of detector type names
        """
        return list(self._detector_registry.keys())
    
    def register_detector(self, detector_type: str, detector_class: Type[RiskDetector]) -> None:
        """
        Register a new detector type with the factory.
        
        BEGINNER NOTES:
        - This allows you to add new detector types to the factory
        - It's like adding a new item to the restaurant menu
        - This makes the factory extensible without changing existing code
        
        Args:
            detector_type: Name of the detector type
            detector_class: Class that implements RiskDetector interface
        """
        if not issubclass(detector_class, RiskDetector):
            raise ValueError(f"Detector class must implement RiskDetector interface")
        
        self._detector_registry[detector_type.lower()] = detector_class
        
        # Remove from cache if it exists
        if detector_type.lower() in self._detector_cache:
            del self._detector_cache[detector_type.lower()]
    
    def get_detector_info(self) -> Dict[str, str]:
        """
        Get information about all available detectors.
        
        Returns:
            Dictionary mapping detector types to their descriptions
        """
        info = {}
        
        for detector_type in self._detector_registry.keys():
            try:
                detector = self.create_detector(detector_type)
                info[detector_type] = detector.get_detector_name()
            except Exception:
                info[detector_type] = f"{detector_type} (error creating)"
        
        return info
