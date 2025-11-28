"""
Unit tests for the analyzer module.

This module tests the analyze_requirements function to ensure it correctly
orchestrates risk detection across multiple detectors and requirements.
"""

import pytest
from unittest.mock import Mock, patch
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.analyzer import analyze_requirements
from src.utils.detector_error_handler import DetectorErrorHandler
from src.patterns.chain_of_responsibility import RiskFilter, NoOpFilter


class TestAnalyzeRequirements:
    """Test cases for the analyze_requirements function."""
    
    def test_analyze_single_requirement_single_detector(self):
        """Test analyzing a single requirement with a single detector."""
        req = Requirement(id="R001", line_number=1, text="The system should allow users to login")
        
        # Create a mock detector
        mock_detector = Mock()
        mock_risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.MEDIUM,
            description="Vague term found",
            requirement_id="R001",
            line_number=1,
            evidence="should"
        )
        mock_detector.detect_risks.return_value = [mock_risk]
        
        risks_by_req = analyze_requirements([req], [mock_detector])
        
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 1
        assert risks_by_req["R001"][0].category == RiskCategory.AMBIGUITY
    
    def test_analyze_multiple_requirements_multiple_detectors(self):
        """Test analyzing multiple requirements with multiple detectors."""
        req1 = Requirement(id="R001", line_number=1, text="The system should allow login")
        req2 = Requirement(id="R002", line_number=2, text="Admin users shall delete records")
        
        # Create mock detectors
        mock_detector1 = Mock()
        mock_detector1.detect_risks.return_value = [
            Risk(id="R001-AMB-001", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.MEDIUM,
                 description="Vague term", requirement_id="R001", line_number=1, evidence="should")
        ]
        
        mock_detector2 = Mock()
        mock_detector2.detect_risks.return_value = [
            Risk(id="R002-SEC-001", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                 description="Missing authorization", requirement_id="R002", line_number=2, evidence="admin")
        ]
        
        risks_by_req = analyze_requirements([req1, req2], [mock_detector1, mock_detector2])
        
        assert "R001" in risks_by_req
        assert "R002" in risks_by_req
        assert len(risks_by_req["R001"]) == 1
        assert len(risks_by_req["R002"]) == 1
        assert risks_by_req["R001"][0].category == RiskCategory.AMBIGUITY
        assert risks_by_req["R002"][0].category == RiskCategory.SECURITY
    
    def test_returns_risks_grouped_by_requirement_id(self):
        """Test that risks are grouped by requirement ID."""
        req1 = Requirement(id="R001", line_number=1, text="Test requirement 1")
        req2 = Requirement(id="R002", line_number=2, text="Test requirement 2")
        
        mock_detector = Mock()
        mock_detector.detect_risks.side_effect = [
            [Risk(id="R001-RISK-1", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.MEDIUM,
                  description="Risk 1", requirement_id="R001", line_number=1, evidence="test")],
            [Risk(id="R002-RISK-1", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                  description="Risk 2", requirement_id="R002", line_number=2, evidence="test")]
        ]
        
        risks_by_req = analyze_requirements([req1, req2], [mock_detector])
        
        assert isinstance(risks_by_req, dict)
        assert "R001" in risks_by_req
        assert "R002" in risks_by_req
        assert len(risks_by_req["R001"]) == 1
        assert len(risks_by_req["R002"]) == 1
    
    def test_empty_requirements_returns_empty_dict(self):
        """Test that empty requirements list returns empty dictionary."""
        risks_by_req = analyze_requirements([], [])
        
        assert isinstance(risks_by_req, dict)
        assert len(risks_by_req) == 0
    
    def test_no_detectors_returns_empty_risks(self):
        """Test that no detectors returns empty risks for all requirements."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        risks_by_req = analyze_requirements([req], [])
        
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 0
    
    def test_detector_error_handled_gracefully(self):
        """Test that detector errors are handled gracefully."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        # Create a detector that raises an error
        failing_detector = Mock()
        failing_detector.detect_risks.side_effect = ValueError("Detector error")
        
        # Should not raise, but handle the error
        risks_by_req = analyze_requirements([req], [failing_detector])
        
        # Error handler should be called and return empty list or handle error
        assert "R001" in risks_by_req
        # The error handler should prevent the error from propagating
    
    def test_multiple_detector_errors_handled(self):
        """Test that multiple detector errors are handled."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        # Create multiple failing detectors
        failing_detector1 = Mock()
        failing_detector1.detect_risks.side_effect = ValueError("Error 1")
        
        failing_detector2 = Mock()
        failing_detector2.detect_risks.side_effect = RuntimeError("Error 2")
        
        # Should handle all errors
        risks_by_req = analyze_requirements([req], [failing_detector1, failing_detector2])
        
        assert "R001" in risks_by_req
    
    def test_error_handler_called_on_exception(self):
        """Test that error handler is called when detector raises exception."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        failing_detector = Mock()
        failing_detector.detect_risks.side_effect = ValueError("Test error")
        
        # Create a mock error handler
        mock_error_handler = Mock(spec=DetectorErrorHandler)
        mock_error_handler.handle_detector_error.return_value = []
        
        risks_by_req = analyze_requirements([req], [failing_detector], error_handler=mock_error_handler)
        
        # Verify error handler was called
        mock_error_handler.handle_detector_error.assert_called()
    
    def test_analysis_continues_after_detector_error(self):
        """Test that analysis continues after a detector error."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        # Create one failing and one working detector
        failing_detector = Mock()
        failing_detector.detect_risks.side_effect = ValueError("Error")
        
        working_detector = Mock()
        working_detector.detect_risks.return_value = [
            Risk(id="R001-RISK-1", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.MEDIUM,
                 description="Risk", requirement_id="R001", line_number=1, evidence="test")
        ]
        
        risks_by_req = analyze_requirements([req], [failing_detector, working_detector])
        
        # Should still get risks from working detector
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) >= 1
    
    def test_risk_filter_applied_when_provided(self):
        """Test that risk filter is applied when provided."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = [
            Risk(id="R001-RISK-1", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.LOW,
                 description="Low risk", requirement_id="R001", line_number=1, evidence="test"),
            Risk(id="R001-RISK-2", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                 description="High risk", requirement_id="R001", line_number=1, evidence="test")
        ]
        
        # Create a filter that only keeps HIGH severity risks
        from src.patterns.chain_of_responsibility import SeverityThresholdFilter
        risk_filter = SeverityThresholdFilter(SeverityLevel.HIGH)
        
        risks_by_req = analyze_requirements([req], [mock_detector], risk_filter=risk_filter)
        
        # Should only have HIGH severity risk
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 1
        assert risks_by_req["R001"][0].severity == SeverityLevel.HIGH
    
    def test_risk_filter_chains_work_correctly(self):
        """Test that risk filter chains work correctly."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = [
            Risk(id="R001-RISK-1", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.MEDIUM,
                 description="Risk", requirement_id="R001", line_number=1, evidence="test"),
            Risk(id="R001-RISK-2", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                 description="Risk", requirement_id="R001", line_number=1, evidence="test")
        ]
        
        # Create a filter chain: severity threshold then category filter
        from src.patterns.chain_of_responsibility import SeverityThresholdFilter, CategoryFilter
        risk_filter = SeverityThresholdFilter(SeverityLevel.MEDIUM, 
                                             CategoryFilter(included_categories=[RiskCategory.SECURITY]))
        
        risks_by_req = analyze_requirements([req], [mock_detector], risk_filter=risk_filter)
        
        # Should only have SECURITY risk (filtered by category)
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 1
        assert risks_by_req["R001"][0].category == RiskCategory.SECURITY
    
    def test_no_filter_returns_all_risks(self):
        """Test that no filter returns all risks."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = [
            Risk(id="R001-RISK-1", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.LOW,
                 description="Risk 1", requirement_id="R001", line_number=1, evidence="test"),
            Risk(id="R001-RISK-2", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                 description="Risk 2", requirement_id="R001", line_number=1, evidence="test")
        ]
        
        risks_by_req = analyze_requirements([req], [mock_detector])
        
        # Should have all risks
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 2
    
    def test_requirement_with_no_risks(self):
        """Test that requirements with no risks get empty list."""
        req = Requirement(id="R001", line_number=1, text="The system shall allow users to login")
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = []
        
        risks_by_req = analyze_requirements([req], [mock_detector])
        
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 0
    
    def test_requirement_with_multiple_risks(self):
        """Test that requirements with multiple risks are collected correctly."""
        req = Requirement(id="R001", line_number=1, text="The system should allow users to login")
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = [
            Risk(id="R001-RISK-1", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.MEDIUM,
                 description="Risk 1", requirement_id="R001", line_number=1, evidence="should"),
            Risk(id="R001-RISK-2", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                 description="Risk 2", requirement_id="R001", line_number=1, evidence="login")
        ]
        
        risks_by_req = analyze_requirements([req], [mock_detector])
        
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 2
    
    def test_all_requirements_get_entry_in_dict(self):
        """Test that all requirements get an entry in the dictionary."""
        req1 = Requirement(id="R001", line_number=1, text="Requirement 1")
        req2 = Requirement(id="R002", line_number=2, text="Requirement 2")
        req3 = Requirement(id="R003", line_number=3, text="Requirement 3")
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = []
        
        risks_by_req = analyze_requirements([req1, req2, req3], [mock_detector])
        
        assert "R001" in risks_by_req
        assert "R002" in risks_by_req
        assert "R003" in risks_by_req
        assert len(risks_by_req) == 3
    
    def test_multiple_detectors_same_requirement(self):
        """Test that multiple detectors can detect risks in the same requirement."""
        req = Requirement(id="R001", line_number=1, text="The system should allow admin users to login")
        
        detector1 = Mock()
        detector1.detect_risks.return_value = [
            Risk(id="R001-AMB-001", category=RiskCategory.AMBIGUITY, severity=SeverityLevel.MEDIUM,
                 description="Vague term", requirement_id="R001", line_number=1, evidence="should")
        ]
        
        detector2 = Mock()
        detector2.detect_risks.return_value = [
            Risk(id="R001-SEC-001", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                 description="Missing authorization", requirement_id="R001", line_number=1, evidence="admin")
        ]
        
        risks_by_req = analyze_requirements([req], [detector1, detector2])
        
        assert "R001" in risks_by_req
        assert len(risks_by_req["R001"]) == 2
        assert any(r.category == RiskCategory.AMBIGUITY for r in risks_by_req["R001"])
        assert any(r.category == RiskCategory.SECURITY for r in risks_by_req["R001"])

