"""
Scope detector module for StressSpec.

Identifies potential scope creep and undefined system boundaries using
keyword/pattern-based heuristics tuned to minimize false positives.
"""

from typing import List

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class ScopeDetector(BaseRiskDetector):
    """Detects scope-related risks in requirements."""

    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []

        risks.extend(self._detect_out_of_scope_terms(requirement))
        risks.extend(self._detect_undefined_system_boundary(requirement))
        risks.extend(self._detect_third_party_dependency_without_spec(requirement))

        return risks

    def _detect_out_of_scope_terms(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []
        rule = self.get_rule_config("out_of_scope_terms")
        keywords = rule.get("keywords", [])

        for term in self.contains_keywords(requirement.text, keywords):
            # Escalate explicit boundary violations to high
            escalate_terms = ["any api", "all platforms", "every browser", "all providers", "support everything"]
            severity = "high" if term.lower() in escalate_terms else None
            risks.append(
                self.create_risk(
                    requirement,
                    description=f"Potential scope creep term '{term}' detected",
                    evidence=term,
                    severity=severity,
                    suggestion=(
                        "Constrain scope with explicit platforms, versions, providers, or acceptance criteria"
                    ),
                )
            )

        return risks

    def _detect_undefined_system_boundary(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []
        rule = self.get_rule_config("undefined_system_boundary")
        keywords = rule.get("keywords", [])

        for term in self.contains_keywords(requirement.text, keywords):
            risks.append(
                self.create_risk(
                    requirement,
                    description=f"External dependency '{term}' without defined boundary/constraints",
                    evidence=term,
                    suggestion=(
                        "Specify interfaces, limits, SLAs, supported providers, or versions"
                    ),
                )
            )

        return risks

    def _detect_third_party_dependency_without_spec(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []
        rule = self.get_rule_config("third_party_dependency_without_spec")
        triggers = rule.get("triggers", [])
        required_with = rule.get("required_with", [])

        text_norm = self.normalize_text(requirement.text)
        has_trigger = any(self.normalize_text(t) in text_norm for t in triggers)
        has_required = any(self.normalize_text(rw) in text_norm for rw in required_with)

        if has_trigger and not has_required:
            risks.append(
                self.create_risk(
                    requirement,
                    description=(
                        "Third-party integration mentioned without specifying provider, version, or protocol"
                    ),
                    evidence=requirement.text,
                    severity="high",
                    suggestion=(
                        "Add constraints (specific provider, supported versions, protocol/contract, SLA)"
                    ),
                )
            )

        return risks

    def get_detector_name(self) -> str:
        return "Scope Detector"

    def get_category(self) -> RiskCategory:
        return RiskCategory.SCOPE


