import logging
from datetime import datetime, date
from app import db
from models import ProductEligibility, AdSalesMetrics, TotalSalesMetrics

def load_sample_data():
    """Load real datasets if tables are empty"""
    
    try:
        # Check if data already exists
        existing_count = ProductEligibility.query.count()
        if existing_count > 0:
            logging.info(f"Found {existing_count} existing records, skipping data load...")
            return
        
        # Load the real datasets
        from load_datasets import load_real_datasets
        load_real_datasets()
        
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        db.session.rollback()
