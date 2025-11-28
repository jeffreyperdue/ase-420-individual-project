"""
Unit tests for the AmbiguityDetector class.

This module tests the ambiguity detector to ensure it correctly identifies
vague terms, imprecise quantifiers, and weak requirement language.
"""

import pytest
from src.models.requirement import Requirement
from src.models.risk import RiskCategory, SeverityLevel
from src.detectors.ambiguity_detector import AmbiguityDetector


class TestAmbiguityDetector:
    """Test cases for the AmbiguityDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = AmbiguityDetector()
    
    # Vague terms detection
    def test_detects_vague_terms_should(self):
        """Test that 'should' is detected as a vague term."""
        req = Requirement(id="R001", line_number=1, text="The system should allow users to login")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("should" in r.evidence.lower() for r in risks)
        assert any(r.category == RiskCategory.AMBIGUITY for r in risks)
    
    def test_detects_vague_terms_might(self):
        """Test that 'might' is detected as a vague term."""
        req = Requirement(id="R002", line_number=2, text="The system might support multiple users")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("might" in r.evidence.lower() for r in risks)
    
    def test_detects_vague_terms_could(self):
        """Test that 'could' is detected as a vague term."""
        req = Requirement(id="R003", line_number=3, text="The system could process requests")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("could" in r.evidence.lower() for r in risks)
    
    def test_detects_vague_terms_possibly(self):
        """Test that 'possibly' is detected as a vague term."""
        req = Requirement(id="R004", line_number=4, text="The system possibly will handle errors")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("possibly" in r.evidence.lower() for r in risks)
    
    def test_detects_vague_terms_maybe(self):
        """Test that 'maybe' is detected as a vague term."""
        req = Requirement(id="R005", line_number=5, text="Maybe the system will support this feature")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("maybe" in r.evidence.lower() for r in risks)
    
    def test_detects_multiple_vague_terms(self):
        """Test that multiple vague terms are detected."""
        req = Requirement(id="R006", line_number=6, text="The system should maybe could support this")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 2  # Should detect multiple vague terms
    
    def test_no_risk_when_no_vague_terms(self):
        """Test that no risks are detected when no vague terms are present."""
        req = Requirement(id="R007", line_number=7, text="The system shall allow users to login")
        risks = self.detector.detect_risks(req)
        
        # Should not detect vague terms, but might detect other ambiguity issues
        vague_risks = [r for r in risks if "should" in r.evidence.lower() or 
                      "might" in r.evidence.lower() or "could" in r.evidence.lower()]
        assert len(vague_risks) == 0
    
    # Imprecise quantifiers detection
    def test_detects_imprecise_quantifiers_some(self):
        """Test that 'some' is detected as an imprecise quantifier."""
        req = Requirement(id="R008", line_number=8, text="The system shall handle some users")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("some" in r.evidence.lower() for r in risks)
    
    def test_detects_imprecise_quantifiers_many(self):
        """Test that 'many' is detected as an imprecise quantifier."""
        req = Requirement(id="R009", line_number=9, text="The system shall support many features")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("many" in r.evidence.lower() for r in risks)
    
    def test_detects_imprecise_quantifiers_fast(self):
        """Test that 'fast' is detected as an imprecise quantifier."""
        req = Requirement(id="R010", line_number=10, text="The system shall respond fast")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("fast" in r.evidence.lower() for r in risks)
    
    def test_detects_imprecise_quantifiers_user_friendly(self):
        """Test that 'user-friendly' is detected as an imprecise quantifier."""
        req = Requirement(id="R011", line_number=11, text="The system shall be user-friendly")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("user-friendly" in r.evidence.lower() for r in risks)
    
    # Weak requirement language detection
    def test_detects_weak_language_preferably(self):
        """Test that 'preferably' is detected as weak requirement language."""
        req = Requirement(id="R012", line_number=12, text="The system preferably should support this")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("preferably" in r.evidence.lower() for r in risks)
    
    def test_detects_weak_language_ideally(self):
        """Test that 'ideally' is detected as weak requirement language."""
        req = Requirement(id="R013", line_number=13, text="Ideally the system will support this feature")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("ideally" in r.evidence.lower() for r in risks)
    
    def test_detects_weak_language_when_possible(self):
        """Test that 'when possible' is detected as weak requirement language."""
        req = Requirement(id="R014", line_number=14, text="The system should support this when possible")
        risks = self.detector.detect_risks(req)
        
        # Should detect both 'should' and potentially 'when possible' if in config
        assert len(risks) >= 1
    
    # Edge cases
    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive."""
        req = Requirement(id="R015", line_number=15, text="The system SHOULD allow users to login")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("should" in r.evidence.lower() for r in risks)
    
    def test_detection_in_middle_of_text(self):
        """Test that vague terms are detected in the middle of text."""
        req = Requirement(id="R016", line_number=16, text="The system shall, should it be needed, support users")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("should" in r.evidence.lower() for r in risks)
    
    def test_detection_at_start_of_text(self):
        """Test that vague terms are detected at the start of text."""
        req = Requirement(id="R017", line_number=17, text="Should the system support this feature")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("should" in r.evidence.lower() for r in risks)
    
    def test_detection_at_end_of_text(self):
        """Test that vague terms are detected at the end of text."""
        req = Requirement(id="R018", line_number=18, text="The system shall support this feature should")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) >= 1
        assert any("should" in r.evidence.lower() for r in risks)
    
    # Risk properties
    def test_risks_have_correct_category(self):
        """Test that detected risks have the correct category."""
        req = Requirement(id="R019", line_number=19, text="The system should be fast")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.category == RiskCategory.AMBIGUITY
    
    def test_risks_include_evidence(self):
        """Test that detected risks include evidence."""
        req = Requirement(id="R020", line_number=20, text="The system should allow login")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.evidence
            assert len(risk.evidence) > 0
    
    def test_risks_include_suggestions(self):
        """Test that detected risks include suggestions."""
        req = Requirement(id="R021", line_number=21, text="The system should be fast")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.suggestion is not None
            assert len(risk.suggestion) > 0
    
    def test_risks_have_correct_requirement_id(self):
        """Test that risks have the correct requirement ID."""
        req = Requirement(id="R022", line_number=22, text="The system should support users")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.requirement_id == "R022"
    
    def test_risks_have_correct_line_number(self):
        """Test that risks have the correct line number."""
        req = Requirement(id="R023", line_number=23, text="The system might support this")
        risks = self.detector.detect_risks(req)
        
        assert len(risks) > 0
        for risk in risks:
            assert risk.line_number == 23
    
    def test_detector_name(self):
        """Test that detector returns correct name."""
        assert self.detector.get_detector_name() == "Ambiguity Detector"
    
    def test_detector_category(self):
        """Test that detector returns correct category."""
        assert self.detector.get_category() == RiskCategory.AMBIGUITY
    
    def test_no_false_positives_with_specific_terms(self):
        """Test that specific, clear language doesn't trigger false positives."""
        req = Requirement(
            id="R024", 
            line_number=24, 
            text="The system shall process 1000 requests per second within 2 seconds"
        )
        risks = self.detector.detect_risks(req)
        
        # Should not detect vague terms in this specific requirement
        vague_risks = [r for r in risks if any(term in r.evidence.lower() 
                      for term in ["should", "might", "could", "some", "many", "fast"])]
        assert len(vague_risks) == 0
    
    def test_combination_of_ambiguity_types(self):
        """Test detection of multiple types of ambiguity in one requirement."""
        req = Requirement(
            id="R025", 
            line_number=25, 
            text="The system should preferably handle some users fast"
        )
        risks = self.detector.detect_risks(req)
        
        # Should detect multiple types of ambiguity
        assert len(risks) >= 3  # should, preferably, some, fast

