"""
customers.py - Customer API Routes

Handles all CRUD operations for customers:
- POST   /customers       -> Create a new customer
- GET    /customers       -> List all customers
- GET    /customers/{id}  -> Get a single customer
- PUT    /customers/{id}  -> Update a customer
- DELETE /customers/{id}  -> Delete a customer
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

# Create a router with a prefix and tag for Swagger docs
router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer.
    
    - Checks if email already exists
    - If email is unique, creates the customer
    """
    # Check if a customer with this email already exists
    existing = db.query(Customer).filter(Customer.email == customer_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A customer with this email already exists")

    # Create new customer from the request data
    new_customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        phone=customer_data.phone,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/", response_model=List[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    """Get a list of all customers."""
    customers = db.query(Customer).order_by(Customer.id).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a single customer by their ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer_data: CustomerUpdate, db: Session = Depends(get_db)):
    """
    Update an existing customer.
    
    - Only updates fields that are provided (not None)
    - Checks email uniqueness if email is being changed
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # If email is being changed, check it doesn't conflict
    if customer_data.email is not None and customer_data.email != customer.email:
        existing = db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="A customer with this email already exists")

    # Update only the fields that were provided
    update_fields = customer_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=200)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer by their ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
