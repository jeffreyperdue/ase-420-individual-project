"""
Unit tests for the MissingDetailDetector class.

This module tests the missing detail detector to ensure it correctly identifies
incomplete phrases, missing specifications, and unspecified actors.
"""

import pytest
from src.models.requirement import Requirement
from src.models.risk import RiskCategory, SeverityLevel
from src.detectors.missing_detail_detector import MissingDetailDetector


class TestMissingDetailDetector:
    """Test cases for the MissingDetailDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = MissingDetailDetector()
    
    # Incomplete phrases detection
    def test_detects_incomplete_phrases(self):
        """Test that incomplete phrases are detected."""
        req = Requirement(id="R001", line_number=1, text="The system shall")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("incomplete" in r.description.lower() for r in risks)
        assert any(r.category == RiskCategory.MISSING_DETAIL for r in risks)
    
    def test_detects_requirements_ending_with_handle(self):
        """Test that requirements ending with 'handle' without details are detected."""
        req = Requirement(id="R002", line_number=2, text="The system shall handle")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("handle" in r.evidence.lower() or "incomplete" in r.description.lower() for r in risks)
    
    def test_detects_requirements_ending_with_support(self):
        """Test that requirements ending with 'support' without details are detected."""
        req = Requirement(id="R003", line_number=3, text="The system will support")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("support" in r.evidence.lower() or "incomplete" in r.description.lower() for r in risks)
    
    def test_detects_requirements_ending_with_process(self):
        """Test that requirements ending with 'process' without details are detected."""
        req = Requirement(id="R004", line_number=4, text="The system must process")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("process" in r.evidence.lower() or "incomplete" in r.description.lower() for r in risks)
    
    def test_no_risk_when_details_present(self):
        """Test that no risk is detected when details are present."""
        req = Requirement(
            id="R005", 
            line_number=5, 
            text="The system shall allow users to login with email and password"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect incomplete phrases when details are present
        incomplete_risks = [r for r in risks if "incomplete" in r.description.lower()]
        assert len(incomplete_risks) == 0
    
    # Missing specifications detection
    def test_detects_missing_action_specifications(self):
        """Test that actions without specifications are detected."""
        req = Requirement(id="R006", line_number=6, text="The system shall handle users")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("handle" in r.evidence.lower() for r in risks)
    
    def test_detects_unspecified_actors(self):
        """Test that unspecified actors are detected."""
        req = Requirement(id="R007", line_number=7, text="The system shall allow user to access")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("user" in r.evidence.lower() or "actor" in r.description.lower() for r in risks)
    
    def test_detects_vague_actions(self):
        """Test that vague actions without specifics are detected."""
        req = Requirement(id="R008", line_number=8, text="The system shall manage data")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("manage" in r.evidence.lower() for r in risks)
    
    def test_no_risk_when_specifications_present(self):
        """Test that no risk is detected when specifications are present."""
        req = Requirement(
            id="R009", 
            line_number=9, 
            text="The system shall handle 1000 concurrent users within 2 seconds"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect missing specifications when details are present
        missing_spec_risks = [r for r in risks if "lacks sufficient detail" in r.description.lower()]
        assert len(missing_spec_risks) == 0
    
    # Edge cases
    def test_detection_at_sentence_end(self):
        """Test that incomplete phrases at sentence end are detected."""
        req = Requirement(id="R010", line_number=10, text="The system shall.")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
    
    def test_multiple_missing_details(self):
        """Test that multiple missing details are detected."""
        req = Requirement(id="R011", line_number=11, text="The system shall handle user")
        risks = self.detector.detect_risks(req)
        
        # Should detect multiple issues (incomplete phrase, missing spec, unspecified actor)
        assert len(risks) >= 1
    
    def test_specific_actors_not_flagged(self):
        """Test that specific actors are not flagged as unspecified."""
        req = Requirement(
            id="R012", 
            line_number=12, 
            text="Authenticated users shall be able to access the dashboard"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not flag "authenticated users" as unspecified
        actor_risks = [r for r in risks if "unspecified" in r.description.lower() and "actor" in r.description.lower()]
        assert len(actor_risks) == 0
    
    def test_actions_with_context_not_flagged(self):
        """Test that actions with sufficient context are not flagged."""
        req = Requirement(
            id="R013", 
            line_number=13, 
            text="The system shall process requests when they arrive within 2 seconds"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not flag actions with context
        missing_spec_risks = [r for r in risks if "lacks sufficient detail" in r.description.lower()]
        assert len(missing_spec_risks) == 0
    
    # Risk properties
    def test_risks_have_correct_category(self):
        """Test that detected risks have the correct category."""
        req = Requirement(id="R014", line_number=14, text="The system shall")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.category == RiskCategory.MISSING_DETAIL
    
    def test_risks_include_evidence(self):
        """Test that detected risks include evidence."""
        req = Requirement(id="R015", line_number=15, text="The system shall handle")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.evidence
            assert len(risk.evidence) > 0
    
    def test_risks_include_suggestions(self):
        """Test that detected risks include suggestions."""
        req = Requirement(id="R016", line_number=16, text="The system shall process")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.suggestion is not None
            assert len(risk.suggestion) > 0
    
    def test_detector_name(self):
        """Test that detector returns correct name."""
        assert self.detector.get_detector_name() == "Missing Detail Detector"
    
    def test_detector_category(self):
        """Test that detector returns correct category."""
        assert self.detector.get_category() == RiskCategory.MISSING_DETAIL
    
    def test_complete_requirement_no_risks(self):
        """Test that complete requirements don't trigger false positives."""
        req = Requirement(
            id="R017", 
            line_number=17, 
            text="Authenticated users shall be able to login to the system using email and password within 5 seconds"
        )
        risks = self.detector.detect_risks(req)
        
        # Complete requirement should not trigger missing detail risks
        # (may have other risks from other detectors, but not missing detail)
        missing_detail_risks = [r for r in risks if r.category == RiskCategory.MISSING_DETAIL]
        assert len(missing_detail_risks) == 0

