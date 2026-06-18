"""
orders.py - Order API Routes

Handles order operations:
- POST /orders       -> Create a new order (with stock validation)
- GET  /orders       -> List all orders
- GET  /orders/{id}  -> Get a single order with its items

Order creation logic:
1. Verify customer exists
2. For each item, verify product exists and has enough stock
3. Create the order and order items
4. Reduce stock for each product
5. Commit everything in one transaction
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse

# Create a router with a prefix and tag for Swagger docs
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    
    Steps:
    1. Check if the customer exists
    2. Check if each product exists and has sufficient stock
    3. Calculate total amount
    4. Create the order and order items
    5. Decrease stock quantities
    6. Commit the transaction
    """

    # Step 1: Check if customer exists
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Step 2: Validate each item — check product exists and stock is sufficient
    # We also collect product data to avoid querying again later
    validated_items = []
    total_amount = 0.0

    for item in order_data.items:
        # Check if product exists
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {item.product_id} not found"
            )

        # Check if there is enough stock
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'. "
                       f"Available: {product.stock_quantity}, Requested: {item.quantity}"
            )

        # Calculate the line total (quantity * unit price)
        line_total = item.quantity * product.price
        total_amount += line_total

        # Save the validated data for later use
        validated_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price,
        })

    # Step 3: Create the order
    new_order = Order(
        customer_id=order_data.customer_id,
        total_amount=round(total_amount, 2),
    )
    db.add(new_order)
    db.flush()  # Flush to get the order ID without committing yet

    # Step 4: Create order items and reduce stock
    for validated in validated_items:
        # Create the order item
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=validated["product"].id,
            quantity=validated["quantity"],
            unit_price=validated["unit_price"],
        )
        db.add(order_item)

        # Reduce stock quantity
        validated["product"].stock_quantity -= validated["quantity"]

    # Step 5: Commit everything in one transaction
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    """Get a list of all orders with their items."""
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single order by its ID, including all order items."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
