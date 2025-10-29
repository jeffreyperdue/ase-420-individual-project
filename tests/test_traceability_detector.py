import pytest

from src.models.requirement import Requirement
from src.detectors.traceability_detector import TraceabilityDetector


class TestTraceabilityDetector:
    def setup_method(self):
        self.detector = TraceabilityDetector()

    def test_no_traceability_signals_flags_high(self):
        req = Requirement(id="R001", line_number=1, text="The system shall display a dashboard")
        risks = self.detector.detect_risks(req)
        assert len(risks) == 1
        assert "No traceability signals" in risks[0].description

    def test_has_id_but_missing_others_downgrades(self):
        req = Requirement(id="R002", line_number=2, text="REQ-123 The system shall display a dashboard")
        risks = self.detector.detect_risks(req)
        # Missing AC and test reference should produce 2 downgraded findings
        assert len(risks) >= 1
        assert any("Missing acceptance criteria" in r.description for r in risks)

    def test_has_ac_marker(self):
        req = Requirement(id="R003", line_number=3, text="Acceptance Criteria: When user logs in, Then dashboard loads")
        risks = self.detector.detect_risks(req)
        # AC present, so only other gaps may be flagged
        assert all("No traceability signals" not in r.description for r in risks)

    def test_has_test_reference(self):
        req = Requirement(id="R004", line_number=4, text="Validated by QA, TC-101 covers login flow")
        risks = self.detector.detect_risks(req)
        assert all("No traceability signals" not in r.description for r in risks)


