"""
Base risk detector module for StressSpec.

This module defines the abstract base class for all risk detectors.
Follows Template Method pattern and Strategy pattern from design decisions.

BEGINNER NOTES:
- This is like a "blueprint" that all risk detectors must follow
- It defines the common workflow that all detectors use
- It uses the Template Method pattern - defines the steps, lets subclasses fill in details
- It's like a recipe that says "check ingredients → cook → serve" but lets each chef decide how to cook
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.factories.risk_factory import RiskFactory

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.utils.text_normalizer import TextNormalizer
from src.utils.risk_id_generator import RiskIdGenerator
from src.config.detector_config_manager import DetectorConfigManager


class RiskDetector(ABC):
    """
    Abstract base class for all risk detectors.
    
    BEGINNER NOTES:
    - This is the "contract" that all risk detectors must follow
    - It's like a job description that says "all detectors must be able to detect risks"
    - It uses the Strategy pattern - different detectors can have different strategies
    - It's like saying "all cars must have wheels and an engine" but different car types
    
    This class defines the interface that all risk detectors must implement:
    - detect_risks(): Main detection method
    - get_detector_name(): Human-readable name
    - get_category(): Type of risks this detector finds
    """
    
    @abstractmethod
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """
        Detect risks in a single requirement.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of Risk objects representing detected issues
        """
        pass
    
    @abstractmethod
    def get_detector_name(self) -> str:
        """
        Get human-readable name of this detector.
        
        Returns:
            String name of the detector
        """
        pass
    
    @abstractmethod
    def get_category(self) -> RiskCategory:
        """
        Get the category of risks this detector finds.
        
        Returns:
            RiskCategory enum value
        """
        pass


class BaseRiskDetector(RiskDetector):
    """
    Base implementation for risk detectors with common functionality.
    
    BEGINNER NOTES:
    - This is like a "starter kit" for building risk detectors
    - It provides common tools and methods that all detectors need
    - It uses the Template Method pattern - defines the workflow, lets subclasses customize
    - It's like a cooking class that teaches the basic steps, but each student makes their own dish
    
    This class provides:
    - Configuration loading from rules.json
    - Common utility methods for text analysis
    - Template method for the detection workflow
    - Severity mapping and risk creation helpers
    """
    
    def __init__(self, rules_file: str = "data/rules.json",
                 text_normalizer: Optional[TextNormalizer] = None,
                 risk_id_generator: Optional[RiskIdGenerator] = None,
                 config_manager: Optional[DetectorConfigManager] = None,
                 risk_factory: Optional['RiskFactory'] = None):
        """
        Initialize the base detector with configuration.
        
        Args:
            rules_file: Path to the rules configuration file
            text_normalizer: Optional TextNormalizer instance (for dependency injection/testing)
            risk_id_generator: Optional RiskIdGenerator instance (for dependency injection/testing)
            config_manager: Optional DetectorConfigManager instance (for dependency injection/testing)
            risk_factory: Optional RiskFactory instance (for dependency injection/testing)
        """
        self.rules_file = rules_file
        self.config_manager = config_manager or DetectorConfigManager(rules_file)
        self.text_normalizer = text_normalizer or TextNormalizer()
        id_gen = risk_id_generator or RiskIdGenerator()
        if risk_factory is None:
            # Lazy import to avoid circular dependency
            from src.factories.risk_factory import RiskFactory
            self.risk_factory = RiskFactory(id_gen)
        else:
            self.risk_factory = risk_factory
        self._setup_detector()
    
    def _setup_detector(self) -> None:
        """
        Setup detector-specific configuration.
        
        BEGINNER NOTES:
        - This method is called after loading the configuration
        - Subclasses can override this to set up their specific rules
        - It's like a "customization step" after getting the basic ingredients
        """
        # Get detector-specific config
        detector_name = self.get_category().value
        self.detector_config = self.config_manager.get_detector_config(detector_name)
        
        # Get severity mapping
        self.severity_mapping = self.config_manager.get_severity_mapping()
        
        # Get global settings (store as dict for backward compatibility)
        self.global_settings = self.config_manager.config.get('global_settings', {})
        
        # Check if detector is enabled
        if not self.config_manager.is_detector_enabled(detector_name):
            raise ValueError(f"Detector {detector_name} is disabled in configuration")
    
    def get_severity_level(self, severity_str: str) -> SeverityLevel:
        """
        Convert string severity to SeverityLevel enum.
        
        Args:
            severity_str: String severity (e.g., "high", "medium")
            
        Returns:
            SeverityLevel enum value
            
        Raises:
            ValueError: If severity string is invalid
        """
        severity_map = {
            'low': SeverityLevel.LOW,
            'medium': SeverityLevel.MEDIUM,
            'high': SeverityLevel.HIGH,
            'critical': SeverityLevel.CRITICAL,
            'blocker': SeverityLevel.BLOCKER
        }
        
        severity_str = severity_str.lower()
        if severity_str not in severity_map:
            raise ValueError(f"Invalid severity level: {severity_str}")
        
        return severity_map[severity_str]
    
    def create_risk(self, 
                   requirement: Requirement,
                   description: str,
                   evidence: str,
                   severity: Optional[str] = None,
                   suggestion: Optional[str] = None) -> Risk:
        """
        Create a Risk object with proper ID and metadata.
        
        Args:
            requirement: The requirement where risk was found
            description: Human-readable description of the risk
            evidence: Specific text that triggered the risk
            severity: Override severity (defaults to detector's default)
            suggestion: Optional suggestion for fixing the risk
            
        Returns:
            Risk object with all metadata filled in
        """
        # Get severity level
        if severity is None:
            severity = self.detector_config.get('severity', 'medium')
        severity_level = self.get_severity_level(severity)
        
        # Use risk factory if provided, otherwise create directly
        if self.risk_factory:
            return self.risk_factory.create_risk(
                requirement=requirement,
                category=self.get_category(),
                description=description,
                evidence=evidence,
                severity=severity_level,
                suggestion=suggestion
            )
        else:
            # Fallback: create risk directly (for backward compatibility)
            risk_id = self.risk_id_generator.generate_id(requirement.id, self.get_category())
            return Risk(
                id=risk_id,
                category=self.get_category(),
                severity=severity_level,
                description=description,
                requirement_id=requirement.id,
                line_number=requirement.line_number,
                evidence=evidence,
                suggestion=suggestion
            )
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison (lowercase, strip whitespace).
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        case_sensitive = self.global_settings.get('case_sensitive', False)
        return self.text_normalizer.normalize_text(text, case_sensitive)
    
    def contains_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Check if text contains any of the specified keywords.
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            
        Returns:
            List of keywords found in the text
        """
        case_sensitive = self.global_settings.get('case_sensitive', False)
        return self.text_normalizer.contains_keywords(text, keywords, case_sensitive)
    
    def get_rule_config(self, rule_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific rule.
        
        Args:
            rule_name: Name of the rule to get config for
            
        Returns:
            Dictionary containing rule configuration
        """
        rules = self.detector_config.get('rules', {})
        return rules.get(rule_name, {})
    
    # Abstract methods that subclasses must implement
    @abstractmethod
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """Detect risks in a requirement. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_detector_name(self) -> str:
        """Get detector name. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_category(self) -> RiskCategory:
        """Get risk category. Must be implemented by subclasses."""
        pass

