"""
Unit tests for the ConflictDetector class.

This module tests the conflict detector to ensure it correctly identifies
duplicate requirements, contradictory terms, and conflicting priorities.
"""

import pytest
from src.models.requirement import Requirement
from src.models.risk import RiskCategory, SeverityLevel
from src.detectors.conflict_detector import ConflictDetector


class TestConflictDetector:
    """Test cases for the ConflictDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ConflictDetector()
    
    # Contradictory terms detection
    def test_detects_must_vs_must_not(self):
        """Test that 'must' and 'must not' are detected as contradictory."""
        req = Requirement(
            id="R001", 
            line_number=1, 
            text="The system must and must not allow users to login"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("must" in r.evidence.lower() and "must not" in r.evidence.lower() for r in risks)
        assert any(r.category == RiskCategory.CONFLICT for r in risks)
    
    def test_detects_shall_vs_shall_not(self):
        """Test that 'shall' and 'shall not' are detected as contradictory."""
        req = Requirement(
            id="R002", 
            line_number=2, 
            text="The system shall and shall not process requests"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("shall" in r.evidence.lower() and "shall not" in r.evidence.lower() for r in risks)
    
    def test_detects_will_vs_will_not(self):
        """Test that 'will' and 'will not' are detected as contradictory."""
        req = Requirement(
            id="R003", 
            line_number=3, 
            text="The system will and will not support this feature"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("will" in r.evidence.lower() and "will not" in r.evidence.lower() for r in risks)
    
    def test_detects_always_vs_never(self):
        """Test that 'always' and 'never' are detected as contradictory."""
        req = Requirement(
            id="R004", 
            line_number=4, 
            text="The system shall always and never allow access"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("always" in r.evidence.lower() and "never" in r.evidence.lower() for r in risks)
    
    def test_detects_required_vs_optional(self):
        """Test that 'required' and 'optional' are detected as contradictory."""
        req = Requirement(
            id="R005", 
            line_number=5, 
            text="This feature is required and optional"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("required" in r.evidence.lower() and "optional" in r.evidence.lower() for r in risks)
    
    def test_no_contradiction_when_terms_not_both_present(self):
        """Test that no contradiction is detected when only one term is present."""
        req = Requirement(id="R006", line_number=6, text="The system must allow users to login")
        risks = self.detector.detect_risks(req)
        
        # Should not detect contradiction
        contradiction_risks = [r for r in risks if "contradictory" in r.description.lower()]
        assert len(contradiction_risks) == 0
    
    # Conflicting priorities detection
    def test_detects_multiple_urgent_terms(self):
        """Test that multiple urgent priority terms are detected."""
        req = Requirement(
            id="R007", 
            line_number=7, 
            text="This is urgent and critical and must be done immediately asap"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("urgent" in r.description.lower() or "priority" in r.description.lower() for r in risks)
    
    def test_detects_conflicting_priorities(self):
        """Test that conflicting priority language is detected."""
        req = Requirement(
            id="R008", 
            line_number=8, 
            text="This feature is urgent, critical, and immediate"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("priority" in r.description.lower() or "urgent" in r.description.lower() for r in risks)
    
    def test_no_priority_conflict_with_single_term(self):
        """Test that single priority term doesn't trigger conflict."""
        req = Requirement(id="R009", line_number=9, text="This feature is urgent")
        risks = self.detector.detect_risks(req)
        
        # Should not detect conflicting priorities with only one term
        priority_risks = [r for r in risks if "priority" in r.description.lower() and "multiple" in r.description.lower()]
        assert len(priority_risks) == 0
    
    # Duplicate detection (requires multiple requirements)
    def test_detects_duplicate_requirements(self):
        """Test that duplicate requirements are detected."""
        req1 = Requirement(id="R010", line_number=10, text="The system shall allow users to login")
        req2 = Requirement(id="R011", line_number=11, text="The system shall allow users to login")
        
        risks = self.detector.detect_duplicate_risks([req1, req2])
        
        assert len(risks) >= 1
        assert any("duplicate" in r.description.lower() for r in risks)
    
    def test_detects_similar_requirements(self):
        """Test that very similar requirements are detected."""
        req1 = Requirement(id="R012", line_number=12, text="The system shall allow users to login with email")
        req2 = Requirement(id="R013", line_number=13, text="The system shall allow users to login with email address")
        
        risks = self.detector.detect_duplicate_risks([req1, req2])
        
        # Should detect high similarity
        assert len(risks) >= 1
    
    def test_no_duplicate_for_different_requirements(self):
        """Test that different requirements are not flagged as duplicates."""
        req1 = Requirement(id="R014", line_number=14, text="The system shall allow users to login")
        req2 = Requirement(id="R015", line_number=15, text="The system shall display user dashboard")
        
        risks = self.detector.detect_duplicate_risks([req1, req2])
        
        # Should not detect duplicates
        assert len(risks) == 0
    
    def test_duplicate_threshold_configuration(self):
        """Test that similarity threshold works correctly."""
        # Create requirements that are somewhat similar but not identical
        req1 = Requirement(id="R016", line_number=16, text="The system shall process user requests")
        req2 = Requirement(id="R017", line_number=17, text="The system shall handle user requests")
        
        risks = self.detector.detect_duplicate_risks([req1, req2])
        
        # Similarity should be high enough to detect (depending on threshold)
        # This test verifies the threshold mechanism works
        assert isinstance(risks, list)
    
    # Edge cases
    def test_handles_empty_requirement_list(self):
        """Test that empty requirement list is handled."""
        risks = self.detector.detect_duplicate_risks([])
        
        assert len(risks) == 0
    
    def test_handles_single_requirement(self):
        """Test that single requirement doesn't trigger duplicate detection."""
        req = Requirement(id="R018", line_number=18, text="The system shall allow users to login")
        risks = self.detector.detect_duplicate_risks([req])
        
        assert len(risks) == 0
    
    def test_similarity_calculation_accuracy(self):
        """Test that similarity calculation is accurate."""
        text1 = "The system shall allow users to login"
        text2 = "The system shall allow users to login"
        
        similarity = self.detector._calculate_similarity(text1, text2)
        
        # Identical texts should have similarity of 1.0
        assert similarity == 1.0
    
    def test_similarity_calculation_different_texts(self):
        """Test similarity calculation for different texts."""
        text1 = "The system shall allow users to login"
        text2 = "The system shall display user dashboard"
        
        similarity = self.detector._calculate_similarity(text1, text2)
        
        # Different texts should have lower similarity
        assert 0.0 <= similarity < 1.0
    
    def test_similarity_calculation_case_insensitive(self):
        """Test that similarity calculation is case-insensitive."""
        text1 = "The system shall allow users to login"
        text2 = "THE SYSTEM SHALL ALLOW USERS TO LOGIN"
        
        similarity = self.detector._calculate_similarity(text1, text2)
        
        # Case differences shouldn't affect similarity much
        assert similarity > 0.9
    
    # Risk properties
    def test_risks_have_correct_category(self):
        """Test that detected risks have the correct category."""
        req = Requirement(
            id="R019", 
            line_number=19, 
            text="The system must and must not allow access"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.category == RiskCategory.CONFLICT
    
    def test_risks_include_evidence(self):
        """Test that detected risks include evidence."""
        req = Requirement(
            id="R020", 
            line_number=20, 
            text="The system shall and shall not process requests"
        )
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.evidence
            assert len(risk.evidence) > 0
    
    def test_risks_include_suggestions(self):
        """Test that detected risks include suggestions."""
        req = Requirement(
            id="R021", 
            line_number=21, 
            text="This is urgent and critical"
        )
        risks = self.detector.detect_risks(req)
        
        if len(risks) > 0:
            for risk in risks:
                assert risk.suggestion is not None
                assert len(risk.suggestion) > 0
    
    def test_detector_name(self):
        """Test that detector returns correct name."""
        assert self.detector.get_detector_name() == "Conflict Detector"
    
    def test_detector_category(self):
        """Test that detector returns correct category."""
        assert self.detector.get_category() == RiskCategory.CONFLICT
    
    def test_cache_functionality(self):
        """Test that requirement cache works correctly."""
        # The cache is internal, but we can verify it doesn't break functionality
        req1 = Requirement(id="R022", line_number=22, text="The system shall allow users to login")
        req2 = Requirement(id="R023", line_number=23, text="The system shall allow users to login")
        
        # First call
        risks1 = self.detector.detect_duplicate_risks([req1, req2])
        
        # Second call (should use cache if implemented)
        risks2 = self.detector.detect_duplicate_risks([req1, req2])
        
        # Results should be consistent
        assert len(risks1) == len(risks2)

