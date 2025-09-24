"""
Performance detector module for StressSpec.

BEGINNER NOTES:
- This detector looks for features that imply performance needs (like load, concurrent users)
  but do not mention measurable performance criteria (like response time, throughput).
- It uses configuration from rules.json, so you can change triggers/required terms without code changes.
"""

from typing import List

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class PerformanceDetector(BaseRiskDetector):
    """
    Detects missing performance specifications.

    BEGINNER NOTES:
    - We consider it a risk when a requirement mentions operations/load but lacks
      explicit performance specs in the same text.
    """

    def get_detector_name(self) -> str:
        return "Performance Detector"

    def get_category(self) -> RiskCategory:
        return RiskCategory.PERFORMANCE

    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []

        rule = self.get_rule_config("missing_performance_specs")
        triggers = rule.get("triggers", [])
        required_with = rule.get("required_with", [])

        text_norm = self.normalize_text(requirement.text)
        has_trigger = any(self.normalize_text(t) in text_norm for t in triggers)
        has_required = any(self.normalize_text(r) in text_norm for r in required_with)

        if has_trigger and not has_required:
            risks.append(
                self.create_risk(
                    requirement=requirement,
                    description="Performance-related feature without measurable performance specification",
                    evidence=requirement.text,
                    severity=self.detector_config.get("severity", "medium"),
                    suggestion="Specify response time, throughput, or latency targets"
                )
            )

        return risks


