"""
Unit tests for the SecurityDetector class.

This module tests the security detector to ensure it correctly identifies
missing authentication, authorization, data protection, and secure communication requirements.
"""

import pytest
from src.models.requirement import Requirement
from src.models.risk import RiskCategory, SeverityLevel
from src.detectors.security_detector import SecurityDetector


class TestSecurityDetector:
    """Test cases for the SecurityDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = SecurityDetector()
    
    # Missing authentication tests
    def test_detects_missing_authentication_for_login(self):
        """Test that login without authentication requirements is detected."""
        req = Requirement(id="R001", line_number=1, text="The system shall allow users to login")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("login" in r.evidence.lower() or "authentication" in r.description.lower() for r in risks)
        assert any(r.category == RiskCategory.SECURITY for r in risks)
    
    def test_detects_missing_authentication_for_access(self):
        """Test that access without authentication requirements is detected."""
        req = Requirement(id="R002", line_number=2, text="The system shall provide user access to dashboard")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("access" in r.evidence.lower() for r in risks)
    
    def test_detects_missing_authentication_for_user_account(self):
        """Test that user account without authentication requirements is detected."""
        req = Requirement(id="R003", line_number=3, text="The system shall manage user account")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("user account" in r.evidence.lower() or "account" in r.evidence.lower() for r in risks)
    
    def test_no_risk_when_authentication_specified(self):
        """Test that no risk is detected when authentication is specified."""
        req = Requirement(
            id="R004", 
            line_number=4, 
            text="The system shall allow users to login with authentication using password"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing authentication since it's mentioned
        auth_risks = [r for r in risks if "authentication" in r.description.lower() and "missing" in r.description.lower()]
        assert len(auth_risks) == 0
    
    def test_no_risk_when_auth_keywords_present(self):
        """Test that no risk is detected when auth keywords are present."""
        req = Requirement(
            id="R005", 
            line_number=5, 
            text="Users must authenticate before accessing the dashboard"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing authentication
        auth_risks = [r for r in risks if "authentication" in r.description.lower() and "missing" in r.description.lower()]
        assert len(auth_risks) == 0
    
    # Missing authorization tests
    def test_detects_missing_authorization_for_admin(self):
        """Test that admin actions without authorization requirements are detected."""
        req = Requirement(id="R006", line_number=6, text="Admin users shall delete records")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("admin" in r.evidence.lower() or "authorization" in r.description.lower() for r in risks)
    
    def test_detects_missing_authorization_for_delete(self):
        """Test that delete operations without authorization are detected."""
        req = Requirement(id="R007", line_number=7, text="The system shall allow users to delete data")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("delete" in r.evidence.lower() for r in risks)
    
    def test_detects_missing_authorization_for_modify(self):
        """Test that modify operations without authorization are detected."""
        req = Requirement(id="R008", line_number=8, text="The system shall allow users to modify settings")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("modify" in r.evidence.lower() for r in risks)
    
    def test_no_risk_when_authorization_specified(self):
        """Test that no risk is detected when authorization is specified."""
        req = Requirement(
            id="R009", 
            line_number=9, 
            text="Only authorized administrators with proper permissions can delete records"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing authorization
        authz_risks = [r for r in risks if "authorization" in r.description.lower() and "missing" in r.description.lower()]
        assert len(authz_risks) == 0
    
    # Missing data protection tests
    def test_detects_missing_encryption_for_data_storage(self):
        """Test that data storage without encryption requirements is detected."""
        req = Requirement(id="R010", line_number=10, text="The system shall store user data in database")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("store" in r.evidence.lower() or "database" in r.evidence.lower() or "data" in r.evidence.lower() for r in risks)
    
    def test_detects_missing_encryption_for_sensitive_data(self):
        """Test that sensitive data storage without protection is detected."""
        req = Requirement(id="R011", line_number=11, text="The system shall save personal information")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("personal information" in r.evidence.lower() or "sensitive" in r.evidence.lower() for r in risks)
    
    def test_no_risk_when_encryption_specified(self):
        """Test that no risk is detected when encryption is specified."""
        req = Requirement(
            id="R012", 
            line_number=12, 
            text="The system shall store user data encrypted in secure database"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing data protection
        data_risks = [r for r in risks if "data" in r.evidence.lower() and "protection" in r.description.lower() and "missing" in r.description.lower()]
        assert len(data_risks) == 0
    
    # Missing secure communication tests
    def test_detects_missing_https_for_data_transmission(self):
        """Test that data transmission without HTTPS is detected."""
        req = Requirement(id="R013", line_number=13, text="The system shall transfer data over network")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("transfer" in r.evidence.lower() or "network" in r.evidence.lower() for r in risks)
    
    def test_detects_missing_ssl_for_communication(self):
        """Test that communication without SSL/TLS is detected."""
        req = Requirement(id="R014", line_number=14, text="The system shall send data via API")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("api" in r.evidence.lower() or "send" in r.evidence.lower() for r in risks)
    
    def test_no_risk_when_secure_communication_specified(self):
        """Test that no risk is detected when secure communication is specified."""
        req = Requirement(
            id="R015", 
            line_number=15, 
            text="The system shall transfer data using HTTPS with SSL encryption"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing secure communication
        comm_risks = [r for r in risks if "communication" in r.description.lower() and "missing" in r.description.lower()]
        assert len(comm_risks) == 0
    
    # Password-related risks
    def test_detects_password_storage_without_encryption(self):
        """Test that password storage without encryption is detected."""
        req = Requirement(id="R016", line_number=16, text="The system shall store user passwords")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        # Should detect both data storage and potentially password-specific risks
        assert any("store" in r.evidence.lower() or "password" in r.evidence.lower() for r in risks)
    
    def test_detects_password_transmission_without_https(self):
        """Test that password transmission without HTTPS is detected."""
        req = Requirement(id="R017", line_number=17, text="The system shall send passwords over network")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("send" in r.evidence.lower() or "network" in r.evidence.lower() for r in risks)
    
    # Edge cases
    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive."""
        req = Requirement(id="R018", line_number=18, text="The system shall allow ADMIN users to DELETE records")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("admin" in r.evidence.lower() or "delete" in r.evidence.lower() for r in risks)
    
    def test_multiple_security_risks_in_one_requirement(self):
        """Test that multiple security risks are detected in one requirement."""
        req = Requirement(
            id="R019", 
            line_number=19, 
            text="Admin users shall login and delete sensitive data stored in database"
        )
        risks = self.detector.detect_risks(req)
        
        # Should detect multiple security issues
        assert len(risks) >= 2
    
    def test_no_false_positives(self):
        """Test that secure requirements don't trigger false positives."""
        req = Requirement(
            id="R020", 
            line_number=20, 
            text="Users must authenticate with password before accessing dashboard. Only authorized administrators with proper permissions can delete records. All data is encrypted and stored securely. Communication uses HTTPS with SSL."
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing security requirements
        missing_risks = [r for r in risks if "missing" in r.description.lower()]
        assert len(missing_risks) == 0
    
    # Risk properties
    def test_risks_have_correct_category(self):
        """Test that detected risks have the correct category."""
        req = Requirement(id="R021", line_number=21, text="The system shall allow users to login")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.category == RiskCategory.SECURITY
    
    def test_risks_include_evidence(self):
        """Test that detected risks include evidence."""
        req = Requirement(id="R022", line_number=22, text="Admin users shall delete records")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.evidence
            assert len(risk.evidence) > 0
    
    def test_risks_include_suggestions(self):
        """Test that detected risks include suggestions."""
        req = Requirement(id="R023", line_number=23, text="The system shall store user data")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.suggestion is not None
            assert len(risk.suggestion) > 0
    
    def test_detector_name(self):
        """Test that detector returns correct name."""
        assert self.detector.get_detector_name() == "Security Detector"
    
    def test_detector_category(self):
        """Test that detector returns correct category."""
        assert self.detector.get_category() == RiskCategory.SECURITY

