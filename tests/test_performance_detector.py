import pytest

from src.models.requirement import Requirement
from src.detectors.performance_detector import PerformanceDetector


class TestPerformanceDetector:
    def setup_method(self):
        self.detector = PerformanceDetector()

    def test_flags_missing_specs(self):
        req = Requirement("R001", 1, "The system shall handle 1000 users concurrently")
        risks = self.detector.detect_risks(req)
        assert len(risks) >= 1
        assert any("Performance" in r.description or "performance" in r.description.lower() for r in risks)

    def test_no_flag_when_specs_present(self):
        req = Requirement("R002", 2, "The system shall handle 1000 users with response time under 2 seconds")
        risks = self.detector.detect_risks(req)
        assert len(risks) == 0


