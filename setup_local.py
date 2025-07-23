import os
from dotenv import load_dotenv
load_dotenv() 
from sqlalchemy import text
from models import ProductEligibility, AdSalesMetrics, TotalSalesMetrics
from app import db
def load_env():
    print(" Loaded .env file")
    load_dotenv()

def test_environment_variables():
    print(" Checking environment variables...")
    required_vars = ["DATABASE_URL"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise Exception(f"Missing environment variables: {', '.join(missing)}")
    print(" All environment variables are set")

def test_database_connection():
    """Test database connection"""
    print("\n Testing database connection...")

    try:
        from app import app, db

        with app.app_context():
            #  Use connect() and text() for SQLAlchemy 2.x compatibility
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(" Database connection successful")
            return True
    except Exception as e:
        print(f" Database connection failed: {e}")
        print("\n Make sure:")
        print("   - PostgreSQL is running")
        print("   - DATABASE_URL is correct")
        print("   - Database exists and is accessible")
        return False

def load_datasets():
    print("Loading real datasets...")

    from app.routes.load_csv import (
        load_product_eligibility_data,
        load_ad_sales_data,
        load_total_sales_data,
    )

    pe_count = load_product_eligibility_data()
    ad_count = load_ad_sales_data()
    total_count = load_total_sales_data()

    total = pe_count + ad_count + total_count
    print(f" Successfully loaded your complete datasets:")
    print(f"   • {pe_count:,} Product Eligibility records")
    print(f"   • {ad_count:,} Ad Sales Metrics records")
    print(f"   • {total_count:,} Total Sales Metrics records")
    print(f"   • Total: {total:,} records")

def check_if_data_exists():
    print("\n Checking if data needs to be loaded...")
    from app.models import ProductEligibility
    from app import app, db

    with app.app_context():
        count = db.session.query(ProductEligibility).count()
        if count > 0:
            print(f" Found {count:,} records - data already loaded")
            return True
    return False

def test_local_llm():
    print("\n Testing local LLM connection...")
    import logging
    logging.basicConfig(level=logging.DEBUG)

    try:
        from app.utils.query_llm import query_llm
        _ = query_llm("Show me sales last month")
        print(" Local LLM connection successful")
    except Exception as e:
        print(f" Local LLM error: {e}")

def main():
    load_env()
    test_environment_variables()

    if test_database_connection():
        if not check_if_data_exists():
            load_datasets()

    test_local_llm()

if __name__ == "__main__":
    main()
