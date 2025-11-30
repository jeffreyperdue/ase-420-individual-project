#!/usr/bin/env python3
"""
StressSpec - Clean Zip File Generator

This script creates a clean zip file of the StressSpec project,
excluding all automatically generated files, hidden files, and unnecessary files.

Usage:
    python create_clean_zip.py [--output-dir OUTPUT_DIR]
    
Default output location: Parent directory of the project (one level up)
"""

import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Set, List

# Get the project root directory (where this script is located)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Default output directory (parent of project root)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT.parent

# Patterns to exclude
EXCLUDE_PATTERNS = {
    # Python cache
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*$py.class',
    
    # Git files
    '.git',
    '.gitignore',
    '.gitkeep',
    
    # Log files
    '*.log',
    
    # Testing artifacts
    '.pytest_cache',
    '.coverage',
    'htmlcov',
    '.coverage.*',
    
    # OS files
    '.DS_Store',
    'Thumbs.db',
    'desktop.ini',
    
    # Temporary files
    '*.tmp',
    '*.temp',
    '*.swp',
    '*.swo',
    '*~',
    
    # Virtual environments
    'venv',
    'env',
    'ENV',
    'env.bak',
    'venv.bak',
    '.venv',
    
    # Build artifacts
    'build',
    'dist',
    '*.egg-info',
    '*.egg',
    
    # IDE files
    '.vscode',
    '.idea',
    '*.code-workspace',
    
    # Hugo build output
    'hugo/docs',
    'hugo/public',
    'hugo/resources',
}

# Directories to exclude entirely
EXCLUDE_DIRECTORIES = {
    '__pycache__',
    '.git',
    '.pytest_cache',
    'htmlcov',
    'venv',
    'env',
    'ENV',
    'build',
    'dist',
    '.vscode',
    '.idea',
    'demo',  # Demo output files
    'test_logs',  # Empty test logs directory
    'data/backups',  # Empty backups directory
}

# File patterns to exclude (by extension or name)
EXCLUDE_FILE_PATTERNS = {
    '.pyc', '.pyo', '.pyd',
    '.log',
    '.tmp', '.temp',
    '.swp', '.swo',
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    '.coverage',
}

# Specific files to exclude
EXCLUDE_FILES = {
    '.gitignore',
    '.gitkeep',
}

# PDFs are now INCLUDED in the zip file (no exclusion)
# EXCLUDE_PDF_DIRECTORIES removed - PDFs will be included

# Files in specific directories to exclude
EXCLUDE_SPECIFIC_FILES = {
    'demo',  # Exclude entire demo directory
    'uploads',  # Exclude user-uploaded files
    'logs',  # Exclude log files directory
}

def should_exclude_path(path: Path, project_root: Path) -> bool:
    """
    Determine if a path should be excluded from the zip file.
    
    Args:
        path: The path to check
        project_root: The root directory of the project
        
    Returns:
        True if the path should be excluded, False otherwise
    """
    # Get relative path from project root
    try:
        rel_path = path.relative_to(project_root)
    except ValueError:
        # Path is outside project root, exclude it
        return True
    
    # Convert to string for pattern matching
    path_str = str(rel_path).replace('\\', '/')
    path_parts = path_str.split('/')
    
    # Check if any directory in the path should be excluded
    for part in path_parts:
        if part in EXCLUDE_DIRECTORIES:
            return True
    
    # Check if it's a directory that should be excluded entirely
    if path.is_dir():
        if path.name in EXCLUDE_DIRECTORIES:
            return True
        return False
    
    # Check file patterns
    if path.suffix in EXCLUDE_FILE_PATTERNS:
        return True
    
    # Check specific file names
    if path.name in EXCLUDE_FILES:
        return True
    
    # Check if file is in a directory that should be excluded
    for exclude_dir in EXCLUDE_SPECIFIC_FILES:
        if path_str.startswith(exclude_dir + '/') or path_str == exclude_dir:
            return True
    
    # PDFs are now INCLUDED (no exclusion check)
    
    # Check for temporary files in weekly reports
    if 'weekly_reports' in path_str and path.suffix in ['.html', '.tmp']:
        if 'tmp' in path.name.lower():
            return True
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # Pattern like *.pyc
            if path.name.endswith(pattern[1:]):
                return True
        elif pattern in path_str or pattern in path.name:
            return True
    
    return False


def create_clean_zip(output_path: Path, project_root: Path) -> None:
    """
    Create a clean zip file of the project.
    
    Args:
        output_path: Path where the zip file should be created
        project_root: Root directory of the project to zip
    """
    print("Creating clean zip file...", flush=True)
    print(f"Project root: {project_root}", flush=True)
    print(f"Output file: {output_path}", flush=True)
    print(flush=True)
    
    # Counters for statistics
    included_files = 0
    excluded_files = 0
    excluded_dirs = 0
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files and directories
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)
            
            # Filter out excluded directories before walking into them
            dirs[:] = [d for d in dirs if not should_exclude_path(root_path / d, project_root)]
            
            # Process files
            for file in files:
                file_path = root_path / file
                
                if should_exclude_path(file_path, project_root):
                    excluded_files += 1
                    continue
                
                # Get relative path for zip archive
                try:
                    arcname = file_path.relative_to(project_root)
                except ValueError:
                    continue
                
                # Add file to zip
                zipf.write(file_path, arcname)
                included_files += 1
                
                # Show progress for every 50 files
                if included_files % 50 == 0:
                    print(f"  Processed {included_files} files...", end='\r', flush=True)
    
    print(flush=True)  # New line after progress
    print(flush=True)
    print("=" * 60, flush=True)
    print("Zip file created successfully!", flush=True)
    print("=" * 60, flush=True)
    print(f"Output file: {output_path}", flush=True)
    print(f"File size: {output_path.stat().st_size / (1024*1024):.2f} MB", flush=True)
    print(flush=True)
    print("Statistics:", flush=True)
    print(f"  Included files: {included_files}", flush=True)
    print(f"  Excluded files: {excluded_files}", flush=True)
    print(f"  Excluded directories: {excluded_dirs}", flush=True)
    print(flush=True)


def main():
    """Main entry point."""
    import argparse
    
    # Force output to be flushed immediately
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
    
    parser = argparse.ArgumentParser(
        description="Create a clean zip file of the StressSpec project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_clean_zip.py
  python create_clean_zip.py --output-dir C:/Users/YourName/Downloads
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f'Directory where zip file will be created (default: {DEFAULT_OUTPUT_DIR})'
    )
    
    args = parser.parse_args()
    
    # Validate output directory
    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"Error: Output directory does not exist: {output_dir}", flush=True)
        sys.exit(1)
    
    if not output_dir.is_dir():
        print(f"Error: Output path is not a directory: {output_dir}", flush=True)
        sys.exit(1)
    
    # Generate zip file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"StressSpec_Clean_{timestamp}.zip"
    output_path = output_dir / zip_filename
    
    # Check if file already exists
    if output_path.exists():
        print(f"Warning: Output file already exists: {output_path}", flush=True)
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.", flush=True)
            sys.exit(0)
    
    # Create the zip file
    try:
        create_clean_zip(output_path, PROJECT_ROOT)
        print(f"\n✅ Success! Clean zip file created at:", flush=True)
        print(f"   {output_path}", flush=True)
    except Exception as e:
        print(f"\n❌ Error creating zip file: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

