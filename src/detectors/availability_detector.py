"""
Availability detector module for StressSpec.

BEGINNER NOTES:
- This detector flags requirements that imply always-on service but lack
  availability/uptime specifications.
- It reads triggers and required terms from rules.json.
"""

from typing import List

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class AvailabilityDetector(BaseRiskDetector):
    """Detects missing availability/uptime specifications."""

    def get_detector_name(self) -> str:
        return "Availability Detector"

    def get_category(self) -> RiskCategory:
        return RiskCategory.AVAILABILITY

    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []

        rule = self.get_rule_config("missing_uptime_specs")
        triggers = rule.get("triggers", [])
        required_with = rule.get("required_with", [])

        text_norm = self.normalize_text(requirement.text)
        has_trigger = any(self.normalize_text(t) in text_norm for t in triggers)
        has_required = any(self.normalize_text(r) in text_norm for r in required_with)

        if has_trigger and not has_required:
            risks.append(
                self.create_risk(
                    requirement=requirement,
                    description="Service mention without availability/uptime specification",
                    evidence=requirement.text,
                    severity=self.detector_config.get("severity", "medium"),
                    suggestion="Specify uptime target (e.g., 99.9%), maintenance windows, or SLOs"
                )
            )

        return risks


