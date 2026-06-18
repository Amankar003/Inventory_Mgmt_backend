"""
product.py - Product Database Model

Defines the products table in the database.
Each product has a unique SKU and tracks stock quantity.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Product(Base):
    """
    Product model representing the 'products' table.
    
    Columns:
        id: Primary key, auto-incremented
        name: Product name
        sku: Stock Keeping Unit, must be unique
        price: Product price
        stock_quantity: How many units are in stock
        created_at: When the product was added
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship: A product can appear in many order items
    order_items = relationship("OrderItem", back_populates="product")
