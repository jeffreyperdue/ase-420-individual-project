"""
Tests for Chain of Responsibility pattern implementation.

This module tests the Chain of Responsibility pattern used for risk filtering.
"""

import pytest
from src.patterns.chain_of_responsibility import (
    RiskFilter,
    SeverityThresholdFilter,
    DuplicateRiskFilter,
    CategoryFilter,
    NoOpFilter
)
from src.models.risk import Risk, RiskCategory, SeverityLevel


class TestSeverityThresholdFilter:
    """Test cases for severity threshold filter."""
    
    def test_filters_low_severity_risks(self, test_data_factory):
        """Test that low severity risks are filtered out."""
        risks = [
            test_data_factory.create_risk(severity=SeverityLevel.LOW, risk_id="R001-LOW-001"),
            test_data_factory.create_risk(severity=SeverityLevel.MEDIUM, risk_id="R001-MED-001"),
            test_data_factory.create_risk(severity=SeverityLevel.HIGH, risk_id="R001-HIGH-001"),
        ]
        
        filter_chain = SeverityThresholdFilter(SeverityLevel.MEDIUM)
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 2
        assert all(risk.severity.value >= SeverityLevel.MEDIUM.value for risk in filtered)
    
    def test_filters_all_below_threshold(self, test_data_factory):
        """Test that all risks below threshold are filtered."""
        risks = [
            test_data_factory.create_risk(severity=SeverityLevel.LOW, risk_id="R001-LOW-001"),
            test_data_factory.create_risk(severity=SeverityLevel.LOW, risk_id="R001-LOW-002"),
        ]
        
        filter_chain = SeverityThresholdFilter(SeverityLevel.HIGH)
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 0


class TestDuplicateRiskFilter:
    """Test cases for duplicate risk filter."""
    
    def test_removes_duplicates(self, test_data_factory):
        """Test that duplicate risks are removed."""
        risks = [
            test_data_factory.create_risk(requirement_id="R001", risk_id="R001-AMB-001"),
            test_data_factory.create_risk(requirement_id="R001", risk_id="R001-AMB-002"),
            test_data_factory.create_risk(requirement_id="R002", risk_id="R002-AMB-001"),
        ]
        
        # Make second risk a duplicate of first (same requirement, category, evidence)
        risks[1].evidence = risks[0].evidence
        
        filter_chain = DuplicateRiskFilter()
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 2
    
    def test_keeps_unique_risks(self, test_data_factory):
        """Test that unique risks are kept."""
        risks = [
            test_data_factory.create_risk(requirement_id="R001", risk_id="R001-AMB-001"),
            test_data_factory.create_risk(requirement_id="R002", risk_id="R002-SEC-001"),
        ]
        
        filter_chain = DuplicateRiskFilter()
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 2


class TestCategoryFilter:
    """Test cases for category filter."""
    
    def test_includes_only_specified_categories(self, test_data_factory):
        """Test that only included categories are kept."""
        risks = [
            test_data_factory.create_risk(category=RiskCategory.AMBIGUITY, risk_id="R001-AMB-001"),
            test_data_factory.create_risk(category=RiskCategory.SECURITY, risk_id="R001-SEC-001"),
            test_data_factory.create_risk(category=RiskCategory.AMBIGUITY, risk_id="R001-AMB-002"),
        ]
        
        filter_chain = CategoryFilter(included_categories=[RiskCategory.AMBIGUITY])
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 2
        assert all(risk.category == RiskCategory.AMBIGUITY for risk in filtered)
    
    def test_excludes_specified_categories(self, test_data_factory):
        """Test that excluded categories are removed."""
        risks = [
            test_data_factory.create_risk(category=RiskCategory.AMBIGUITY, risk_id="R001-AMB-001"),
            test_data_factory.create_risk(category=RiskCategory.SECURITY, risk_id="R001-SEC-001"),
        ]
        
        filter_chain = CategoryFilter(excluded_categories=[RiskCategory.SECURITY])
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 1
        assert filtered[0].category == RiskCategory.AMBIGUITY


class TestNoOpFilter:
    """Test cases for no-op filter."""
    
    def test_passes_all_risks_through(self, test_data_factory):
        """Test that no-op filter passes all risks unchanged."""
        risks = [
            test_data_factory.create_risk(risk_id="R001-AMB-001"),
            test_data_factory.create_risk(risk_id="R001-SEC-001"),
        ]
        
        filter_chain = NoOpFilter()
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 2
        assert filtered == risks


class TestFilterChain:
    """Test cases for chaining filters."""
    
    def test_chained_filters(self, test_data_factory):
        """Test that filters can be chained together."""
        risks = [
            test_data_factory.create_risk(
                severity=SeverityLevel.LOW, 
                category=RiskCategory.AMBIGUITY,
                risk_id="R001-AMB-001"
            ),
            test_data_factory.create_risk(
                severity=SeverityLevel.HIGH,
                category=RiskCategory.AMBIGUITY,
                risk_id="R001-AMB-002"
            ),
            test_data_factory.create_risk(
                severity=SeverityLevel.HIGH,
                category=RiskCategory.SECURITY,
                risk_id="R001-SEC-001"
            ),
        ]
        
        # Chain: filter by severity (HIGH only), then by category (AMBIGUITY only)
        filter_chain = SeverityThresholdFilter(
            SeverityLevel.HIGH,
            CategoryFilter(included_categories=[RiskCategory.AMBIGUITY])
        )
        
        filtered = filter_chain.filter(risks)
        
        assert len(filtered) == 1
        assert filtered[0].category == RiskCategory.AMBIGUITY
        assert filtered[0].severity == SeverityLevel.HIGH

