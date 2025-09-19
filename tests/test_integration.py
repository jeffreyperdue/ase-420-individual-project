"""
Integration tests for StressSpec.

These tests verify that the complete workflow from file loading
to requirement parsing works correctly.
"""

import pytest
import tempfile
import os
from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser


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
