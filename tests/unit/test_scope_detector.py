import pytest

from src.models.requirement import Requirement
from src.detectors.scope_detector import ScopeDetector


class TestScopeDetector:
    def setup_method(self):
        self.detector = ScopeDetector()

    def test_out_of_scope_terms(self):
        req = Requirement(id="R010", line_number=10, text="Support any API and all platforms without restriction")
        risks = self.detector.detect_risks(req)
        assert len(risks) >= 1
        assert any("scope creep" in r.description.lower() for r in risks)

    def test_undefined_system_boundary(self):
        req = Requirement(id="R011", line_number=11, text="Integrate with external system for data sync")
        risks = self.detector.detect_risks(req)
        assert len(risks) >= 1
        assert any("external dependency" in r.description.lower() for r in risks)

    def test_third_party_dependency_without_spec(self):
        req = Requirement(id="R012", line_number=12, text="Integrate to payment gateway")
        risks = self.detector.detect_risks(req)
        assert len(risks) >= 1
        assert any("Third-party integration" in r.description for r in risks)

    def test_ok_when_constraints_present(self):
        req = Requirement(
            id="R013",
            line_number=13,
            text="Integrate with provider X using protocol Y v2; SLA 99.9%"
        )
        risks = self.detector.detect_risks(req)
        # constraints present should avoid the third_party_dependency_without_spec signal
        assert all("Third-party integration" not in r.description for r in risks)


