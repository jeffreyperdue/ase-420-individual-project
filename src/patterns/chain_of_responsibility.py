"""
Chain of Responsibility pattern implementation for risk filtering in StressSpec.

This module implements the Chain of Responsibility pattern to allow flexible
risk filtering pipelines that can be composed and extended.

BEGINNER NOTES:
- This follows the Chain of Responsibility pattern from design patterns course materials
- It allows multiple filters to be chained together
- Each filter can process risks and pass them to the next filter
- It makes it easy to add new filters without modifying existing code
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.risk import Risk, SeverityLevel


class RiskFilter(ABC):
    """
    Base class for risk filtering chain.
    
    BEGINNER NOTES:
    - This is the base class for all risk filters
    - It implements the Chain of Responsibility pattern
    - Each filter processes risks and passes them to the next filter
    - It's like a "filter pipeline" where each filter does its job and passes to the next
    
    This class provides:
    - Chain structure (next filter in chain)
    - Template method for filtering workflow
    - Abstract method for filter-specific logic
    """
    
    def __init__(self, next_filter: Optional['RiskFilter'] = None):
        """
        Initialize the filter with optional next filter in chain.
        
        Args:
            next_filter: Next filter in the chain (None if this is the last filter)
        """
        self.next_filter = next_filter
    
    def filter(self, risks: List[Risk]) -> List[Risk]:
        """
        Filter risks and pass to next filter in chain.
        
        BEGINNER NOTES:
        - This is the template method that defines the filtering workflow
        - It applies this filter's logic, then passes to next filter
        - It's like a "relay race" where each filter does its part
        
        Args:
            risks: List of risks to filter
            
        Returns:
            Filtered list of risks
        """
        filtered = self._apply_filter(risks)
        if self.next_filter:
            return self.next_filter.filter(filtered)
        return filtered
    
    @abstractmethod
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        """
        Apply this filter's logic.
        
        Args:
            risks: List of risks to filter
            
        Returns:
            Filtered list of risks
        """
        pass


class SeverityThresholdFilter(RiskFilter):
    """
    Filter out risks below severity threshold.
    
    BEGINNER NOTES:
    - This filter removes risks that are below a certain severity level
    - It's like a "quality gate" that only lets through important risks
    - Useful for focusing on high-priority issues
    """
    
    def __init__(self, min_severity: SeverityLevel, next_filter: Optional[RiskFilter] = None):
        """
        Initialize severity threshold filter.
        
        Args:
            min_severity: Minimum severity level to keep (risks below this are filtered out)
            next_filter: Next filter in chain
        """
        super().__init__(next_filter)
        self.min_severity = min_severity
    
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        """Filter out risks below severity threshold."""
        return [risk for risk in risks if risk.severity.value >= self.min_severity.value]


class DuplicateRiskFilter(RiskFilter):
    """
    Filter out duplicate risks.
    
    BEGINNER NOTES:
    - This filter removes duplicate risks based on requirement ID, category, and evidence
    - It's like a "deduplication filter" that keeps only unique risks
    - Useful for cleaning up duplicate detections
    """
    
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        """Filter out duplicate risks."""
        seen = set()
        unique = []
        
        for risk in risks:
            # Create a key from requirement ID, category, and evidence
            key = (risk.requirement_id, risk.category, risk.evidence)
            if key not in seen:
                seen.add(key)
                unique.append(risk)
        
        return unique


class CategoryFilter(RiskFilter):
    """
    Filter risks by category (include or exclude specific categories).
    
    BEGINNER NOTES:
    - This filter can include or exclude specific risk categories
    - It's like a "category selector" that focuses on certain types of risks
    - Useful for analyzing specific risk types
    """
    
    def __init__(self, 
                 included_categories: Optional[List] = None,
                 excluded_categories: Optional[List] = None,
                 next_filter: Optional[RiskFilter] = None):
        """
        Initialize category filter.
        
        Args:
            included_categories: List of categories to include (None = include all)
            excluded_categories: List of categories to exclude (None = exclude none)
            next_filter: Next filter in chain
        """
        super().__init__(next_filter)
        self.included_categories = set(included_categories) if included_categories else None
        self.excluded_categories = set(excluded_categories) if excluded_categories else None
    
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        """Filter risks by category."""
        filtered = []
        
        for risk in risks:
            # Check inclusion list
            if self.included_categories and risk.category not in self.included_categories:
                continue
            
            # Check exclusion list
            if self.excluded_categories and risk.category in self.excluded_categories:
                continue
            
            filtered.append(risk)
        
        return filtered


class NoOpFilter(RiskFilter):
    """
    No-operation filter that passes all risks through unchanged.
    
    BEGINNER NOTES:
    - This filter does nothing - it's a "pass-through" filter
    - Useful as a placeholder or default filter
    - Can be used when no filtering is needed
    """
    
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        """Pass all risks through unchanged."""
        return risks

