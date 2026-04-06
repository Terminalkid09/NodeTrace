#!/usr/bin/env python
"""Run the FastAPI server with proper path configuration."""
import os
import sys

# Change to the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Add the backend directory to Python path
sys.path.insert(0, backend_dir)

# Skip database creation for testing
os.environ['SKIP_DB_CREATE'] = 'true'

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
