"""
Ambiguity detector module for StressSpec.

This module detects vague or ambiguous language in requirements.
Follows the Strategy pattern and inherits from BaseRiskDetector.

BEGINNER NOTES:
- This detector looks for vague terms that make requirements unclear
- It's like a grammar checker that flags imprecise language
- Each vague term found creates a risk flag with medium severity
- It uses the configuration from rules.json to define what terms are vague
"""

from typing import List
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class AmbiguityDetector(BaseRiskDetector):
    """
    Detects ambiguous language in requirements.
    
    BEGINNER NOTES:
    - This detector is like a "precision checker" for requirements
    - It looks for words that are too vague or imprecise
    - Examples: "should" instead of "shall", "fast" instead of "within 2 seconds"
    - It helps make requirements more specific and testable
    
    This detector finds:
    - Vague terms like "should", "might", "could"
    - Imprecise quantifiers like "some", "many", "fast"
    - Weak requirement language like "preferably", "ideally"
    """
    
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """
        Analyze a requirement for ambiguous language.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of Risk objects representing ambiguity issues found
        """
        risks = []
        
        # Check for vague terms
        vague_risks = self._detect_vague_terms(requirement)
        risks.extend(vague_risks)
        
        # Check for imprecise quantifiers
        quantifier_risks = self._detect_imprecise_quantifiers(requirement)
        risks.extend(quantifier_risks)
        
        # Check for weak requirement language
        weak_risks = self._detect_weak_requirements(requirement)
        risks.extend(weak_risks)
        
        return risks
    
    def _detect_vague_terms(self, requirement: Requirement) -> List[Risk]:
        """
        Detect vague terms that make requirements unclear.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for vague terms found
        """
        risks = []
        
        # Get vague terms from configuration
        rule_config = self.get_rule_config('vague_terms')
        vague_keywords = rule_config.get('keywords', [])
        
        if not vague_keywords:
            return risks
        
        # Find vague terms in the requirement text
        found_terms = self.contains_keywords(requirement.text, vague_keywords)
        
        for term in found_terms:
            risk = self.create_risk(
                requirement=requirement,
                description=f"Vague term '{term}' found - consider using more precise language",
                evidence=term,
                suggestion=f"Replace '{term}' with more specific language (e.g., 'shall', 'must', 'will')"
            )
            risks.append(risk)
        
        return risks
    
    def _detect_imprecise_quantifiers(self, requirement: Requirement) -> List[Risk]:
        """
        Detect imprecise quantifiers and subjective terms.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for imprecise quantifiers found
        """
        risks = []
        
        # Get imprecise quantifiers from configuration
        rule_config = self.get_rule_config('imprecise_quantifiers')
        quantifier_keywords = rule_config.get('keywords', [])
        
        if not quantifier_keywords:
            return risks
        
        # Find imprecise quantifiers in the requirement text
        found_quantifiers = self.contains_keywords(requirement.text, quantifier_keywords)
        
        for quantifier in found_quantifiers:
            risk = self.create_risk(
                requirement=requirement,
                description=f"Imprecise quantifier '{quantifier}' found - specify exact values or criteria",
                evidence=quantifier,
                suggestion=f"Replace '{quantifier}' with specific values (e.g., 'at least 5', 'within 2 seconds', '99.9% uptime')"
            )
            risks.append(risk)
        
        return risks
    
    def _detect_weak_requirements(self, requirement: Requirement) -> List[Risk]:
        """
        Detect weak requirement language that lacks commitment.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for weak requirement language found
        """
        risks = []
        
        # Get weak requirement keywords from configuration
        rule_config = self.get_rule_config('weak_requirements')
        weak_keywords = rule_config.get('keywords', [])
        
        if not weak_keywords:
            return risks
        
        # Find weak requirement language in the requirement text
        found_weak_terms = self.contains_keywords(requirement.text, weak_keywords)
        
        for weak_term in found_weak_terms:
            risk = self.create_risk(
                requirement=requirement,
                description=f"Weak requirement language '{weak_term}' found - requirements should be definitive",
                evidence=weak_term,
                suggestion=f"Replace '{weak_term}' with stronger language (e.g., 'shall', 'must', 'will')"
            )
            risks.append(risk)
        
        return risks
    
    def get_detector_name(self) -> str:
        """
        Get human-readable name of this detector.
        
        Returns:
            String name of the detector
        """
        return "Ambiguity Detector"
    
    def get_category(self) -> RiskCategory:
        """
        Get the category of risks this detector finds.
        
        Returns:
            RiskCategory enum value for ambiguity
        """
        return RiskCategory.AMBIGUITY

