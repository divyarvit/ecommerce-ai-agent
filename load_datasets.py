import pandas as pd
import logging
from datetime import datetime
from app import app, db
from models import ProductEligibility, AdSalesMetrics, TotalSalesMetrics

def load_real_datasets():
    """Load the actual provided datasets"""
    
    with app.app_context():
        try:
            # Clear existing data
            ProductEligibility.query.delete()
            AdSalesMetrics.query.delete()
            TotalSalesMetrics.query.delete()
            
            print("Loading real datasets...")
            
            # Load Product Eligibility Data
            eligibility_file = 'attached_assets/Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped)_1753217281657.csv'
            eligibility_df = pd.read_csv(eligibility_file)
            
            for _, row in eligibility_df.iterrows():
                record = ProductEligibility(
                    eligibility_datetime_utc=pd.to_datetime(row['eligibility_datetime_utc']),
                    item_id=int(row['item_id']),
                    eligibility=str(row['eligibility']).upper() == 'TRUE',
                    message=row['message'] if pd.notna(row['message']) and row['message'].strip() else None
                )
                db.session.add(record)
            
            print(f" Loaded {len(eligibility_df)} eligibility records")
            
            # Load Ad Sales Metrics
            ad_sales_file = 'attached_assets/Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped)_1753217281656.csv'
            ad_sales_df = pd.read_csv(ad_sales_file)
            
            for _, row in ad_sales_df.iterrows():
                record = AdSalesMetrics(
                    date=pd.to_datetime(row['date']).date(),
                    item_id=int(row['item_id']),
                    ad_sales=float(row['ad_sales']) if pd.notna(row['ad_sales']) else 0,
                    impressions=int(row['impressions']) if pd.notna(row['impressions']) else 0,
                    ad_spend=float(row['ad_spend']) if pd.notna(row['ad_spend']) else 0,
                    clicks=int(row['clicks']) if pd.notna(row['clicks']) else 0,
                    units_sold=int(row['units_sold']) if pd.notna(row['units_sold']) else 0
                )
                db.session.add(record)
            
            print(f" Loaded {len(ad_sales_df)} ad sales records")
            
            # Load Total Sales Metrics
            total_sales_file = 'attached_assets/Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped)_1753217281658.csv'
            total_sales_df = pd.read_csv(total_sales_file)
            
            for _, row in total_sales_df.iterrows():
                record = TotalSalesMetrics(
                    date=pd.to_datetime(row['date']).date(),
                    item_id=int(row['item_id']),
                    total_sales=float(row['total_sales']) if pd.notna(row['total_sales']) else 0,
                    total_units_ordered=int(row['total_units_ordered']) if pd.notna(row['total_units_ordered']) else 0
                )
                db.session.add(record)
            
            print(f" Loaded {len(total_sales_df)} total sales records")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n Successfully loaded your complete datasets:")
            print(f"   • {len(eligibility_df):,} Product Eligibility records")
            print(f"   • {len(ad_sales_df):,} Ad Sales Metrics records") 
            print(f"   • {len(total_sales_df):,} Total Sales Metrics records")
            print(f"   • Total: {len(eligibility_df) + len(ad_sales_df) + len(total_sales_df):,} records")
            
        except Exception as e:
            logging.error(f"Error loading datasets: {e}")
            db.session.rollback()
            print(f" Error: {e}")

if __name__ == "__main__":
    load_real_datasets()