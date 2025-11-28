"""
Integration tests for StressSpec.

These tests verify that the complete workflow from file loading
to requirement parsing works correctly.
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
from src.reporting import ReportData, MarkdownReporter, CsvReporter, JsonReporter, HtmlReporter


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = FileLoader()
        self.parser = RequirementParser()
    
    def test_complete_workflow_txt_file(self):
        """Test complete workflow with a .txt file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The system shall allow users to login\n")
            f.write("The system shall display dashboard\n")
            f.write("# This is a comment\n")
            f.write("The system shall handle errors gracefully\n")
            temp_path = f.name
        
        try:
            # Load file
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 3  # Comments should be filtered
            
            # Parse requirements
            requirements = self.parser.parse_requirements(lines)
            assert len(requirements) == 3
            
            # Verify requirements
            assert requirements[0].id == "R001"
            assert requirements[0].line_number == 1
            assert requirements[0].text == "The system shall allow users to login"
            
            assert requirements[1].id == "R002"
            assert requirements[1].line_number == 2
            assert requirements[1].text == "The system shall display dashboard"
            
            assert requirements[2].id == "R003"
            assert requirements[2].line_number == 3  # Line number in processed list
            assert requirements[2].text == "The system shall handle errors gracefully"
            
            # Run detectors end-to-end and ensure risks dict exists
            factory = RiskDetectorFactory()
            detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
            risks_by_req = analyze_requirements(requirements, detectors)
            assert set(risks_by_req.keys()) == {"R001", "R002", "R003"}

        finally:
            os.unlink(temp_path)
    
    def test_complete_workflow_md_file(self):
        """Test complete workflow with a .md file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# System Requirements\n")
            f.write("- The system shall be secure\n")
            f.write("- The system shall be fast\n")
            f.write("// Performance comment\n")
            f.write("- The system shall be reliable\n")
            temp_path = f.name
        
        try:
            # Load file
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 3  # Comments and headers should be filtered
            
            # Parse requirements
            requirements = self.parser.parse_requirements(lines)
            assert len(requirements) == 3
            
            # Verify requirements
            assert requirements[0].id == "R001"
            assert requirements[0].text == "- The system shall be secure"
            
            assert requirements[1].id == "R002"
            assert requirements[1].text == "- The system shall be fast"
            
            assert requirements[2].id == "R003"
            assert requirements[2].text == "- The system shall be reliable"
            
        finally:
            os.unlink(temp_path)
    
    def test_workflow_with_empty_lines_and_comments(self):
        """Test workflow with various edge cases."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("\n")  # Empty line
            f.write("   \n")  # Whitespace line
            f.write("# Comment line\n")
            f.write("Requirement 1\n")
            f.write("\n")  # Another empty line
            f.write("// Another comment\n")
            f.write("Requirement 2\n")
            temp_path = f.name
        
        try:
            # Load file
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 2  # Only the two requirements
            
            # Parse requirements
            requirements = self.parser.parse_requirements(lines)
            assert len(requirements) == 2
            
            # Verify requirements
            assert requirements[0].id == "R001"
            assert requirements[0].text == "Requirement 1"
            
            assert requirements[1].id == "R002"
            assert requirements[1].text == "Requirement 2"
            
        finally:
            os.unlink(temp_path)
    
    def test_top_5_integration_markdown(self):
        """Test that top 5 riskiest appears in Markdown reports."""
        # Create temporary file with requirements that will trigger risks
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The system shall allow users to login with password\n")  # Security risk
            f.write("The system should be fast\n")  # Ambiguity risk
            f.write("The system shall handle data\n")  # Missing detail risk
            f.write("The system shall process requests\n")  # Performance risk
            f.write("The system shall be available\n")  # Availability risk
            temp_path = f.name
        
        try:
            # Complete workflow
            lines = self.loader.load_file(temp_path)
            requirements = self.parser.parse_requirements(lines)
            factory = RiskDetectorFactory()
            detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
            risks_by_req = analyze_requirements(requirements, detectors)
            
            # Calculate scores and top 5
            risk_scores = calculate_risk_scores(requirements, risks_by_req)
            top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
            
            # Create report data
            report_data = ReportData(
                requirements=requirements,
                risks_by_requirement=risks_by_req,
                source_file=temp_path,
                top_5_riskiest=top_5
            )
            
            # Generate Markdown report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as out_file:
                out_path = out_file.name
            
            try:
                reporter = MarkdownReporter()
                output_path = reporter.write(report_data, out_path)
                
                # Verify report was created
                assert output_path.exists()
                content = output_path.read_text(encoding="utf-8")
                
                # Verify top 5 section appears
                assert "Top 5 Riskiest Requirements" in content
                assert "These requirements have the highest combined risk scores" in content
                
            finally:
                if Path(out_path).exists():
                    os.unlink(out_path)
        
        finally:
            os.unlink(temp_path)
    
    def test_top_5_integration_json(self):
        """Test that top 5 riskiest appears in JSON reports."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The system shall allow users to login with password\n")
            f.write("The system should be fast\n")
            temp_path = f.name
        
        try:
            # Complete workflow
            lines = self.loader.load_file(temp_path)
            requirements = self.parser.parse_requirements(lines)
            factory = RiskDetectorFactory()
            detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
            risks_by_req = analyze_requirements(requirements, detectors)
            
            # Calculate scores and top 5
            risk_scores = calculate_risk_scores(requirements, risks_by_req)
            top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
            
            # Create report data
            report_data = ReportData(
                requirements=requirements,
                risks_by_requirement=risks_by_req,
                source_file=temp_path,
                top_5_riskiest=top_5
            )
            
            # Generate JSON report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out_file:
                out_path = out_file.name
            
            try:
                reporter = JsonReporter()
                output_path = reporter.write(report_data, out_path)
                
                # Verify report was created
                assert output_path.exists()
                content = json.loads(output_path.read_text(encoding="utf-8"))
                
                # Verify top 5 appears in JSON
                assert "top_5_riskiest" in content
                assert isinstance(content["top_5_riskiest"], list)
                if top_5:  # Only check if there are risks
                    assert len(content["top_5_riskiest"]) > 0
                    
                    # Verify structure
                    top_item = content["top_5_riskiest"][0]
                    assert "requirement_id" in top_item
                    assert "total_score" in top_item
                    assert "risk_count" in top_item
                
            finally:
                if Path(out_path).exists():
                    os.unlink(out_path)
        
        finally:
            os.unlink(temp_path)
    
    def test_top_5_integration_csv(self):
        """Test that top 5 riskiest appears in CSV reports."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The system shall allow users to login with password\n")
            f.write("The system should be fast\n")
            temp_path = f.name
        
        try:
            # Complete workflow
            lines = self.loader.load_file(temp_path)
            requirements = self.parser.parse_requirements(lines)
            factory = RiskDetectorFactory()
            detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
            risks_by_req = analyze_requirements(requirements, detectors)
            
            # Calculate scores and top 5
            risk_scores = calculate_risk_scores(requirements, risks_by_req)
            top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
            
            # Create report data
            report_data = ReportData(
                requirements=requirements,
                risks_by_requirement=risks_by_req,
                source_file=temp_path,
                top_5_riskiest=top_5
            )
            
            # Generate CSV report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as out_file:
                out_path = out_file.name
            
            try:
                reporter = CsvReporter()
                output_path = reporter.write(report_data, out_path)
                
                # Verify report was created
                assert output_path.exists()
                content = output_path.read_text(encoding="utf-8")
                
                # Verify score columns appear in CSV
                assert "total_score" in content
                assert "avg_severity" in content
                assert "risk_count" in content
                
                # Verify top 5 summary CSV was created if there are risks
                summary_path = output_path.parent / f"{output_path.stem}_top5.csv"
                if top_5:
                    assert summary_path.exists()
                    summary_content = summary_path.read_text(encoding="utf-8")
                    assert "rank" in summary_content
                    assert "total_score" in summary_content
                    
                    # Clean up summary file
                    if summary_path.exists():
                        os.unlink(summary_path)
                
            finally:
                if Path(out_path).exists():
                    os.unlink(out_path)
        
        finally:
            os.unlink(temp_path)
    
    def test_top_5_integration_html(self):
        """Test that top 5 riskiest appears in HTML reports."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The system shall allow users to login with password\n")
            f.write("The system should be fast\n")
            temp_path = f.name
        
        try:
            # Complete workflow
            lines = self.loader.load_file(temp_path)
            requirements = self.parser.parse_requirements(lines)
            factory = RiskDetectorFactory()
            detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
            risks_by_req = analyze_requirements(requirements, detectors)
            
            # Calculate scores and top 5
            risk_scores = calculate_risk_scores(requirements, risks_by_req)
            top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
            
            # Create report data
            report_data = ReportData(
                requirements=requirements,
                risks_by_requirement=risks_by_req,
                source_file=temp_path,
                top_5_riskiest=top_5
            )
            
            # Generate HTML report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as out_file:
                out_path = out_file.name
            
            try:
                reporter = HtmlReporter()
                output_path = reporter.write(report_data, out_path)
                
                # Verify report was created
                assert output_path.exists()
                content = output_path.read_text(encoding="utf-8")
                
                # Verify HTML structure and top 5 section appears
                assert "<!DOCTYPE html>" in content
                assert "StressSpec Report" in content
                assert "Top 5 Riskiest Requirements" in content
                assert "These requirements have the highest combined risk scores" in content
                
                # Verify summary statistics are present
                assert "Summary" in content
                assert "Total Requirements" in content
                assert "Total Risks" in content
                
                # Verify detailed requirements section
                assert "Detailed Requirements" in content
                
            finally:
                if Path(out_path).exists():
                    os.unlink(out_path)
        
        finally:
            os.unlink(temp_path)
