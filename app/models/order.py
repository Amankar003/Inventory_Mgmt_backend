"""
order.py - Order and OrderItem Database Models

Defines the orders and order_items tables.
An order belongs to a customer and contains multiple order items.
Each order item references a product.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Order(Base):
    """
    Order model representing the 'orders' table.
    
    Columns:
        id: Primary key, auto-incremented
        customer_id: Foreign key to customers table
        total_amount: Total cost of all items in the order
        created_at: When the order was placed
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    OrderItem model representing the 'order_items' table.
    
    Each row is one line item in an order.
    
    Columns:
        id: Primary key, auto-incremented
        order_id: Foreign key to orders table
        product_id: Foreign key to products table
        quantity: How many units of this product
        unit_price: Price per unit at the time of order
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
