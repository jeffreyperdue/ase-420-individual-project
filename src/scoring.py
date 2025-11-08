"""
Risk scoring module for StressSpec.

This module provides functionality to calculate risk scores for requirements
and identify the top riskiest requirements based on aggregated severity scores.

BEGINNER NOTES:
- This module handles the "scoring" concern - calculating how risky each requirement is
- It uses the risk severity values (1-5) to compute total and average scores
- It ranks requirements to find the most risky ones
- This follows the Single Responsibility Principle - it only handles scoring logic
"""

from typing import Dict, List, Optional
from src.models.requirement import Requirement
from src.models.risk import Risk


def calculate_risk_scores(
    requirements: List[Requirement],
    risks_by_requirement: Dict[str, List[Risk]]
) -> Dict[str, Dict]:
    """
    Calculate risk scores for each requirement.
    
    BEGINNER NOTES:
    - This function takes all requirements and their associated risks
    - It computes a total score (sum of all severity values) for each requirement
    - It also calculates average severity and risk count
    - Requirements with no risks get a score of 0
    
    Args:
        requirements: List of all requirements
        risks_by_requirement: Dictionary mapping requirement_id to list of risks
        
    Returns:
        Dictionary mapping requirement_id to score data:
        {
            'requirement_id': {
                'total_score': int,
                'avg_severity': float,
                'risk_count': int,
                'risks': List[Risk]
            }
        }
    """
    scores: Dict[str, Dict] = {}
    
    for requirement in requirements:
        req_id = requirement.id
        risks = risks_by_requirement.get(req_id, [])
        
        if not risks:
            # No risks - score is 0
            scores[req_id] = {
                'total_score': 0,
                'avg_severity': 0.0,
                'risk_count': 0,
                'risks': []
            }
        else:
            # Calculate total score (sum of all severity values)
            total_score = sum(risk.get_severity_score() for risk in risks)
            
            # Calculate average severity
            avg_severity = total_score / len(risks)
            
            # Store score data
            scores[req_id] = {
                'total_score': total_score,
                'avg_severity': round(avg_severity, 2),
                'risk_count': len(risks),
                'risks': risks
            }
    
    return scores


def get_top_riskiest(
    requirements: List[Requirement],
    risk_scores: Dict[str, Dict],
    top_n: int = 5
) -> List[Dict]:
    """
    Get the top N riskiest requirements.
    
    BEGINNER NOTES:
    - This function sorts requirements by their risk scores
    - It returns the top N (default 5) most risky requirements
    - Ranking is by total score (descending), then risk count, then requirement ID
    - If there are fewer than N requirements, it returns all available
    
    Args:
        requirements: List of all requirements
        risk_scores: Dictionary of risk scores (from calculate_risk_scores)
        top_n: Number of top riskiest requirements to return (default: 5)
        
    Returns:
        List of dictionaries containing top riskiest requirements:
        [
            {
                'requirement_id': str,
                'total_score': int,
                'avg_severity': float,
                'risk_count': int,
                'requirement': Requirement,
                'risks': List[Risk]
            },
            ...
        ]
    """
    # Create requirement lookup for easy access
    req_lookup = {req.id: req for req in requirements}
    
    # Build list of scored requirements with full data
    scored_requirements = []
    
    for req_id, score_data in risk_scores.items():
        requirement = req_lookup.get(req_id)
        if requirement:
            scored_requirements.append({
                'requirement_id': req_id,
                'total_score': score_data['total_score'],
                'avg_severity': score_data['avg_severity'],
                'risk_count': score_data['risk_count'],
                'requirement': requirement,
                'risks': score_data['risks']
            })
    
    # Sort by:
    # 1. Total score (descending - higher is riskier)
    # 2. Risk count (descending - more risks is riskier)
    # 3. Requirement ID (ascending - for consistent ordering in ties)
    scored_requirements.sort(
        key=lambda x: (-x['total_score'], -x['risk_count'], x['requirement_id'])
    )
    
    # Return top N (or all if fewer than N)
    return scored_requirements[:top_n]

