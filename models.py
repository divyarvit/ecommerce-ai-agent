"""
E-commerce AI Agent - Database Models
====================================

This module defines the SQLAlchemy database models for the e-commerce AI agent.
Each model represents a table in the PostgreSQL database with appropriate
indexes for optimal query performance.

Models:
- ProductEligibility: Product advertising eligibility status and messages
- AdSalesMetrics: Advertising performance data (sales, clicks, impressions)
- TotalSalesMetrics: Overall sales performance metrics

Author: AI Agent
Date: July 2025
"""

from app import db
from sqlalchemy import DateTime, Integer, String, Boolean, Numeric, Date, Text
from sqlalchemy.sql import func

class ProductEligibility(db.Model):
    """
    Product Eligibility Model
    ========================
    
    Stores product advertising eligibility status with timestamps and reason messages.
    Used to track which products are eligible for advertising campaigns.
    
    Fields:
    - eligibility_datetime_utc: Timestamp when eligibility was determined
    - item_id: Unique product identifier (indexed for fast lookups)
    - eligibility: Boolean flag indicating if product is eligible
    - message: Optional text explaining eligibility status
    """
    __tablename__ = 'product_eligibility'
    
    id = db.Column(Integer, primary_key=True)
    eligibility_datetime_utc = db.Column(DateTime, nullable=False)
    item_id = db.Column(Integer, nullable=False, index=True)
    eligibility = db.Column(Boolean, nullable=False)
    message = db.Column(Text)
    
    def __repr__(self):
        return f'<ProductEligibility {self.item_id}: {self.eligibility}>'

class AdSalesMetrics(db.Model):
    """
    Ad Sales Metrics Model
    =====================
    
    Tracks advertising performance metrics for products on a daily basis.
    Contains all key advertising KPIs needed for performance analysis.
    
    Fields:
    - date: Date of the advertising data (indexed)
    - item_id: Product identifier (indexed)  
    - ad_sales: Revenue generated from advertising
    - impressions: Number of ad impressions
    - ad_spend: Amount spent on advertising
    - clicks: Number of ad clicks
    - units_sold: Units sold through advertising
    
    Common Calculations:
    - CPC (Cost Per Click): ad_spend / clicks
    - CTR (Click Through Rate): clicks / impressions
    - RoAS (Return on Ad Spend): ad_sales / ad_spend
    - Conversion Rate: units_sold / clicks
    """
    __tablename__ = 'ad_sales_metrics'
    
    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False, index=True)
    item_id = db.Column(Integer, nullable=False, index=True)
    ad_sales = db.Column(Numeric(10, 2), default=0)
    impressions = db.Column(Integer, default=0)
    ad_spend = db.Column(Numeric(10, 2), default=0)
    clicks = db.Column(Integer, default=0)
    units_sold = db.Column(Integer, default=0)
    
    def __repr__(self):
        return f'<AdSalesMetrics {self.item_id} on {self.date}>'

class TotalSalesMetrics(db.Model):
    """
    Total Sales Metrics Model
    ========================
    
    Stores overall sales performance data for products on a daily basis.
    Includes both organic and advertising-driven sales.
    
    Fields:
    - date: Date of the sales data (indexed)
    - item_id: Product identifier (indexed)
    - total_sales: Total revenue for the product
    - total_units_ordered: Total units sold
    
    Note: This includes all sales channels, not just advertising-driven sales
    """
    __tablename__ = 'total_sales_metrics'
    
    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False, index=True)
    item_id = db.Column(Integer, nullable=False, index=True)
    total_sales = db.Column(Numeric(10, 2), default=0)
    total_units_ordered = db.Column(Integer, default=0)
    
    def __repr__(self):
        return f'<TotalSalesMetrics {self.item_id} on {self.date}>'
