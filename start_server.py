#!/usr/bin/env python3
"""
Startup script for the Genomic VCF Processing Service.

This script provides an easy way to start the server with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path


def main():
    """Start the FastAPI server."""
    # Check if we're in the right directory
    if not Path("app/main.py").exists():
        print("ERROR: app/main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Load environment variables if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("INFO: Loaded environment variables from .env file")
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("Starting Genomic VCF Processing Service")
    print("=" * 50)
    print(f"    Host: {host}")
    print(f"    Port: {port}")
    print(f"    Debug: {debug}")
    print(f"    API Docs: http://{host}:{port}/docs")
    print("=" * 50)
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: Error starting server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
