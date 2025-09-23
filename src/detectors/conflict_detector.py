"""
Conflict detector module for StressSpec.

This module detects duplicate or contradictory requirements.
Follows the Strategy pattern and inherits from BaseRiskDetector.

BEGINNER NOTES:
- This detector looks for requirements that conflict with each other
- It's like a "consistency checker" that finds contradictions
- It can detect duplicate requirements and contradictory language
- It helps ensure requirements are consistent and non-conflicting
"""

from typing import List, Dict, Tuple
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector
import difflib


class ConflictDetector(BaseRiskDetector):
    """
    Detects duplicate or contradictory requirements.
    
    BEGINNER NOTES:
    - This detector is like a "consistency checker" for requirements
    - It looks for requirements that contradict each other or are duplicates
    - Examples: "must" vs "must not", very similar requirements
    - It helps ensure requirements are consistent and don't conflict
    
    This detector finds:
    - Duplicate requirements that are very similar
    - Contradictory terms within or between requirements
    - Conflicting priorities that may cause issues
    """
    
    def __init__(self, rules_file: str = "data/rules.json"):
        """
        Initialize the conflict detector.
        
        Args:
            rules_file: Path to the rules configuration file
        """
        super().__init__(rules_file)
        self._requirement_cache = {}  # Cache for similarity calculations
    
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """
        Analyze a requirement for conflicts with other requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of Risk objects representing conflicts found
        """
        risks = []
        
        # Check for contradictory terms within the requirement
        contradiction_risks = self._detect_contradictory_terms(requirement)
        risks.extend(contradiction_risks)
        
        # Check for conflicting priorities
        priority_risks = self._detect_conflicting_priorities(requirement)
        risks.extend(priority_risks)
        
        return risks
    
    def detect_duplicate_risks(self, requirements: List[Requirement]) -> List[Risk]:
        """
        Detect duplicate requirements across the entire set.
        
        Args:
            requirements: List of all requirements to analyze
            
        Returns:
            List of Risk objects representing duplicates found
        """
        risks = []
        
        # Get duplicate detection configuration
        rule_config = self.get_rule_config('duplicate_requirements')
        similarity_threshold = rule_config.get('similarity_threshold', 0.8)
        
        # Compare each requirement with all others
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements[i+1:], i+1):
                similarity = self._calculate_similarity(req1.text, req2.text)
                
                if similarity >= similarity_threshold:
                    risk = self.create_risk(
                        requirement=req1,
                        description=f"Duplicate requirement detected - {similarity:.1%} similar to {req2.id}",
                        evidence=f"Similar to: {req2.text[:50]}...",
                        suggestion=f"Consider merging or clarifying the difference between {req1.id} and {req2.id}"
                    )
                    risks.append(risk)
        
        return risks
    
    def _detect_contradictory_terms(self, requirement: Requirement) -> List[Risk]:
        """
        Detect contradictory terms within a requirement.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for contradictory terms found
        """
        risks = []
        
        # Get contradictory terms configuration
        rule_config = self.get_rule_config('contradictory_terms')
        contradictory_pairs = rule_config.get('pairs', [])
        
        if not contradictory_pairs:
            return risks
        
        normalized_text = self.normalize_text(requirement.text)
        
        for positive_term, negative_term in contradictory_pairs:
            # Check if both terms appear in the requirement
            has_positive = self.normalize_text(positive_term) in normalized_text
            has_negative = self.normalize_text(negative_term) in normalized_text
            
            if has_positive and has_negative:
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"Contradictory terms found: '{positive_term}' and '{negative_term}'",
                    evidence=f"'{positive_term}' and '{negative_term}'",
                    suggestion=f"Clarify the requirement - it cannot both {positive_term} and {negative_term}"
                )
                risks.append(risk)
        
        return risks
    
    def _detect_conflicting_priorities(self, requirement: Requirement) -> List[Risk]:
        """
        Detect conflicting priority language in requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for conflicting priorities found
        """
        risks = []
        
        # Get conflicting priorities configuration
        rule_config = self.get_rule_config('conflicting_priorities')
        priority_keywords = rule_config.get('keywords', [])
        context_required = rule_config.get('context_required', True)
        
        if not priority_keywords:
            return risks
        
        # Find priority keywords in the requirement text
        found_priorities = self.contains_keywords(requirement.text, priority_keywords)
        
        # If multiple urgent terms are found, it might indicate conflicting priorities
        if len(found_priorities) > 1:
            risk = self.create_risk(
                requirement=requirement,
                description=f"Multiple urgent priority terms found: {', '.join(found_priorities)}",
                evidence=', '.join(found_priorities),
                suggestion="Clarify the actual priority level - multiple urgent terms may indicate confusion"
            )
            risks.append(risk)
        
        return risks
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using sequence matching.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize texts
        norm_text1 = self.normalize_text(text1)
        norm_text2 = self.normalize_text(text2)
        
        # Use difflib to calculate similarity
        similarity = difflib.SequenceMatcher(None, norm_text1, norm_text2).ratio()
        
        return similarity
    
    def get_detector_name(self) -> str:
        """
        Get human-readable name of this detector.
        
        Returns:
            String name of the detector
        """
        return "Conflict Detector"
    
    def get_category(self) -> RiskCategory:
        """
        Get the category of risks this detector finds.
        
        Returns:
            RiskCategory enum value for conflict
        """
        return RiskCategory.CONFLICT
