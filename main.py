#!/usr/bin/env python3
"""
StressSpec - Requirements Stress Tester
Main entry point for the application.

This module provides the CLI interface for analyzing requirement documents
and detecting potential risks and issues.

BEGINNER NOTES:
- This is the "front door" of our application - the first thing users interact with
- It handles command-line arguments (like --file and --verbose)
- It coordinates all the other modules to do the actual work
- Think of it like a restaurant host who takes your order and coordinates with the kitchen
"""

# Standard library imports - these come with Python
import argparse  # For handling command-line arguments (--file, --verbose, etc.)
import sys       # For system operations like exiting with error codes
from pathlib import Path  # For handling file paths in a cross-platform way
from typing import List, Optional  # For type hints (makes code more readable)

# Our custom modules - these are the "workers" that do the actual processing
from src.file_loader import FileLoader          # Loads and processes requirement files
from src.requirement_parser import RequirementParser  # Converts raw text into structured requirements
from src.models.requirement import Requirement  # The data structure that represents a single requirement


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    BEGINNER NOTES:
    - This function sets up what command-line options our program accepts
    - argparse is Python's built-in tool for handling command-line arguments
    - It automatically generates help text and handles errors
    - Returns a namespace object that contains the parsed arguments
    """
    # Create the argument parser with a description and examples
    parser = argparse.ArgumentParser(
        description="StressSpec - Requirements Stress Tester",
        formatter_class=argparse.RawDescriptionHelpFormatter,  # Allows multi-line help text
        epilog="""
Examples:
  python main.py --file requirements.txt
  python main.py --file requirements.md
  python main.py --file data/sample_requirements.txt
        """
    )
    
    # Add the --file argument (required)
    parser.add_argument(
        "--file", "-f",           # Both --file and -f work
        type=str,                 # Expects a string (file path)
        required=True,            # User MUST provide this argument
        help="Path to the requirements file (.txt or .md)"
    )
    
    # Add the --verbose argument (optional flag)
    parser.add_argument(
        "--verbose", "-v",        # Both --verbose and -v work
        action="store_true",      # If present, sets to True; if absent, sets to False
        help="Enable verbose output"
    )
    
    # Parse the arguments and return them
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the application.
    
    BEGINNER NOTES:
    - This is the "orchestrator" function that coordinates everything
    - It follows the pattern: parse arguments → load file → parse requirements → display results
    - Uses try/except to handle errors gracefully
    - sys.exit(1) means "exit with error code 1" (indicates failure)
    """
    try:
        # Step 1: Parse command-line arguments
        args = parse_arguments()
        
        # Step 2: Show verbose output if requested
        if args.verbose:
            print("StressSpec - Requirements Stress Tester")
            print("=" * 50)
            print(f"Input file: {args.file}")
            print()
        
        # Step 3: Initialize our "worker" objects
        # These are like hiring employees to do specific jobs
        file_loader = FileLoader()      # Employee who reads files
        parser = RequirementParser()    # Employee who processes text into requirements
        
        # Step 4: Load the file and get raw text lines
        raw_lines = file_loader.load_file(args.file)
        
        # Step 5: Convert raw lines into structured Requirement objects
        requirements = parser.parse_requirements(raw_lines)
        
        # Step 6: Display the results to the user
        print(f"Successfully parsed {len(requirements)} requirements:")
        print("-" * 50)
        
        # Loop through each requirement and display it
        for req in requirements:
            print(f"{req.id}: Line {req.line_number}")  # Show ID and line number
            print(f"  {req.text}")                      # Show the actual requirement text
            print()                                     # Empty line for readability
        
        # Step 7: Show completion message if verbose
        if args.verbose:
            print("=" * 50)
            print("Parsing completed successfully!")
            
    # Error handling - different types of errors get different messages
    except FileNotFoundError as e:
        # This happens when the file doesn't exist
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)  # Exit with error code 1
    except ValueError as e:
        # This happens when the file has wrong format or is empty
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # This catches any other unexpected errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


# This is a Python idiom - only run main() if this file is executed directly
# (not if it's imported as a module)
if __name__ == "__main__":
    main()
