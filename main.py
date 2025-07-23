"""
E-commerce AI Agent - Application Entry Point
============================================

This is the main entry point for the e-commerce AI agent application.
It imports the configured Flask app from app.py and starts the development server.

For production deployment, use gunicorn:
    gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

Author: AI Agent
Date: July 2025
"""

import os
from dotenv import load_dotenv

# Load environment variables first, before importing Flask app
load_dotenv()

from app import app

if __name__ == '__main__':
    # Start the development server
    # In production, this should be handled by gunicorn or similar WSGI server
    app.run(host='0.0.0.0', port=5000, debug=True)  # noqa: F401
