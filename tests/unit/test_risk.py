"""
Unit tests for the Risk model.

BEGINNER NOTES:
- This file tests our Risk class to make sure it works correctly
- Unit tests are like "quality control" - they check each piece works as expected
- We test both "happy path" (normal usage) and "error cases" (what happens when things go wrong)
- If all tests pass, we know our code is working correctly
"""

import pytest
from src.models.risk import Risk, RiskCategory, SeverityLevel


class TestRisk:
    """
    Test cases for the Risk class.
    
    BEGINNER NOTES:
    - This class contains all our tests for the Risk model
    - Each method starting with 'test_' is a separate test
    - Tests should be independent - each one can run by itself
    """
    
    def test_risk_creation_with_all_fields(self):
        """Test basic risk creation with all required fields."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Ambiguous requirement",
            requirement_id="R001",
            line_number=1,
            evidence="vague term 'should'",
            suggestion="Use specific, measurable terms"
        )
        
        assert risk.id == "R001-AMB-001"
        assert risk.category == RiskCategory.AMBIGUITY
        assert risk.severity == SeverityLevel.HIGH
        assert risk.description == "Ambiguous requirement"
        assert risk.requirement_id == "R001"
        assert risk.line_number == 1
        assert risk.evidence == "vague term 'should'"
        assert risk.suggestion == "Use specific, measurable terms"
    
    def test_risk_creation_without_suggestion(self):
        """Test risk creation without optional suggestion field."""
        risk = Risk(
            id="R001-SEC-001",
            category=RiskCategory.SECURITY,
            severity=SeverityLevel.CRITICAL,
            description="Security risk detected",
            requirement_id="R001",
            line_number=1,
            evidence="password"
        )
        
        assert risk.id == "R001-SEC-001"
        assert risk.suggestion is None
    
    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Risk ID cannot be empty"):
            Risk(
                id="",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            )
    
    def test_invalid_category_raises_error(self):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError, match="Risk category must be a RiskCategory enum"):
            # Create a risk with invalid category by directly modifying after creation
            # We need to use a different approach since dataclass validation happens in __post_init__
            risk_dict = {
                'id': 'R001-AMB-001',
                'category': 'invalid_category',  # This will fail type checking
                'severity': SeverityLevel.MEDIUM,
                'description': 'Test risk',
                'requirement_id': 'R001',
                'line_number': 1,
                'evidence': 'test'
            }
            # Since Python's type system won't catch this at runtime for dataclasses,
            # we test by trying to create with wrong type
            with pytest.raises((ValueError, TypeError)):
                Risk(**risk_dict)
    
    def test_invalid_severity_raises_error(self):
        """Test that invalid severity raises ValueError."""
        with pytest.raises(ValueError, match="Risk severity must be a SeverityLevel enum"):
            risk_dict = {
                'id': 'R001-AMB-001',
                'category': RiskCategory.AMBIGUITY,
                'severity': 'invalid_severity',  # This will fail type checking
                'description': 'Test risk',
                'requirement_id': 'R001',
                'line_number': 1,
                'evidence': 'test'
            }
            with pytest.raises((ValueError, TypeError)):
                Risk(**risk_dict)
    
    def test_empty_description_raises_error(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Risk description cannot be empty"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            )
    
    def test_whitespace_only_description_raises_error(self):
        """Test that whitespace-only description raises ValueError."""
        with pytest.raises(ValueError, match="Risk description cannot be empty"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="   \n\t  ",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            )
    
    def test_empty_requirement_id_raises_error(self):
        """Test that empty requirement_id raises ValueError."""
        with pytest.raises(ValueError, match="Requirement ID cannot be empty"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="",
                line_number=1,
                evidence="test"
            )
    
    def test_zero_line_number_raises_error(self):
        """Test that zero line number raises ValueError."""
        with pytest.raises(ValueError, match="Line number must be positive"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="R001",
                line_number=0,
                evidence="test"
            )
    
    def test_negative_line_number_raises_error(self):
        """Test that negative line number raises ValueError."""
        with pytest.raises(ValueError, match="Line number must be positive"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="R001",
                line_number=-1,
                evidence="test"
            )
    
    def test_empty_evidence_raises_error(self):
        """Test that empty evidence raises ValueError."""
        with pytest.raises(ValueError, match="Risk evidence cannot be empty"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="R001",
                line_number=1,
                evidence=""
            )
    
    def test_whitespace_only_evidence_raises_error(self):
        """Test that whitespace-only evidence raises ValueError."""
        with pytest.raises(ValueError, match="Risk evidence cannot be empty"):
            Risk(
                id="R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="R001",
                line_number=1,
                evidence="   \n\t  "
            )
    
    def test_str_representation(self):
        """Test string representation of risk."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Ambiguous requirement",
            requirement_id="R001",
            line_number=1,
            evidence="vague term"
        )
        
        expected = "HIGH: Ambiguous requirement in R001"
        assert str(risk) == expected
    
    def test_repr_representation(self):
        """Test detailed string representation."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Ambiguous requirement",
            requirement_id="R001",
            line_number=1,
            evidence="vague term"
        )
        
        repr_str = repr(risk)
        assert "R001-AMB-001" in repr_str
        assert "ambiguity" in repr_str
        assert "HIGH" in repr_str
        assert "R001" in repr_str
        assert "line=1" in repr_str
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Ambiguous requirement",
            requirement_id="R001",
            line_number=1,
            evidence="vague term",
            suggestion="Use specific terms"
        )
        
        risk_dict = risk.to_dict()
        
        assert risk_dict["id"] == "R001-AMB-001"
        assert risk_dict["category"] == "ambiguity"
        assert risk_dict["severity"] == 3
        assert risk_dict["severity_name"] == "HIGH"
        assert risk_dict["description"] == "Ambiguous requirement"
        assert risk_dict["requirement_id"] == "R001"
        assert risk_dict["line_number"] == 1
        assert risk_dict["evidence"] == "vague term"
        assert risk_dict["suggestion"] == "Use specific terms"
    
    def test_to_dict_with_none_suggestion(self):
        """Test to_dict conversion when suggestion is None."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.MEDIUM,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        risk_dict = risk.to_dict()
        assert risk_dict["suggestion"] is None
    
    def test_get_severity_score_returns_correct_value(self):
        """Test that get_severity_score returns the correct numeric value."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        assert risk.get_severity_score() == 3
    
    def test_get_severity_score_all_levels(self):
        """Test get_severity_score for all severity levels."""
        levels = [
            (SeverityLevel.LOW, 1),
            (SeverityLevel.MEDIUM, 2),
            (SeverityLevel.HIGH, 3),
            (SeverityLevel.CRITICAL, 4),
            (SeverityLevel.BLOCKER, 5)
        ]
        
        for severity, expected_score in levels:
            risk = Risk(
                id=f"R001-AMB-001",
                category=RiskCategory.AMBIGUITY,
                severity=severity,
                description="Test risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            )
            assert risk.get_severity_score() == expected_score
    
    def test_is_critical_returns_true_for_high(self):
        """Test that is_critical returns True for HIGH severity."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        assert risk.is_critical() is True
    
    def test_is_critical_returns_true_for_critical(self):
        """Test that is_critical returns True for CRITICAL severity."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.CRITICAL,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        assert risk.is_critical() is True
    
    def test_is_critical_returns_true_for_blocker(self):
        """Test that is_critical returns True for BLOCKER severity."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.BLOCKER,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        assert risk.is_critical() is True
    
    def test_is_critical_returns_false_for_low(self):
        """Test that is_critical returns False for LOW severity."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.LOW,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        assert risk.is_critical() is False
    
    def test_is_critical_returns_false_for_medium(self):
        """Test that is_critical returns False for MEDIUM severity."""
        risk = Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.MEDIUM,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        assert risk.is_critical() is False
    
    def test_severity_level_enum_values(self):
        """Test that all SeverityLevel enum values are correct."""
        assert SeverityLevel.LOW.value == 1
        assert SeverityLevel.MEDIUM.value == 2
        assert SeverityLevel.HIGH.value == 3
        assert SeverityLevel.CRITICAL.value == 4
        assert SeverityLevel.BLOCKER.value == 5
    
    def test_risk_category_enum_values(self):
        """Test that all RiskCategory enum values are correct."""
        assert RiskCategory.AMBIGUITY.value == "ambiguity"
        assert RiskCategory.MISSING_DETAIL.value == "missing_detail"
        assert RiskCategory.SECURITY.value == "security"
        assert RiskCategory.CONFLICT.value == "conflict"
        assert RiskCategory.PERFORMANCE.value == "performance"
        assert RiskCategory.AVAILABILITY.value == "availability"
        assert RiskCategory.TRACEABILITY.value == "traceability"
        assert RiskCategory.SCOPE.value == "scope"
    
    def test_risk_with_all_categories(self):
        """Test creating risks with all different categories."""
        categories = [
            RiskCategory.AMBIGUITY,
            RiskCategory.MISSING_DETAIL,
            RiskCategory.SECURITY,
            RiskCategory.CONFLICT,
            RiskCategory.PERFORMANCE,
            RiskCategory.AVAILABILITY,
            RiskCategory.TRACEABILITY,
            RiskCategory.SCOPE
        ]
        
        for category in categories:
            risk = Risk(
                id=f"R001-{category.value.upper()}-001",
                category=category,
                severity=SeverityLevel.MEDIUM,
                description="Test risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            )
            assert risk.category == category

