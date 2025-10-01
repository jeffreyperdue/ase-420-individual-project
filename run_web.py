#!/usr/bin/env python3
"""
StressSpec Web UI Development Server

This script starts the development server for the web UI.
It includes hot reload, debugging, and development-specific configurations.

BEGINNER NOTES:
- This script starts the web server for development
- It includes automatic reloading when code changes
- It sets up debugging and development-friendly settings
- Use this for local development and testing
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the development server."""
    print("Starting StressSpec Web UI Development Server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("[ERROR] requirements.txt not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if web directory exists
    if not Path("web").exists():
        print("[ERROR] web directory not found")
        print("Please run setup_web.py first to create the web structure")
        sys.exit(1)
    
    # Set development environment variables
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("RELOAD", "True")
    
    print("Development settings:")
    print(f"  - Debug mode: {os.environ.get('DEBUG', 'True')}")
    print(f"  - Hot reload: {os.environ.get('RELOAD', 'True')}")
    print(f"  - Host: 127.0.0.1")
    print(f"  - Port: 8000")
    print()
    print("Server will be available at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the server
        uvicorn.run(
            "web.main:app",  # Path to the FastAPI app
            host="127.0.0.1",
            port=8000,
            reload=True,  # Enable hot reload
            reload_dirs=["web"],  # Watch web directory for changes
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
