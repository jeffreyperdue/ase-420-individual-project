"""
Security detector module for StressSpec.

This module detects missing security requirements.
Follows the Strategy pattern and inherits from BaseRiskDetector.

BEGINNER NOTES:
- This detector looks for security gaps in requirements
- It's like a "security auditor" that checks for missing protections
- It flags when security features are mentioned without proper safeguards
- It helps ensure requirements include necessary security measures
"""

from typing import List, Set
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class SecurityDetector(BaseRiskDetector):
    """
    Detects missing security requirements.
    
    BEGINNER NOTES:
    - This detector is like a "security auditor" for requirements
    - It looks for security features that lack proper protection requirements
    - Examples: "login" without "authentication", "admin" without "authorization"
    - It helps ensure security is built into requirements from the start
    
    This detector finds:
    - Missing authentication requirements for user access features
    - Missing authorization requirements for administrative actions
    - Missing data protection requirements for data storage
    - Missing secure communication requirements for data transmission
    """
    
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """
        Analyze a requirement for missing security requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of Risk objects representing security issues found
        """
        risks = []
        
        # Check for missing authentication
        auth_risks = self._detect_missing_authentication(requirement)
        risks.extend(auth_risks)
        
        # Check for missing authorization
        authz_risks = self._detect_missing_authorization(requirement)
        risks.extend(authz_risks)
        
        # Check for missing data protection
        data_risks = self._detect_missing_data_protection(requirement)
        risks.extend(data_risks)
        
        # Check for insecure communication
        comm_risks = self._detect_insecure_communication(requirement)
        risks.extend(comm_risks)
        
        return risks
    
    def _detect_missing_authentication(self, requirement: Requirement) -> List[Risk]:
        """
        Detect user access features without authentication requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for missing authentication found
        """
        risks = []
        
        # Get authentication detection rules from configuration
        rule_config = self.get_rule_config('missing_authentication')
        triggers = rule_config.get('triggers', [])
        required_with = rule_config.get('required_with', [])
        
        if not triggers:
            return risks
        
        # Check if requirement mentions authentication triggers
        found_triggers = self.contains_keywords(requirement.text, triggers)
        
        for trigger in found_triggers:
            # Check if authentication requirements are also mentioned
            has_auth_requirements = self.contains_keywords(requirement.text, required_with)
            
            if not has_auth_requirements:
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"User access feature '{trigger}' mentioned without authentication requirements",
                    evidence=trigger,
                    suggestion="Add authentication requirements (e.g., 'users must authenticate before accessing')"
                )
                risks.append(risk)
        
        return risks
    
    def _detect_missing_authorization(self, requirement: Requirement) -> List[Risk]:
        """
        Detect administrative actions without authorization requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for missing authorization found
        """
        risks = []
        
        # Get authorization detection rules from configuration
        rule_config = self.get_rule_config('missing_authorization')
        triggers = rule_config.get('triggers', [])
        required_with = rule_config.get('required_with', [])
        
        if not triggers:
            return risks
        
        # Check if requirement mentions authorization triggers
        found_triggers = self.contains_keywords(requirement.text, triggers)
        
        for trigger in found_triggers:
            # Check if authorization requirements are also mentioned
            has_authz_requirements = self.contains_keywords(requirement.text, required_with)
            
            if not has_authz_requirements:
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"Administrative action '{trigger}' mentioned without authorization requirements",
                    evidence=trigger,
                    suggestion="Add authorization requirements (e.g., 'only authorized administrators can perform this action')"
                )
                risks.append(risk)
        
        return risks
    
    def _detect_missing_data_protection(self, requirement: Requirement) -> List[Risk]:
        """
        Detect data storage without protection requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for missing data protection found
        """
        risks = []
        
        # Get data protection detection rules from configuration
        rule_config = self.get_rule_config('missing_data_protection')
        triggers = rule_config.get('triggers', [])
        required_with = rule_config.get('required_with', [])
        
        if not triggers:
            return risks
        
        # Check if requirement mentions data storage triggers
        found_triggers = self.contains_keywords(requirement.text, triggers)
        
        for trigger in found_triggers:
            # Check if data protection requirements are also mentioned
            has_protection_requirements = self.contains_keywords(requirement.text, required_with)
            
            if not has_protection_requirements:
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"Data storage '{trigger}' mentioned without protection requirements",
                    evidence=trigger,
                    suggestion="Add data protection requirements (e.g., 'data must be encrypted', 'personal information must be protected')"
                )
                risks.append(risk)
        
        return risks
    
    def _detect_insecure_communication(self, requirement: Requirement) -> List[Risk]:
        """
        Detect data transmission without security requirements.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of risks for insecure communication found
        """
        risks = []
        
        # Get insecure communication detection rules from configuration
        rule_config = self.get_rule_config('insecure_communication')
        triggers = rule_config.get('triggers', [])
        required_with = rule_config.get('required_with', [])
        
        if not triggers:
            return risks
        
        # Check if requirement mentions communication triggers
        found_triggers = self.contains_keywords(requirement.text, triggers)
        
        for trigger in found_triggers:
            # Check if secure communication requirements are also mentioned
            has_secure_comm_requirements = self.contains_keywords(requirement.text, required_with)
            
            if not has_secure_comm_requirements:
                risk = self.create_risk(
                    requirement=requirement,
                    description=f"Data transmission '{trigger}' mentioned without security requirements",
                    evidence=trigger,
                    suggestion="Add secure communication requirements (e.g., 'communication must use HTTPS', 'data must be encrypted in transit')"
                )
                risks.append(risk)
        
        return risks
    
    def get_detector_name(self) -> str:
        """
        Get human-readable name of this detector.
        
        Returns:
            String name of the detector
        """
        return "Security Detector"
    
    def get_category(self) -> RiskCategory:
        """
        Get the category of risks this detector finds.
        
        Returns:
            RiskCategory enum value for security
        """
        return RiskCategory.SECURITY
