"""
File loader module for StressSpec.

This module handles loading and basic processing of requirement files.
Follows Single Responsibility Principle by focusing only on file operations.

BEGINNER NOTES:
- This is like a "file clerk" who knows how to read different types of files
- It only cares about getting text from files - it doesn't understand requirements
- It follows the "Single Responsibility Principle" - one job, done well
- It's like a librarian who can find and read books, but doesn't interpret them
"""

import os          # For operating system operations
from pathlib import Path  # For handling file paths (works on Windows, Mac, Linux)
from typing import List, Dict   # For type hints (makes code more readable)
from .requirement_structure_detector import RequirementStructureDetector


class FileLoader:
    """
    Handles loading of requirement files from disk.
    
    BEGINNER NOTES:
    - This class is like a specialized employee who only reads files
    - It doesn't understand what requirements are - it just gets text from files
    - It's like a photocopier that can copy different types of documents
    
    This class is responsible for:
    - Validating file paths and extensions (making sure file exists and is right type)
    - Reading file contents (actually getting the text from the file)
    - Basic line processing (cleaning up the text - removing empty lines, comments, etc.)
    """
    
    # Class variable - shared by all instances of FileLoader
    # This is like a "rule book" that says "we only accept these file types"
    SUPPORTED_EXTENSIONS = {'.txt', '.md'}
    
    def __init__(self):
        """
        Initialize the file loader.
        
        BEGINNER NOTES:
        - This is the "constructor" - it runs when you create a new FileLoader
        - Right now it doesn't need to set up anything special, so it's empty
        - It's like hiring a new employee - they're ready to work immediately
        """
        pass  # No setup needed for this simple class
    
    def load_file_structured(self, file_path: str) -> List[Dict]:
        """
        Load and parse a file with structured requirement detection.
        
        BEGINNER NOTES:
        - This method uses the structure detector to understand requirement formats
        - It combines related lines into complete requirements
        - It filters out separators, headers, and other non-requirement content
        - It returns structured requirement data instead of just raw lines
        
        Args:
            file_path: Path to the requirement file
            
        Returns:
            List of structured requirement dictionaries
        """
        # Load raw lines first
        raw_lines = self._load_raw_lines(file_path)
        
        # Use structure detector to parse requirements
        detector = RequirementStructureDetector()
        structured_requirements = detector.parse_structured_requirements(raw_lines)
        
        # Filter out invalid requirements
        valid_requirements = detector.filter_valid_requirements(structured_requirements)
        
        # Make sure we got something useful
        if not valid_requirements:
            raise ValueError(f"File contains no valid requirements: {file_path}")
        
        return valid_requirements

    def _load_raw_lines(self, file_path: str) -> List[str]:
        """
        Load raw lines from a file without processing.
        
        BEGINNER NOTES:
        - This is a helper method that just reads the file
        - It doesn't do any cleaning or filtering
        - It's used by both load_file and load_file_structured
        
        Args:
            file_path: Path to the requirements file to load
            
        Returns:
            List of raw lines from the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        # Convert string path to Path object
        path = Path(file_path)
        
        # Check if the file exists
        if not path.exists():
            raise FileNotFoundError(f"Requirements file not found: {file_path}")
        
        # Read all lines from the file
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except UnicodeDecodeError:
            # If UTF-8 fails, try with latin-1
            with open(path, 'r', encoding='latin-1') as file:
                return file.readlines()

    def load_file(self, file_path: str) -> List[str]:
        """
        Load a requirements file and return processed lines.
        
        BEGINNER NOTES:
        - This is the main "work" function of the FileLoader
        - It's like a recipe: check file → read file → clean up text → return result
        - It handles errors gracefully (like a good employee who reports problems)
        
        Args:
            file_path: Path to the requirements file (like "data/requirements.txt")
            
        Returns:
            List of non-empty, processed requirement lines (clean text ready for parsing)
            
        Raises:
            FileNotFoundError: If the file doesn't exist (like looking for a book that's not in the library)
            ValueError: If the file has wrong type or is empty (like getting a blank book)
        """
        # Convert string path to Path object (handles Windows/Mac/Linux differences)
        path = Path(file_path)
        
        # Step 1: Check if file exists (like checking if a book is in the library)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Step 2: Check if file type is supported (like checking if it's a book, not a DVD)
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension: {path.suffix}. "
                f"Supported extensions: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        # Step 3: Read the file content
        try:
            # Try to read with UTF-8 encoding (handles most text files)
            with open(path, 'r', encoding='utf-8') as file:
                lines = file.readlines()  # Read all lines into a list
        except UnicodeDecodeError:
            # If UTF-8 fails, try with latin-1 (handles older files)
            with open(path, 'r', encoding='latin-1') as file:
                lines = file.readlines()
        
        # Step 4: Clean up the lines (remove empty lines, comments, etc.)
        processed_lines = self._process_lines(lines)
        
        # Step 5: Make sure we got something useful
        if not processed_lines:
            raise ValueError(f"File contains no valid requirements: {file_path}")
        
        return processed_lines
    
    def _process_lines(self, raw_lines: List[str]) -> List[str]:
        """
        Process raw file lines by filtering and cleaning.
        
        BEGINNER NOTES:
        - This is a "helper" function (starts with _) - it's used internally
        - It's like a cleaning service that removes unwanted stuff
        - It goes through each line and decides "keep it" or "throw it away"
        
        Args:
            raw_lines: Raw lines from the file (might have empty lines, comments, etc.)
            
        Returns:
            List of processed, non-empty requirement lines (only the good stuff)
        """
        processed = []  # Start with empty list - we'll add good lines here
        
        # Go through each line in the file
        for line in raw_lines:
            # Step 1: Remove leading and trailing whitespace (spaces, tabs, newlines)
            cleaned_line = line.strip()
            
            # Step 2: Skip empty lines (nothing left after removing whitespace)
            if not cleaned_line:
                continue  # Skip this line, go to next one
            
            # Step 3: Skip comment lines (lines that start with # or //)
            if cleaned_line.startswith('#') or cleaned_line.startswith('//'):
                continue  # Skip this line, go to next one
            
            # Step 4: If we get here, it's a good line - add it to our results
            processed.append(cleaned_line)
        
        return processed  # Return only the lines we want to keep
