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
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel


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
    
    def __init__(self, rules_file: str = "data/rules.json"):
        """
        Initialize the base detector with configuration.
        
        Args:
            rules_file: Path to the rules configuration file
        """
        self.rules_file = rules_file
        self.config = self._load_configuration()
        self._setup_detector()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """
        Load configuration from rules.json file.
        
        Returns:
            Dictionary containing detector configuration
            
        Raises:
            FileNotFoundError: If rules file doesn't exist
            ValueError: If rules file is invalid JSON
        """
        try:
            rules_path = Path(self.rules_file)
            if not rules_path.exists():
                raise FileNotFoundError(f"Rules file not found: {self.rules_file}")
            
            with open(rules_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in rules file {self.rules_file}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading rules file {self.rules_file}: {e}")
    
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
        self.detector_config = self.config.get('detectors', {}).get(detector_name, {})
        
        # Get severity mapping
        self.severity_mapping = self.config.get('severity_mapping', {})
        
        # Get global settings
        self.global_settings = self.config.get('global_settings', {})
        
        # Check if detector is enabled
        if not self.detector_config.get('enabled', False):
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
        # Generate unique risk ID
        risk_id = f"{requirement.id}-{self.get_category().value.upper()[:3]}-001"
        
        # Get severity level
        if severity is None:
            severity = self.detector_config.get('severity', 'medium')
        severity_level = self.get_severity_level(severity)
        
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
        if not self.global_settings.get('case_sensitive', False):
            text = text.lower()
        return text.strip()
    
    def contains_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Check if text contains any of the specified keywords.
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            
        Returns:
            List of keywords found in the text
        """
        normalized_text = self.normalize_text(text)
        found_keywords = []
        
        for keyword in keywords:
            normalized_keyword = self.normalize_text(keyword)
            if normalized_keyword in normalized_text:
                found_keywords.append(keyword)
        
        return found_keywords
    
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
