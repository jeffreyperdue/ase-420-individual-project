#!/usr/bin/env python3
"""
StressSpec Web UI Setup Script

This script helps set up the development environment for the web UI.
It creates necessary directories, installs dependencies, and configures the environment.

BEGINNER NOTES:
- This script automates the setup process for the web interface
- It creates directories, installs packages, and sets up configuration
- Run this script after cloning the repository to get started quickly
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories for the web application."""
    directories = [
        "web",
        "web/static",
        "web/static/css",
        "web/static/js",
        "web/static/images",
        "web/templates",
        "web/templates/reports",
        "web/api",
        "uploads",
        "logs"
    ]
    
    print("[INFO] Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  [SUCCESS] Created: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    return run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def download_htmx():
    """Download HTMX library."""
    htmx_url = "https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js"
    htmx_path = "web/static/js/htmx.min.js"
    
    print("[INFO] Downloading HTMX...")
    try:
        import urllib.request
        urllib.request.urlretrieve(htmx_url, htmx_path)
        print(f"[SUCCESS] HTMX downloaded to {htmx_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download HTMX: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("[INFO] Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("[SUCCESS] .env file created. Please review and adjust settings as needed.")
        return True
    elif env_file.exists():
        print("[SUCCESS] .env file already exists")
        return True
    else:
        print("[WARNING] No env.example template found")
        return False

def verify_setup():
    """Verify that the setup was successful."""
    print("\n[INFO] Verifying setup...")
    
    # Check if key files exist
    key_files = [
        "requirements.txt",
        "web/static/js/htmx.min.js",
        ".env"
    ]
    
    all_good = True
    for file_path in key_files:
        if (project_root / file_path).exists():
            print(f"  [SUCCESS] {file_path}")
        else:
            print(f"  [ERROR] {file_path} (missing)")
            all_good = False
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import jinja2
        print("  [SUCCESS] FastAPI dependencies installed")
    except ImportError as e:
        print(f"  [ERROR] FastAPI dependencies not installed: {e}")
        all_good = False
    
    return all_good

def main():
    """Main setup function."""
    print("StressSpec Web UI Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ is required")
        sys.exit(1)
    
    print(f"[SUCCESS] Python {sys.version.split()[0]} detected")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("[ERROR] Failed to install dependencies")
        sys.exit(1)
    
    # Download HTMX
    if not download_htmx():
        print("[WARNING] HTMX download failed, but setup can continue")
    
    # Create environment file
    create_env_file()
    
    # Verify setup
    if verify_setup():
        print("\n[SUCCESS] Setup completed successfully!")
        print("\nNext steps:")
        print("1. Review and adjust .env file if needed")
        print("2. Run: python run_web.py")
        print("3. Open http://127.0.0.1:8000 in your browser")
    else:
        print("\n[WARNING] Setup completed with some issues. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
