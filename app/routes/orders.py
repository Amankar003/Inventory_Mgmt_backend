from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def place_order(data: OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Validate stock and collect line items
    cart = []
    total = 0.0

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'. "
                       f"Available: {product.stock_quantity}, Requested: {item.quantity}"
            )

        line_total = item.quantity * product.price
        total += line_total
        cart.append({"product": product, "quantity": item.quantity, "unit_price": product.price})

    # Persist order + items, deduct stock in one transaction
    order = Order(customer_id=data.customer_id, total_amount=round(total, 2))
    db.add(order)
    db.flush()

    for entry in cart:
        db.add(OrderItem(
            order_id=order.id,
            product_id=entry["product"].id,
            quantity=entry["quantity"],
            unit_price=entry["unit_price"],
        ))
        entry["product"].stock_quantity -= entry["quantity"]

    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
