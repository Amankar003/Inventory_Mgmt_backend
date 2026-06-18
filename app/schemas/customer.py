"""
customer.py - Customer Pydantic Schemas

These schemas handle request validation and response serialization for customers.
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class CustomerCreate(BaseModel):
    """Schema for creating a new customer (request body)."""
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    email: str = Field(..., min_length=1, max_length=255, description="Customer email, must be unique")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")


class CustomerUpdate(BaseModel):
    """Schema for updating a customer (request body). All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class CustomerResponse(BaseModel):
    """Schema for returning customer data in API responses."""
    id: int
    name: str
    email: str
    phone: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
