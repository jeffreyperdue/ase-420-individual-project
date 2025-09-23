"""
Missing detail detector module for StressSpec.

This module detects incomplete or missing detail in requirements.
Follows the Strategy pattern and inherits from BaseRiskDetector.

BEGINNER NOTES:
- This detector looks for requirements that are incomplete or lack specifics
- It's like a "completeness checker" for requirements
- It flags requirements that end abruptly or lack necessary details
- It helps ensure requirements are specific enough to be testable
"""

from typing import List
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class MissingDetailDetector(BaseRiskDetector):
    """
    Detects missing details and incomplete requirements.
    
    BEGINNER NOTES:
    - This detector is like a "completeness checker" for requirements
    - It looks for requirements that are too vague or incomplete
    - Examples: "The system shall handle users" (how? what specifically?)
    - It helps make requirements more complete and actionable
    
    This detector finds:
    - Incomplete phrases that end without specifics
    - Missing specifications for actions
    - Unspecified or ambiguous actors
    """
    
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """
        Analyze a requirement for missing details.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of Risk objects representing missing detail issues found
        """
        risks = []
        
        # Check for incomplete phrases
        incomplete_risks = self._detect_incomplete_phrases(requirement)
        risks.extend(incomplete_risks)
        
        # Check for missing specifications
        missing_spec_risks = self._detect_missing_specifications(requirement)
        risks.extend(missing_spec_risks)
        
        # Check for unspecified actors
        actor_risks = self._detect_unspecified_actors(requirement)
        risks.extend(actor_risks)
        
        return risks
    
    def _detect_incomplete_phrases(self, requirement: Requirement) -> List[Risk]:
        """
        Detect incomplete phrases that end without specifying what should be done.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for incomplete phrases found
        """
        risks = []
        
        # Get incomplete phrase patterns from configuration
        rule_config = self.get_rule_config('incomplete_phrases')
        incomplete_patterns = rule_config.get('patterns', [])
        
        if not incomplete_patterns:
            return risks
        
        normalized_text = self.normalize_text(requirement.text)
        
        for pattern in incomplete_patterns:
            normalized_pattern = self.normalize_text(pattern)
            
            # Check if the requirement starts with the pattern but doesn't continue
            if normalized_text.startswith(normalized_pattern):
                # Check if there's more content after the pattern
                remaining_text = normalized_text[len(normalized_pattern):].strip()
                
                # If there's little content after the pattern, it's likely incomplete
                if len(remaining_text) < 10:  # Arbitrary threshold for "enough detail"
                    risk = self.create_risk(
                        requirement=requirement,
                        description=f"Incomplete phrase detected - requirement ends without specifying what should be done",
                        evidence=pattern,
                        suggestion=f"Complete the requirement by specifying what the system should do after '{pattern}'"
                    )
                    risks.append(risk)
        
        return risks
    
    def _detect_missing_specifications(self, requirement: Requirement) -> List[Risk]:
        """
        Detect actions without specific details about how they should be performed.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for missing specifications found
        """
        risks = []
        
        # Get missing specification keywords from configuration
        rule_config = self.get_rule_config('missing_specifications')
        action_keywords = rule_config.get('keywords', [])
        context_required = rule_config.get('context_required', True)
        
        if not action_keywords:
            return risks
        
        # Find action keywords in the requirement text
        found_actions = self.contains_keywords(requirement.text, action_keywords)
        
        for action in found_actions:
            # Check if the action has sufficient context/details
            if self._lacks_sufficient_context(requirement.text, action):
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"Action '{action}' lacks sufficient detail about how it should be performed",
                    evidence=action,
                    suggestion=f"Specify how '{action}' should be performed (e.g., when, where, under what conditions)"
                )
                risks.append(risk)
        
        return risks
    
    def _detect_unspecified_actors(self, requirement: Requirement) -> List[Risk]:
        """
        Detect unspecified or ambiguous actors in requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for unspecified actors found
        """
        risks = []
        
        # Get unspecified actor keywords from configuration
        rule_config = self.get_rule_config('unspecified_actors')
        actor_keywords = rule_config.get('keywords', [])
        
        if not actor_keywords:
            return risks
        
        # Find actor keywords in the requirement text
        found_actors = self.contains_keywords(requirement.text, actor_keywords)
        
        for actor in found_actors:
            # Check if the actor is specified with enough detail
            if self._is_actor_unspecified(requirement.text, actor):
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"Actor '{actor}' is unspecified or ambiguous",
                    evidence=actor,
                    suggestion=f"Specify which '{actor}' (e.g., 'authenticated users', 'system administrators', 'external API')"
                )
                risks.append(risk)
        
        return risks
    
    def _lacks_sufficient_context(self, text: str, action: str) -> bool:
        """
        Check if an action lacks sufficient context or detail.
        
        Args:
            text: The requirement text
            action: The action keyword found
            
        Returns:
            True if the action lacks sufficient context
        """
        # Simple heuristic: check if there are specific details around the action
        # Look for common detail indicators
        detail_indicators = ['when', 'where', 'how', 'within', 'after', 'before', 'if', 'unless', 'during']
        
        # Get text around the action (within 50 characters)
        action_pos = text.lower().find(action.lower())
        if action_pos == -1:
            return True
        
        start = max(0, action_pos - 25)
        end = min(len(text), action_pos + len(action) + 25)
        context_text = text[start:end].lower()
        
        # Check if any detail indicators are present
        has_details = any(indicator in context_text for indicator in detail_indicators)
        
        # Also check for specific numbers, time periods, etc.
        import re
        has_specifics = bool(re.search(r'\d+|seconds?|minutes?|hours?|days?|%', context_text))
        
        return not (has_details or has_specifics)
    
    def _is_actor_unspecified(self, text: str, actor: str) -> bool:
        """
        Check if an actor is unspecified or ambiguous.
        
        Args:
            text: The requirement text
            actor: The actor keyword found
            
        Returns:
            True if the actor is unspecified
        """
        # Common specific actor types
        specific_actors = [
            'authenticated user', 'logged-in user', 'registered user',
            'system administrator', 'admin user', 'superuser',
            'external user', 'guest user', 'anonymous user',
            'api client', 'external system', 'third-party'
        ]
        
        # Check if the actor appears with specific qualifiers
        text_lower = text.lower()
        for specific in specific_actors:
            if specific in text_lower and actor.lower() in specific:
                return False
        
        # If it's just the generic actor word, it's likely unspecified
        return True
    
    def get_detector_name(self) -> str:
        """
        Get human-readable name of this detector.
        
        Returns:
            String name of the detector
        """
        return "Missing Detail Detector"
    
    def get_category(self) -> RiskCategory:
        """
        Get the category of risks this detector finds.
        
        Returns:
            RiskCategory enum value for missing detail
        """
        return RiskCategory.MISSING_DETAIL
