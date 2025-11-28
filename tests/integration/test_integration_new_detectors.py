import tempfile
import os

from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser
from src.factories.detector_factory import RiskDetectorFactory
from src.analyzer import analyze_requirements


def test_integration_includes_traceability_and_scope_categories():
    content = """
The system shall be user-friendly.
---
The system shall support any API on all platforms.
---
Acceptance Criteria: When user logs in, Then dashboard loads.
---
The system shall integrate with external system for data sync.
""".strip()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        loader = FileLoader()
        structured = loader.load_file_structured(temp_path)

        parser = RequirementParser()
        requirements = parser.parse_structured_requirements(structured)

        factory = RiskDetectorFactory()
        detectors = factory.create_enabled_detectors() or factory.create_all_detectors()

        risks_by_req = analyze_requirements(requirements, detectors)

        categories = set()
        for risks in risks_by_req.values():
            for r in risks:
                categories.add(r.category.value if hasattr(r.category, 'value') else str(r.category))

        assert 'traceability' in categories
        assert 'scope' in categories
    finally:
        os.unlink(temp_path)


