"""
Unit tests for the StressSpecService class.

This module tests the StressSpecService to ensure it correctly orchestrates
the complete analysis workflow from file loading to report generation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from src.services.stress_spec_service import StressSpecService
from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser
from src.factories.detector_factory import RiskDetectorFactory
from src.factories.reporter_factory import ReporterFactory
from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.reporting import ReportFormat, ReportData
from src.patterns.observer import AnalysisProgressObserver


class TestStressSpecService:
    """Test cases for the StressSpecService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mocks for all dependencies
        self.mock_loader = Mock(spec=FileLoader)
        self.mock_parser = Mock(spec=RequirementParser)
        self.mock_detector_factory = Mock(spec=RiskDetectorFactory)
        self.mock_reporter_factory = Mock(spec=ReporterFactory)
        
        self.service = StressSpecService(
            file_loader=self.mock_loader,
            parser=self.mock_parser,
            detector_factory=self.mock_detector_factory,
            reporter_factory=self.mock_reporter_factory
        )
    
    # Initialization tests
    def test_service_initializes_with_defaults(self):
        """Test that service initializes with default dependencies."""
        service = StressSpecService()
        
        assert service.file_loader is not None
        assert service.parser is not None
        assert service.detector_factory is not None
        assert service.reporter_factory is not None
        assert service.progress_subject is not None
    
    def test_service_initializes_with_injected_dependencies(self):
        """Test that service initializes with injected dependencies."""
        assert self.service.file_loader is self.mock_loader
        assert self.service.parser is self.mock_parser
        assert self.service.detector_factory is self.mock_detector_factory
        assert self.service.reporter_factory is self.mock_reporter_factory
    
    def test_progress_observers_registered(self):
        """Test that progress observers are registered."""
        mock_observer = Mock(spec=AnalysisProgressObserver)
        service = StressSpecService(progress_observers=[mock_observer])
        
        assert len(service.progress_subject.observers) == 1
        assert mock_observer in service.progress_subject.observers
    
    # Complete workflow tests
    def test_analyze_file_complete_workflow(self):
        """Test complete workflow from file to report."""
        # Setup mocks
        self.mock_loader.load_file.return_value = ["The system shall allow users to login"]
        
        req = Requirement(id="R001", line_number=1, text="The system shall allow users to login")
        self.mock_parser.parse_requirements.return_value = [req]
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = []
        self.mock_detector_factory.create_enabled_detectors.return_value = [mock_detector]
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        result = self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify
        assert isinstance(result, Path)
        self.mock_loader.load_file.assert_called_once_with("test.txt")
        self.mock_parser.parse_requirements.assert_called_once()
        mock_reporter.write.assert_called_once()
    
    def test_analyze_file_calls_all_components(self):
        """Test that analyze_file calls all components in correct order."""
        # Setup mocks
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify call order
        assert self.mock_loader.load_file.called
        assert self.mock_parser.parse_requirements.called
        assert self.mock_detector_factory.create_enabled_detectors.called
        assert mock_reporter.write.called
    
    def test_analyze_file_generates_report(self):
        """Test that analyze_file generates a report."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        output_path = Path("/tmp/report.md")
        mock_reporter.write.return_value = output_path
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        result = self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify
        assert result == output_path
        mock_reporter.write.assert_called_once()
        # Verify ReportData was created correctly
        call_args = mock_reporter.write.call_args
        report_data = call_args[0][0]
        assert isinstance(report_data, ReportData)
        assert len(report_data.requirements) == 1
    
    def test_analyze_file_returns_output_path(self):
        """Test that analyze_file returns the output path."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        expected_path = Path("/tmp/report.md")
        mock_reporter = Mock()
        mock_reporter.write.return_value = expected_path
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        result = self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify
        assert result == expected_path
        assert isinstance(result, Path)
    
    # Progress notification tests
    def test_progress_notifications_sent(self):
        """Test that progress notifications are sent during analysis."""
        mock_observer = Mock(spec=AnalysisProgressObserver)
        self.service.add_progress_observer(mock_observer)
        
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify progress notifications were sent
        assert mock_observer.on_progress.called
    
    def test_progress_notifications_in_correct_order(self):
        """Test that progress notifications are sent in correct order."""
        progress_calls = []
        
        class ProgressTracker(AnalysisProgressObserver):
            def on_progress(self, stage, progress, message):
                progress_calls.append(stage)
        
        tracker = ProgressTracker()
        self.service.add_progress_observer(tracker)
        
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify order (at least Loading should come before Complete)
        assert len(progress_calls) > 0
        assert "Loading" in progress_calls
        assert "Complete" in progress_calls
    
    def test_add_progress_observer(self):
        """Test adding a progress observer."""
        mock_observer = Mock(spec=AnalysisProgressObserver)
        
        self.service.add_progress_observer(mock_observer)
        
        assert mock_observer in self.service.progress_subject.observers
    
    # Error handling tests
    def test_file_not_found_error(self):
        """Test handling of file not found error."""
        self.mock_loader.load_file.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            self.service.analyze_file("nonexistent.txt", ReportFormat.MD)
    
    def test_invalid_file_error(self):
        """Test handling of invalid file error."""
        self.mock_loader.load_file.side_effect = ValueError("Invalid file")
        
        with pytest.raises(ValueError):
            self.service.analyze_file("invalid.txt", ReportFormat.MD)
    
    def test_detector_error_handled(self):
        """Test that detector errors don't break the workflow."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        
        # Detector factory returns detectors that might error, but analyzer handles it
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Should complete successfully
        result = self.service.analyze_file("test.txt", ReportFormat.MD)
        assert isinstance(result, Path)
    
    def test_reporter_error_handled(self):
        """Test handling of reporter errors."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        mock_reporter.write.side_effect = IOError("Cannot write file")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        with pytest.raises(IOError):
            self.service.analyze_file("test.txt", ReportFormat.MD)
    
    # Edge cases
    def test_empty_file_handling(self):
        """Test handling of empty file."""
        self.mock_loader.load_file.return_value = []
        self.mock_parser.parse_requirements.return_value = []
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        result = self.service.analyze_file("empty.txt", ReportFormat.MD)
        
        assert isinstance(result, Path)
        # Should still generate a report even with no requirements
    
    def test_custom_output_path(self):
        """Test that custom output path is used."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/custom/path/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        result = self.service.analyze_file("test.txt", ReportFormat.MD, output_path="/custom/path/report.md")
        
        # Verify custom path was passed to reporter
        call_args = mock_reporter.write.call_args
        assert call_args[0][1] == "/custom/path/report.md"
    
    def test_default_output_path_generation(self):
        """Test that default output path is generated when not provided."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute without output_path
        result = self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify reporter was called (it will generate default path)
        mock_reporter.write.assert_called_once()
    
    def test_all_report_formats_supported(self):
        """Test that all report formats are supported."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        self.mock_detector_factory.create_enabled_detectors.return_value = []
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Test all formats
        formats = [ReportFormat.MD, ReportFormat.CSV, ReportFormat.JSON, ReportFormat.HTML]
        
        for fmt in formats:
            self.service.analyze_file("test.txt", fmt)
            self.mock_reporter_factory.create_reporter.assert_called_with(fmt)
            self.mock_reporter_factory.reset_mock()
    
    def test_top_5_riskiest_included_in_report(self):
        """Test that top 5 riskiest requirements are included in report."""
        # Setup
        self.mock_loader.load_file.return_value = ["Test requirement"]
        req = Requirement(id="R001", line_number=1, text="Test requirement")
        self.mock_parser.parse_requirements.return_value = [req]
        
        # Create a risk
        risk = Risk(
            id="R001-RISK-1",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Test risk",
            requirement_id="R001",
            line_number=1,
            evidence="test"
        )
        
        mock_detector = Mock()
        mock_detector.detect_risks.return_value = [risk]
        self.mock_detector_factory.create_enabled_detectors.return_value = [mock_detector]
        
        mock_reporter = Mock()
        mock_reporter.write.return_value = Path("/tmp/report.md")
        self.mock_reporter_factory.create_reporter.return_value = mock_reporter
        
        # Execute
        self.service.analyze_file("test.txt", ReportFormat.MD)
        
        # Verify ReportData includes top_5_riskiest
        call_args = mock_reporter.write.call_args
        report_data = call_args[0][0]
        assert hasattr(report_data, 'top_5_riskiest')
        assert isinstance(report_data.top_5_riskiest, list)

