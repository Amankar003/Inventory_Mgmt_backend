"""
order.py - Order Pydantic Schemas

These schemas handle request validation and response serialization for orders.
The OrderCreate schema accepts a customer_id and a list of items.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class OrderItemCreate(BaseModel):
    """Schema for a single item in an order creation request."""
    product_id: int = Field(..., description="ID of the product to order")
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")


class OrderCreate(BaseModel):
    """
    Schema for creating a new order (request body).
    
    Example:
    {
        "customer_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 1}
        ]
    }
    """
    customer_id: int = Field(..., description="ID of the customer placing the order")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="At least one item required")


class OrderItemResponse(BaseModel):
    """Schema for returning order item data in API responses."""
    id: int
    product_id: int
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Schema for returning order data in API responses."""
    id: int
    customer_id: int
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = {"from_attributes": True}
