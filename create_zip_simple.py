#!/usr/bin/env python3
"""Simple zip creator that writes output to a file."""
import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUT_DIR = PROJECT_ROOT.parent
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_filename = f"StressSpec_Clean_{timestamp}.zip"
output_path = OUTPUT_DIR / zip_filename

# Exclusion patterns
EXCLUDE_DIRS = {'__pycache__', '.git', 'demo', 'test_logs', 'data/backups', 'logs', 'uploads'}
EXCLUDE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.log', '.tmp', '.temp', '.swp', '.swo'}
EXCLUDE_NAMES = {'.gitignore', '.gitkeep', '.DS_Store', 'Thumbs.db', 'desktop.ini'}
# PDFs are now INCLUDED in the zip file

log_file = PROJECT_ROOT / 'zip_creation.log'
with open(log_file, 'w') as log:
    log.write(f"Starting zip creation...\n")
    log.write(f"Project root: {PROJECT_ROOT}\n")
    log.write(f"Output: {output_path}\n\n")
    log.flush()
    
    included = 0
    excluded = 0
    
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(PROJECT_ROOT):
                # Filter directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
                
                root_path = Path(root)
                
                # Skip excluded directories
                rel_root = root_path.relative_to(PROJECT_ROOT)
                if any(excl in str(rel_root) for excl in EXCLUDE_DIRS):
                    continue
                
                for file in files:
                    file_path = root_path / file
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    rel_str = str(rel_path).replace('\\', '/')
                    
                    # Check exclusions
                    skip = False
                    
                    # Check directory exclusions
                    for part in rel_str.split('/'):
                        if part in EXCLUDE_DIRS:
                            skip = True
                            break
                    
                    if skip:
                        excluded += 1
                        continue
                    
                    # Check file extensions
                    if file_path.suffix in EXCLUDE_EXTENSIONS:
                        excluded += 1
                        continue
                    
                    # Check file names
                    if file_path.name in EXCLUDE_NAMES:
                        excluded += 1
                        continue
                    
                    # PDFs are now INCLUDED (no exclusion check)
                    
                    # Exclude the zip creation scripts themselves
                    if 'create_clean_zip.py' in rel_str or 'create_zip_simple.py' in rel_str:
                        excluded += 1
                        continue
                    
                    # Add file
                    try:
                        zf.write(file_path, rel_path)
                        included += 1
                        if included % 100 == 0:
                            log.write(f"Processed {included} files...\n")
                            log.flush()
                    except Exception as e:
                        log.write(f"Error adding {rel_path}: {e}\n")
                        log.flush()
        
        size_mb = output_path.stat().st_size / (1024 * 1024)
        log.write(f"\n{'='*60}\n")
        log.write(f"SUCCESS!\n")
        log.write(f"{'='*60}\n")
        log.write(f"Output: {output_path}\n")
        log.write(f"Size: {size_mb:.2f} MB\n")
        log.write(f"Included: {included} files\n")
        log.write(f"Excluded: {excluded} files\n")
        log.flush()
        
        print(f"SUCCESS! Zip file created: {output_path}")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Included: {included} files, Excluded: {excluded} files")
        print(f"See {log_file} for details")
        
    except Exception as e:
        error_msg = f"ERROR: {e}\n"
        import traceback
        error_msg += traceback.format_exc()
        log.write(error_msg)
        log.flush()
        print(error_msg)
        sys.exit(1)

