"""
E-commerce AI Agent - Flask Application Configuration
====================================================

This module sets up the Flask application with PostgreSQL database configuration,
SQLAlchemy ORM, and initializes the database tables for the AI-powered e-commerce
data analysis system.

Features:
- PostgreSQL database integration
- Real-time streaming responses
- AI-powered natural language to SQL conversion
- Interactive data visualizations
- Production-ready configuration

Author: AI Agent
Date: July 2025
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for development and debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models using DeclarativeBase.
    This provides the foundation for all database models with modern SQLAlchemy 2.0 syntax.
    """
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models so their tables are created
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Import and register routes
    from routes import *  # noqa: F401,F403
    
    # Load sample data if tables are empty
    from data_loader import load_sample_data
    load_sample_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
