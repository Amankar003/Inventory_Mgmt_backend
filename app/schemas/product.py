"""
product.py - Product Pydantic Schemas

These schemas handle request validation and response serialization for products.
Pydantic automatically validates incoming data and raises errors if data is invalid.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    """Schema for creating a new product (request body)."""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    sku: str = Field(..., min_length=1, max_length=100, description="Unique Stock Keeping Unit")
    price: float = Field(..., gt=0, description="Product price, must be positive")
    stock_quantity: int = Field(..., ge=0, description="Stock quantity, cannot be negative")


class ProductUpdate(BaseModel):
    """Schema for updating a product (request body). All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    """Schema for returning product data in API responses."""
    id: int
    name: str
    sku: str
    price: float
    stock_quantity: int
    created_at: datetime

    # This tells Pydantic to read data from SQLAlchemy model attributes
    model_config = {"from_attributes": True}
