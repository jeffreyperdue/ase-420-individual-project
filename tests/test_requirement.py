"""
Unit tests for the Requirement model.

BEGINNER NOTES:
- This file tests our Requirement class to make sure it works correctly
- Unit tests are like "quality control" - they check each piece works as expected
- We test both "happy path" (normal usage) and "error cases" (what happens when things go wrong)
- If all tests pass, we know our code is working correctly
"""

import pytest  # Testing framework that helps us write and run tests
from src.models.requirement import Requirement  # The class we're testing


class TestRequirement:
    """
    Test cases for the Requirement class.
    
    BEGINNER NOTES:
    - This class contains all our tests for the Requirement model
    - Each method starting with 'test_' is a separate test
    - Tests should be independent - each one can run by itself
    """
    
    def test_requirement_creation(self):
        """
        Test basic requirement creation.
        
        BEGINNER NOTES:
        - This test checks that we can create a Requirement object with valid data
        - We create a requirement and then check that all its properties are correct
        - assert statements are like "make sure this is true, or fail the test"
        """
        # Create a Requirement object with test data
        req = Requirement(
            id="R001",
            line_number=1,
            text="The system shall allow users to login"
        )
        
        # Check that all the properties were set correctly
        assert req.id == "R001"
        assert req.line_number == 1
        assert req.text == "The system shall allow users to login"
    
    def test_requirement_string_representation(self):
        """Test string representation of requirement."""
        req = Requirement(
            id="R001",
            line_number=1,
            text="The system shall allow users to login"
        )
        
        expected = "R001: The system shall allow users to login"
        assert str(req) == expected
    
    def test_requirement_repr(self):
        """Test detailed string representation."""
        req = Requirement(
            id="R001",
            line_number=1,
            text="The system shall allow users to login with email and password"
        )
        
        repr_str = repr(req)
        assert "R001" in repr_str
        assert "line=1" in repr_str
        assert "The system shall allow users to login with email a" in repr_str
    
    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Requirement ID cannot be empty"):
            Requirement(id="", line_number=1, text="Some requirement")
    
    def test_zero_line_number_raises_error(self):
        """Test that zero line number raises ValueError."""
        with pytest.raises(ValueError, match="Line number must be positive"):
            Requirement(id="R001", line_number=0, text="Some requirement")
    
    def test_negative_line_number_raises_error(self):
        """Test that negative line number raises ValueError."""
        with pytest.raises(ValueError, match="Line number must be positive"):
            Requirement(id="R001", line_number=-1, text="Some requirement")
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Requirement text cannot be empty"):
            Requirement(id="R001", line_number=1, text="")
    
    def test_whitespace_only_text_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="Requirement text cannot be empty"):
            Requirement(id="R001", line_number=1, text="   \n\t  ")
