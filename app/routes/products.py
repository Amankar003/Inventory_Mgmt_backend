"""
products.py - Product API Routes

Handles all CRUD operations for products:
- POST   /products       -> Create a new product
- GET    /products       -> List all products
- GET    /products/{id}  -> Get a single product
- PUT    /products/{id}  -> Update a product
- DELETE /products/{id}  -> Delete a product
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

# Create a router with a prefix and tag for Swagger docs
router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    
    - Checks if SKU already exists
    - If SKU is unique, creates the product
    """
    # Check if a product with this SKU already exists
    existing = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="A product with this SKU already exists")

    # Create new product from the request data
    new_product = Product(
        name=product_data.name,
        sku=product_data.sku,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)  # Refresh to get the auto-generated id and created_at
    return new_product


@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Get a list of all products."""
    products = db.query(Product).order_by(Product.id).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by its ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    """
    Update an existing product.
    
    - Only updates fields that are provided (not None)
    - Checks SKU uniqueness if SKU is being changed
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # If SKU is being changed, check it doesn't conflict with another product
    if product_data.sku is not None and product_data.sku != product.sku:
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="A product with this SKU already exists")

    # Update only the fields that were provided
    update_fields = product_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=200)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by its ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
