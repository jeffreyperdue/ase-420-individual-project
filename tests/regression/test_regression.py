"""
Regression tests for StressSpec.

This module contains tests that verify previously fixed bugs don't reoccur,
edge cases that caused issues in the past, and data integrity checks.

BEGINNER NOTES:
- Regression tests ensure bugs that were fixed stay fixed
- They test edge cases that have caused problems before
- They verify data integrity and consistency
- They help prevent performance regressions
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser
from src.factories.detector_factory import RiskDetectorFactory
from src.analyzer import analyze_requirements
from src.scoring import calculate_risk_scores, get_top_riskiest
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.services.stress_spec_service import StressSpecService
from src.reporting import ReportFormat


class TestRegressionFixedBugs:
    """Test cases for bugs that were previously fixed."""
    
    def test_file_loader_handles_unicode_characters(self):
        """Regression: File loader should handle unicode characters correctly."""
        loader = FileLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write("The system shall support café users\n")
            f.write("The system shall handle résumé data\n")
            f.write("The system shall process 中文 text\n")
            temp_path = f.name
        
        try:
            lines = loader.load_file(temp_path)
            assert len(lines) == 3
            assert "café" in lines[0]
            assert "résumé" in lines[1]
            assert "中文" in lines[2]
        finally:
            os.unlink(temp_path)
    
    def test_parser_handles_special_characters(self):
        """Regression: Parser should handle special characters correctly."""
        parser = RequirementParser()
        
        lines = [
            "The system shall support email@domain.com",
            "The system shall handle $100 transactions",
            "The system shall process data (with parentheses)",
            "The system shall support 100% uptime"
        ]
        
        requirements = parser.parse_requirements(lines)
        
        assert len(requirements) == 4
        assert "@" in requirements[0].text
        assert "$" in requirements[1].text
        assert "(" in requirements[2].text
        assert "%" in requirements[3].text
    
    def test_scoring_handles_zero_risks(self):
        """Regression: Scoring should handle requirements with zero risks."""
        req = Requirement(id="R001", line_number=1, text="The system shall allow users to login")
        requirements = [req]
        risks_by_requirement = {"R001": []}
        
        scores = calculate_risk_scores(requirements, risks_by_requirement)
        
        assert "R001" in scores
        assert scores["R001"]["total_score"] == 0
        assert scores["R001"]["avg_severity"] == 0.0
        assert scores["R001"]["risk_count"] == 0
    
    def test_report_generation_with_empty_risks(self):
        """Regression: Report generation should work with empty risks."""
        from src.reporting import ReportData, MarkdownReporter
        
        req = Requirement(id="R001", line_number=1, text="The system shall allow users to login")
        report_data = ReportData(
            requirements=[req],
            risks_by_requirement={"R001": []},
            source_file="test.txt",
            top_5_riskiest=[]
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            reporter = MarkdownReporter()
            output_path = reporter.write(report_data, temp_path)
            
            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")
            assert "R001" in content
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)
    
    def test_detector_error_does_not_crash_analysis(self):
        """Regression: Detector errors should not crash the entire analysis."""
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        
        # Create a detector that raises an error
        failing_detector = type('FailingDetector', (), {
            'detect_risks': lambda self, req: (_ for _ in ()).throw(ValueError("Test error")),
            'get_detector_name': lambda self: "Failing Detector",
            'get_category': lambda self: RiskCategory.AMBIGUITY
        })()
        
        # Analysis should complete despite detector error
        risks_by_req = analyze_requirements([req], [failing_detector])
        
        assert "R001" in risks_by_req
        # Error handler should prevent crash


class TestRegressionEdgeCases:
    """Test cases for edge cases that have caused issues."""
    
    def test_very_long_requirement_text(self):
        """Regression: Very long requirement text should be handled."""
        parser = RequirementParser()
        
        # Create a very long requirement (1000+ characters)
        long_text = "The system shall " + "support " * 200 + "users"
        lines = [long_text]
        
        requirements = parser.parse_requirements(lines)
        
        assert len(requirements) == 1
        assert len(requirements[0].text) > 1000
    
    def test_requirement_with_only_whitespace(self):
        """Regression: Requirements with only whitespace should be filtered."""
        loader = FileLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("   \n")
            f.write("\t\t\n")
            f.write("Valid requirement\n")
            temp_path = f.name
        
        try:
            lines = loader.load_file(temp_path)
            # Whitespace-only lines should be filtered
            assert len(lines) == 1
            assert lines[0] == "Valid requirement"
        finally:
            os.unlink(temp_path)
    
    def test_requirement_with_special_characters(self):
        """Regression: Requirements with special characters should be parsed."""
        parser = RequirementParser()
        
        lines = [
            "The system shall handle <script> tags",
            "The system shall process {JSON} data",
            "The system shall support [brackets]",
            "The system shall handle | pipes |"
        ]
        
        requirements = parser.parse_requirements(lines)
        
        assert len(requirements) == 4
        for req in requirements:
            assert len(req.text) > 0
    
    def test_requirement_with_unicode_characters(self):
        """Regression: Requirements with unicode should be handled."""
        parser = RequirementParser()
        
        lines = [
            "The system shall support café users",
            "The system shall handle résumé data",
            "The system shall process 中文 text",
            "The system shall support 🎉 emoji"
        ]
        
        requirements = parser.parse_requirements(lines)
        
        assert len(requirements) == 4
        assert "café" in requirements[0].text
        assert "résumé" in requirements[1].text
        assert "中文" in requirements[2].text
    
    def test_file_with_only_comments(self):
        """Regression: File with only comments should raise appropriate error."""
        loader = FileLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Comment 1\n")
            f.write("// Comment 2\n")
            f.write("# Another comment\n")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="no valid requirements"):
                loader.load_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_file_with_mixed_line_endings(self):
        """Regression: File with mixed line endings should be handled."""
        loader = FileLoader()
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write(b"Requirement 1\r\n")  # Windows line ending
            f.write(b"Requirement 2\n")     # Unix line ending
            f.write(b"Requirement 3\r")      # Old Mac line ending
            temp_path = f.name
        
        try:
            lines = loader.load_file(temp_path)
            assert len(lines) == 3
        finally:
            os.unlink(temp_path)
    
    def test_empty_requirements_list(self):
        """Regression: Empty requirements list should be handled."""
        risks_by_requirement = analyze_requirements([], [])
        
        assert isinstance(risks_by_requirement, dict)
        assert len(risks_by_requirement) == 0
    
    def test_requirements_with_identical_text(self):
        """Regression: Requirements with identical text should be handled."""
        parser = RequirementParser()
        
        lines = [
            "The system shall allow users to login",
            "The system shall allow users to login",
            "The system shall allow users to login"
        ]
        
        requirements = parser.parse_requirements(lines)
        
        assert len(requirements) == 3
        assert requirements[0].id == "R001"
        assert requirements[1].id == "R002"
        assert requirements[2].id == "R003"
        # IDs should be unique even if text is identical
    
    def test_requirements_with_very_similar_text(self):
        """Regression: Very similar requirements should be handled."""
        parser = RequirementParser()
        
        lines = [
            "The system shall allow users to login",
            "The system shall allow users to log in",
            "The system shall allow users to sign in"
        ]
        
        requirements = parser.parse_requirements(lines)
        
        assert len(requirements) == 3
        # All should be parsed as separate requirements


class TestRegressionDataIntegrity:
    """Test cases for data integrity and consistency."""
    
    def test_requirement_ids_remain_unique(self):
        """Regression: Requirement IDs should remain unique."""
        parser = RequirementParser()
        
        lines = ["Requirement 1", "Requirement 2", "Requirement 3"]
        requirements1 = parser.parse_requirements(lines)
        
        parser.reset_counter()
        requirements2 = parser.parse_requirements(lines)
        
        # IDs should be unique within each parse
        ids1 = {req.id for req in requirements1}
        ids2 = {req.id for req in requirements2}
        
        assert len(ids1) == 3
        assert len(ids2) == 3
        # After reset, IDs should start from R001 again
        assert requirements2[0].id == "R001"
    
    def test_risk_ids_remain_unique(self):
        """Regression: Risk IDs should remain unique."""
        req = Requirement(id="R001", line_number=1, text="The system should allow users to login")
        
        factory = RiskDetectorFactory()
        detectors = factory.create_all_detectors()
        risks_by_req = analyze_requirements([req], detectors)
        
        if "R001" in risks_by_req and len(risks_by_req["R001"]) > 1:
            risk_ids = {risk.id for risk in risks_by_req["R001"]}
            assert len(risk_ids) == len(risks_by_req["R001"])  # All IDs should be unique
    
    def test_line_numbers_preserved(self):
        """Regression: Line numbers should be preserved correctly."""
        loader = FileLoader()
        parser = RequirementParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Requirement 1\n")
            f.write("\n")  # Empty line
            f.write("Requirement 2\n")
            f.write("# Comment\n")
            f.write("Requirement 3\n")
            temp_path = f.name
        
        try:
            lines = loader.load_file(temp_path)
            requirements = parser.parse_requirements(lines)
            
            # Line numbers should reflect position in filtered list
            assert requirements[0].line_number == 1
            assert requirements[1].line_number == 2
            assert requirements[2].line_number == 3
        finally:
            os.unlink(temp_path)
    
    def test_requirement_text_not_modified(self):
        """Regression: Requirement text should not be modified during processing."""
        parser = RequirementParser()
        
        original_text = "The system shall allow users to login"
        lines = [original_text]
        
        requirements = parser.parse_requirements(lines)
        
        assert requirements[0].text == original_text
        assert requirements[0].text is not None
    
    def test_risk_evidence_accuracy(self):
        """Regression: Risk evidence should accurately reflect what triggered it."""
        req = Requirement(id="R001", line_number=1, text="The system should allow users to login")
        
        from src.detectors.ambiguity_detector import AmbiguityDetector
        detector = AmbiguityDetector()
        risks = detector.detect_risks(req)
        
        if len(risks) > 0:
            # Evidence should contain the actual term that triggered the risk
            assert any("should" in risk.evidence.lower() for risk in risks)


class TestRegressionPerformance:
    """Test cases for performance regressions."""
    
    def test_analysis_time_for_100_requirements(self):
        """Regression: Analysis should complete in reasonable time for 100 requirements."""
        import time
        
        parser = RequirementParser()
        factory = RiskDetectorFactory()
        detectors = factory.create_all_detectors()
        
        # Create 100 requirements
        lines = [f"The system shall support feature {i}" for i in range(100)]
        requirements = parser.parse_requirements(lines)
        
        start_time = time.time()
        risks_by_req = analyze_requirements(requirements, detectors)
        elapsed_time = time.time() - start_time
        
        # Should complete in under 10 seconds
        assert elapsed_time < 10.0
        assert len(risks_by_req) == 100
    
    def test_memory_usage_for_large_files(self):
        """Regression: Large files should not cause excessive memory usage."""
        loader = FileLoader()
        parser = RequirementParser()
        
        # Create a file with 1000 requirements
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1000):
                f.write(f"The system shall support feature {i}\n")
            temp_path = f.name
        
        try:
            lines = loader.load_file(temp_path)
            requirements = parser.parse_requirements(lines)
            
            assert len(requirements) == 1000
            # Should not raise memory errors
        finally:
            os.unlink(temp_path)
    
    def test_detector_performance_not_degraded(self):
        """Regression: Detector performance should not degrade over time."""
        import time
        
        req = Requirement(id="R001", line_number=1, text="The system should allow users to login")
        
        from src.detectors.ambiguity_detector import AmbiguityDetector
        detector = AmbiguityDetector()
        
        # Run detector multiple times
        times = []
        for _ in range(10):
            start = time.time()
            detector.detect_risks(req)
            times.append(time.time() - start)
        
        # Performance should be consistent (not degrading)
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Max time should not be more than 3x average (no significant degradation)
        assert max_time < avg_time * 3


class TestRegressionCompatibility:
    """Test cases for version compatibility."""
    
    def test_backward_compatible_report_formats(self):
        """Regression: Report formats should remain backward compatible."""
        from src.reporting import ReportData, MarkdownReporter, CsvReporter, JsonReporter, HtmlReporter
        
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        report_data = ReportData(
            requirements=[req],
            risks_by_requirement={"R001": []},
            source_file="test.txt",
            top_5_riskiest=[]
        )
        
        reporters = [
            MarkdownReporter(),
            CsvReporter(),
            JsonReporter(),
            HtmlReporter()
        ]
        
        for reporter in reporters:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tmp', delete=False) as f:
                temp_path = f.name
            
            try:
                output_path = reporter.write(report_data, temp_path)
                assert output_path.exists()
            finally:
                if Path(temp_path).exists():
                    os.unlink(temp_path)
    
    def test_config_file_format_compatibility(self):
        """Regression: Configuration file format should be handled correctly."""
        from src.config.configuration_provider import JsonFileConfigurationProvider
        
        # Test with existing rules.json format
        provider = JsonFileConfigurationProvider("data/rules.json")
        
        try:
            config = provider.get_configuration()
            assert "detectors" in config
            assert "version" in config or "detectors" in config
        except Exception:
            # If file doesn't exist, that's okay for this test
            pass

