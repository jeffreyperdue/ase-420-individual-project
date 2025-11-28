"""
Unit tests for the RequirementParser class.
"""

import pytest
from src.requirement_parser import RequirementParser
from src.models.requirement import Requirement


class TestRequirementParser:
    """Test cases for the RequirementParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RequirementParser()
    
    def test_parse_single_requirement(self):
        """Test parsing a single requirement line."""
        lines = ["The system shall allow users to login"]
        requirements = self.parser.parse_requirements(lines)
        
        assert len(requirements) == 1
        assert requirements[0].id == "R001"
        assert requirements[0].line_number == 1
        assert requirements[0].text == "The system shall allow users to login"
    
    def test_parse_multiple_requirements(self):
        """Test parsing multiple requirement lines."""
        lines = [
            "The system shall allow users to login",
            "The system shall display user dashboard",
            "The system shall support password reset"
        ]
        requirements = self.parser.parse_requirements(lines)
        
        assert len(requirements) == 3
        
        # Check first requirement
        assert requirements[0].id == "R001"
        assert requirements[0].line_number == 1
        assert requirements[0].text == "The system shall allow users to login"
        
        # Check second requirement
        assert requirements[1].id == "R002"
        assert requirements[1].line_number == 2
        assert requirements[1].text == "The system shall display user dashboard"
        
        # Check third requirement
        assert requirements[2].id == "R003"
        assert requirements[2].line_number == 3
        assert requirements[2].text == "The system shall support password reset"
    
    def test_id_increment_correctly(self):
        """Test that IDs increment correctly across multiple parse calls."""
        lines1 = ["Requirement 1", "Requirement 2"]
        lines2 = ["Requirement 3", "Requirement 4"]
        
        requirements1 = self.parser.parse_requirements(lines1)
        requirements2 = self.parser.parse_requirements(lines2)
        
        assert requirements1[0].id == "R001"
        assert requirements1[1].id == "R002"
        assert requirements2[0].id == "R003"
        assert requirements2[1].id == "R004"
    
    def test_line_numbers_match_input(self):
        """Test that line numbers match the input order."""
        lines = [
            "First requirement",
            "Second requirement",
            "Third requirement"
        ]
        requirements = self.parser.parse_requirements(lines)
        
        for i, req in enumerate(requirements, start=1):
            assert req.line_number == i
    
    def test_reset_counter(self):
        """Test that counter can be reset."""
        lines = ["Requirement 1", "Requirement 2"]
        
        # First parse
        requirements1 = self.parser.parse_requirements(lines)
        assert requirements1[0].id == "R001"
        assert requirements1[1].id == "R002"
        
        # Reset counter
        self.parser.reset_counter()
        
        # Second parse should start from R001 again
        requirements2 = self.parser.parse_requirements(lines)
        assert requirements2[0].id == "R001"
        assert requirements2[1].id == "R002"
    
    def test_empty_lines_list(self):
        """Test parsing empty lines list."""
        requirements = self.parser.parse_requirements([])
        assert len(requirements) == 0
    
    def test_requirement_objects_are_valid(self):
        """Test that created Requirement objects are valid."""
        lines = ["The system shall validate user input"]
        requirements = self.parser.parse_requirements(lines)
        
        assert len(requirements) == 1
        req = requirements[0]
        
        # Verify it's a proper Requirement object
        assert isinstance(req, Requirement)
        assert req.id == "R001"
        assert req.line_number == 1
        assert req.text == "The system shall validate user input"
        
        # Verify string representation works
        assert str(req) == "R001: The system shall validate user input"
