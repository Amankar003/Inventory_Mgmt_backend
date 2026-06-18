"""
main.py - FastAPI Application Entry Point

This is the main file that:
1. Creates the FastAPI app
2. Sets up CORS (so the React frontend can talk to the backend)
3. Includes all the route modules
4. Creates database tables on startup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Import all models so SQLAlchemy knows about them when creating tables
from app.models import Product, Customer, Order, OrderItem

# Import route modules
from app.routes import products, customers, orders

# Create the FastAPI application
app = FastAPI(
    title="Inventory & Order Management System",
    description="A simple API to manage products, customers, and orders",
    version="1.0.0",
)

# Set up CORS middleware
# This allows the React frontend to make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the route modules
# Each router adds its endpoints to the app
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.on_event("startup")
def startup():
    """
    Runs when the application starts.
    Creates all database tables if they don't exist yet.
    """
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Inventory & Order Management System is running"}
