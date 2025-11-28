import pytest

from src.models.requirement import Requirement
from src.detectors.availability_detector import AvailabilityDetector


class TestAvailabilityDetector:
    def setup_method(self):
        self.detector = AvailabilityDetector()

    def test_flags_missing_specs(self):
        req = Requirement("R010", 10, "The service shall be available for all users")
        risks = self.detector.detect_risks(req)
        assert len(risks) >= 1
        assert any("availability" in r.description.lower() or "uptime" in r.description.lower() for r in risks)

    def test_no_flag_when_specs_present(self):
        req = Requirement("R011", 11, "The platform shall achieve 99.9% uptime")
        risks = self.detector.detect_risks(req)
        assert len(risks) == 0


