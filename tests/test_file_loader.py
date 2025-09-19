"""
Unit tests for the FileLoader class.
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.file_loader import FileLoader


class TestFileLoader:
    """Test cases for the FileLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = FileLoader()
    
    def test_load_valid_txt_file(self):
        """Test loading a valid .txt file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Requirement 1\n")
            f.write("Requirement 2\n")
            f.write("Requirement 3\n")
            temp_path = f.name
        
        try:
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 3
            assert lines[0] == "Requirement 1"
            assert lines[1] == "Requirement 2"
            assert lines[2] == "Requirement 3"
        finally:
            os.unlink(temp_path)
    
    def test_load_valid_md_file(self):
        """Test loading a valid .md file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Requirements\n")
            f.write("- Requirement 1\n")
            f.write("- Requirement 2\n")
            temp_path = f.name
        
        try:
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 2
            assert lines[0] == "- Requirement 1"
            assert lines[1] == "- Requirement 2"
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found_raises_error(self):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_file("nonexistent.txt")
    
    def test_unsupported_extension_raises_error(self):
        """Test that unsupported file extension raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file extension"):
                self.loader.load_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_file_raises_error(self):
        """Test that empty file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="File contains no valid requirements"):
                self.loader.load_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_file_with_only_comments_raises_error(self):
        """Test that file with only comments raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("// Another comment\n")
            f.write("   \n")  # Empty line
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="File contains no valid requirements"):
                self.loader.load_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_strips_whitespace(self):
        """Test that whitespace is properly stripped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("  Requirement 1  \n")
            f.write("\tRequirement 2\t\n")
            f.write("Requirement 3\n")
            temp_path = f.name
        
        try:
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 3
            assert lines[0] == "Requirement 1"
            assert lines[1] == "Requirement 2"
            assert lines[2] == "Requirement 3"
        finally:
            os.unlink(temp_path)
    
    def test_filters_empty_lines(self):
        """Test that empty lines are filtered out."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Requirement 1\n")
            f.write("\n")  # Empty line
            f.write("   \n")  # Whitespace-only line
            f.write("Requirement 2\n")
            temp_path = f.name
        
        try:
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 2
            assert lines[0] == "Requirement 1"
            assert lines[1] == "Requirement 2"
        finally:
            os.unlink(temp_path)
    
    def test_filters_comments(self):
        """Test that comment lines are filtered out."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("Requirement 1\n")
            f.write("// Another comment\n")
            f.write("Requirement 2\n")
            temp_path = f.name
        
        try:
            lines = self.loader.load_file(temp_path)
            assert len(lines) == 2
            assert lines[0] == "Requirement 1"
            assert lines[1] == "Requirement 2"
        finally:
            os.unlink(temp_path)
