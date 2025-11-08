"""
Unit tests for the scoring module.

Tests risk score calculation and top riskiest requirements identification.
"""

import pytest
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.scoring import calculate_risk_scores, get_top_riskiest


class TestCalculateRiskScores:
    """Test calculate_risk_scores function."""
    
    def test_calculate_scores_with_risks(self):
        """Test score calculation for requirements with risks."""
        req1 = Requirement(id="R001", line_number=1, text="Test requirement 1")
        req2 = Requirement(id="R002", line_number=2, text="Test requirement 2")
        requirements = [req1, req2]
        
        risk1 = Risk(
            id="R001-RISK-1",
            category=RiskCategory.SECURITY,
            severity=SeverityLevel.HIGH,
            description="Security risk",
            requirement_id="R001",
            line_number=1,
            evidence="password"
        )
        risk2 = Risk(
            id="R001-RISK-2",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.MEDIUM,
            description="Ambiguity risk",
            requirement_id="R001",
            line_number=1,
            evidence="should"
        )
        risk3 = Risk(
            id="R002-RISK-1",
            category=RiskCategory.SECURITY,
            severity=SeverityLevel.CRITICAL,
            description="Critical security risk",
            requirement_id="R002",
            line_number=2,
            evidence="admin"
        )
        
        risks_by_requirement = {
            "R001": [risk1, risk2],
            "R002": [risk3]
        }
        
        scores = calculate_risk_scores(requirements, risks_by_requirement)
        
        assert "R001" in scores
        assert "R002" in scores
        assert scores["R001"]["total_score"] == 5  # HIGH(3) + MEDIUM(2) = 5
        assert scores["R001"]["avg_severity"] == 2.5
        assert scores["R001"]["risk_count"] == 2
        assert scores["R002"]["total_score"] == 4  # CRITICAL(4)
        assert scores["R002"]["avg_severity"] == 4.0
        assert scores["R002"]["risk_count"] == 1
    
    def test_calculate_scores_no_risks(self):
        """Test score calculation for requirements with no risks."""
        req1 = Requirement(id="R001", line_number=1, text="Test requirement 1")
        requirements = [req1]
        risks_by_requirement = {"R001": []}
        
        scores = calculate_risk_scores(requirements, risks_by_requirement)
        
        assert "R001" in scores
        assert scores["R001"]["total_score"] == 0
        assert scores["R001"]["avg_severity"] == 0.0
        assert scores["R001"]["risk_count"] == 0
        assert scores["R001"]["risks"] == []
    
    def test_calculate_scores_missing_requirement(self):
        """Test score calculation when requirement has no entry in risks dict."""
        req1 = Requirement(id="R001", line_number=1, text="Test requirement 1")
        requirements = [req1]
        risks_by_requirement = {}  # No entry for R001
        
        scores = calculate_risk_scores(requirements, risks_by_requirement)
        
        assert "R001" in scores
        assert scores["R001"]["total_score"] == 0
        assert scores["R001"]["risk_count"] == 0
    
    def test_calculate_scores_all_severity_levels(self):
        """Test score calculation with all severity levels."""
        req1 = Requirement(id="R001", line_number=1, text="Test requirement")
        requirements = [req1]
        
        risks = [
            Risk(
                id="R001-RISK-1",
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.LOW,
                description="Low risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            ),
            Risk(
                id="R001-RISK-2",
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.MEDIUM,
                description="Medium risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            ),
            Risk(
                id="R001-RISK-3",
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.HIGH,
                description="High risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            ),
            Risk(
                id="R001-RISK-4",
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.CRITICAL,
                description="Critical risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            ),
            Risk(
                id="R001-RISK-5",
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.BLOCKER,
                description="Blocker risk",
                requirement_id="R001",
                line_number=1,
                evidence="test"
            ),
        ]
        
        risks_by_requirement = {"R001": risks}
        scores = calculate_risk_scores(requirements, risks_by_requirement)
        
        # Total: 1 + 2 + 3 + 4 + 5 = 15
        assert scores["R001"]["total_score"] == 15
        assert scores["R001"]["avg_severity"] == 3.0
        assert scores["R001"]["risk_count"] == 5


class TestGetTopRiskiest:
    """Test get_top_riskiest function."""
    
    def test_get_top_5_riskiest(self):
        """Test getting top 5 riskiest requirements."""
        requirements = [
            Requirement(id="R001", line_number=1, text="Req 1"),
            Requirement(id="R002", line_number=2, text="Req 2"),
            Requirement(id="R003", line_number=3, text="Req 3"),
            Requirement(id="R004", line_number=4, text="Req 4"),
            Requirement(id="R005", line_number=5, text="Req 5"),
            Requirement(id="R006", line_number=6, text="Req 6"),
        ]
        
        # Create risks with different scores
        risks_by_requirement = {
            "R001": [
                Risk(id="R001-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.CRITICAL,
                     description="Critical", requirement_id="R001", line_number=1, evidence="test"),
                Risk(id="R001-R2", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                     description="High", requirement_id="R001", line_number=1, evidence="test"),
            ],  # Score: 7
            "R002": [
                Risk(id="R002-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.BLOCKER,
                     description="Blocker", requirement_id="R002", line_number=2, evidence="test"),
            ],  # Score: 5
            "R003": [
                Risk(id="R003-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                     description="High", requirement_id="R003", line_number=3, evidence="test"),
                Risk(id="R003-R2", category=RiskCategory.SECURITY, severity=SeverityLevel.MEDIUM,
                     description="Medium", requirement_id="R003", line_number=3, evidence="test"),
            ],  # Score: 5
            "R004": [
                Risk(id="R004-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.MEDIUM,
                     description="Medium", requirement_id="R004", line_number=4, evidence="test"),
            ],  # Score: 2
            "R005": [],  # Score: 0
            "R006": [
                Risk(id="R006-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.LOW,
                     description="Low", requirement_id="R006", line_number=6, evidence="test"),
            ],  # Score: 1
        }
        
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
        
        assert len(top_5) == 5
        # Should be sorted by score descending: R001(7), then R003(5, 2 risks), R002(5, 1 risk), R004(2), R006(1)
        # When tied on score, more risks = riskier, so R003 comes before R002
        assert top_5[0]["requirement_id"] == "R001"
        assert top_5[0]["total_score"] == 7
        assert top_5[1]["requirement_id"] == "R003"  # Tied with R002 on score (5) but has more risks (2 vs 1)
        assert top_5[1]["total_score"] == 5
        assert top_5[2]["requirement_id"] == "R002"  # Same score as R003 but fewer risks
        assert top_5[2]["total_score"] == 5
        assert top_5[3]["requirement_id"] == "R004"
        assert top_5[4]["requirement_id"] == "R006"
    
    def test_get_top_less_than_5_requirements(self):
        """Test getting top 5 when there are fewer than 5 requirements."""
        requirements = [
            Requirement(id="R001", line_number=1, text="Req 1"),
            Requirement(id="R002", line_number=2, text="Req 2"),
        ]
        
        risks_by_requirement = {
            "R001": [
                Risk(id="R001-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                     description="High", requirement_id="R001", line_number=1, evidence="test"),
            ],
            "R002": [
                Risk(id="R002-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.MEDIUM,
                     description="Medium", requirement_id="R002", line_number=2, evidence="test"),
            ],
        }
        
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
        
        # Should return all 2 requirements
        assert len(top_5) == 2
        assert top_5[0]["requirement_id"] == "R001"
        assert top_5[1]["requirement_id"] == "R002"
    
    def test_get_top_riskiest_tie_breaking(self):
        """Test tie-breaking when scores are equal."""
        requirements = [
            Requirement(id="R001", line_number=1, text="Req 1"),
            Requirement(id="R002", line_number=2, text="Req 2"),
            Requirement(id="R003", line_number=3, text="Req 3"),
        ]
        
        # All have same total score (5), but different risk counts
        risks_by_requirement = {
            "R001": [
                Risk(id="R001-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                     description="High", requirement_id="R001", line_number=1, evidence="test"),
                Risk(id="R001-R2", category=RiskCategory.SECURITY, severity=SeverityLevel.MEDIUM,
                     description="Medium", requirement_id="R001", line_number=1, evidence="test"),
            ],  # Score: 5, Count: 2
            "R002": [
                Risk(id="R002-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                     description="High", requirement_id="R002", line_number=2, evidence="test"),
                Risk(id="R002-R2", category=RiskCategory.SECURITY, severity=SeverityLevel.MEDIUM,
                     description="Medium", requirement_id="R002", line_number=2, evidence="test"),
            ],  # Score: 5, Count: 2
            "R003": [
                Risk(id="R003-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.CRITICAL,
                     description="Critical", requirement_id="R003", line_number=3, evidence="test"),
                Risk(id="R003-R2", category=RiskCategory.SECURITY, severity=SeverityLevel.LOW,
                     description="Low", requirement_id="R003", line_number=3, evidence="test"),
            ],  # Score: 5, Count: 2
        }
        
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
        
        # All tied, should be sorted by requirement ID (ascending)
        assert len(top_5) == 3
        assert top_5[0]["requirement_id"] == "R001"
        assert top_5[1]["requirement_id"] == "R002"
        assert top_5[2]["requirement_id"] == "R003"
    
    def test_get_top_riskiest_no_risks(self):
        """Test getting top 5 when no requirements have risks."""
        requirements = [
            Requirement(id="R001", line_number=1, text="Req 1"),
            Requirement(id="R002", line_number=2, text="Req 2"),
        ]
        
        risks_by_requirement = {
            "R001": [],
            "R002": [],
        }
        
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
        
        # Should return all requirements with score 0
        assert len(top_5) == 2
        assert top_5[0]["total_score"] == 0
        assert top_5[1]["total_score"] == 0
    
    def test_get_top_riskiest_custom_n(self):
        """Test getting top N with custom N value."""
        requirements = [
            Requirement(id="R001", line_number=1, text="Req 1"),
            Requirement(id="R002", line_number=2, text="Req 2"),
            Requirement(id="R003", line_number=3, text="Req 3"),
        ]
        
        risks_by_requirement = {
            "R001": [
                Risk(id="R001-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.CRITICAL,
                     description="Critical", requirement_id="R001", line_number=1, evidence="test"),
            ],
            "R002": [
                Risk(id="R002-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.HIGH,
                     description="High", requirement_id="R002", line_number=2, evidence="test"),
            ],
            "R003": [
                Risk(id="R003-R1", category=RiskCategory.SECURITY, severity=SeverityLevel.MEDIUM,
                     description="Medium", requirement_id="R003", line_number=3, evidence="test"),
            ],
        }
        
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_2 = get_top_riskiest(requirements, risk_scores, top_n=2)
        
        assert len(top_2) == 2
        assert top_2[0]["requirement_id"] == "R001"
        assert top_2[1]["requirement_id"] == "R002"
    
    def test_get_top_riskiest_structure(self):
        """Test that top riskiest returns correct data structure."""
        requirements = [
            Requirement(id="R001", line_number=1, text="Req 1"),
        ]
        
        risk = Risk(
            id="R001-R1",
            category=RiskCategory.SECURITY,
            severity=SeverityLevel.HIGH,
            description="High risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        risks_by_requirement = {"R001": [risk]}
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
        
        assert len(top_5) == 1
        item = top_5[0]
        assert "requirement_id" in item
        assert "total_score" in item
        assert "avg_severity" in item
        assert "risk_count" in item
        assert "requirement" in item
        assert "risks" in item
        assert item["requirement_id"] == "R001"
        assert item["total_score"] == 3
        assert item["risk_count"] == 1
        assert len(item["risks"]) == 1
        assert isinstance(item["requirement"], Requirement)

