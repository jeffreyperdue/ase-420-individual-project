"""
Traceability detector module for StressSpec.

Detects missing traceability signals in requirements: requirement IDs, acceptance
criteria, and test references. Designed to be permissive and user-friendly:
if any one signal is present, remaining gaps are reported with downgraded
severity and constructive guidance.
"""

from typing import List

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory
from .base import BaseRiskDetector


class TraceabilityDetector(BaseRiskDetector):
    """Detects missing traceability elements in requirements."""

    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        risks: List[Risk] = []

        # Determine which signals are present
        has_id = self._has_requirement_id(requirement)
        has_ac = self._has_acceptance_criteria(requirement)
        has_test_ref = self._has_test_reference(requirement)

        # If no signals at all, raise a single high-severity risk (default severity from config)
        if not (has_id or has_ac or has_test_ref):
            risks.append(
                self.create_risk(
                    requirement,
                    description=(
                        "No traceability signals found (ID, acceptance criteria, or test reference)"
                    ),
                    evidence=requirement.text,
                )
            )
            return risks

        # If some present, flag missing ones with downgraded severity to medium
        downgrade_severity = "medium"

        if not has_id:
            risks.append(
                self.create_risk(
                    requirement,
                    description="Missing requirement ID (e.g., R001, REQ-123, ABC-123)",
                    evidence=requirement.text,
                    severity=downgrade_severity,
                    suggestion=(
                        "Add a stable identifier (R###, REQ-#, US-#, FR-#, or ABC-123)"
                    ),
                )
            )

        if not has_ac:
            risks.append(
                self.create_risk(
                    requirement,
                    description=(
                        "Missing acceptance criteria (e.g., Given/When/Then or 'Acceptance Criteria')"
                    ),
                    evidence=requirement.text,
                    severity=downgrade_severity,
                    suggestion=(
                        "Add AC with Given/When/Then or a short checklist under the requirement"
                    ),
                )
            )

        if not has_test_ref:
            risks.append(
                self.create_risk(
                    requirement,
                    description=(
                        "Missing test reference (e.g., TC-123, 'Test Case', 'validated by QA')"
                    ),
                    evidence=requirement.text,
                    severity=downgrade_severity,
                    suggestion=(
                        "Reference a test artifact (TC-###) or note how it will be verified"
                    ),
                )
            )

        return risks

    def _has_requirement_id(self, requirement: Requirement) -> bool:
        # Use conservative regexes to avoid false positives from single letters like 'R'
        import re
        text = requirement.text
        regexes = [
            r"\bR\d{3,}\b",           # R### or longer
            r"\bREQ-\d+\b",          # REQ-123
            r"\bUS-\d+\b",           # US-12
            r"\bFR-\d+\b",           # FR-001
            r"\b[A-Z]{2,}-\d+\b",    # ABC-123 style
        ]
        return any(re.search(rx, text) for rx in regexes)

    def _has_acceptance_criteria(self, requirement: Requirement) -> bool:
        rule = self.get_rule_config("missing_acceptance_criteria")
        keywords = rule.get("keywords", [])
        if self.contains_keywords(requirement.text, keywords):
            return True
        # Simple bullet/list heuristic: presence of common bullet markers with action words
        list_markers = ["- ", "* ", "1. ", "2. "]
        action_words = ["given", "when", "then", "acceptance", "criteria", "ac:"]
        text_norm = self.normalize_text(requirement.text)
        if any(m in requirement.text for m in list_markers) and any(a in text_norm for a in action_words):
            return True
        return False

    def _has_test_reference(self, requirement: Requirement) -> bool:
        rule = self.get_rule_config("missing_test_reference")
        keywords = rule.get("keywords", [])
        return len(self.contains_keywords(requirement.text, keywords)) > 0

    def get_detector_name(self) -> str:
        return "Traceability Detector"

    def get_category(self) -> RiskCategory:
        return RiskCategory.TRACEABILITY


