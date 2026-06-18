"""
database.py - Database Connection Setup

Creates the SQLAlchemy engine, session, and base class.
Provides a get_db() function that FastAPI routes use to get a database session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# Create the SQLAlchemy engine
# The engine manages the connection pool to the PostgreSQL database
engine = create_engine(DATABASE_URL)

# Create a session factory
# Each request will get its own session from this factory
# autocommit=False means we control when to commit
# autoflush=False means we control when to flush changes to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models
# All models will inherit from this class
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI.
    
    Creates a new database session for each request,
    and closes it when the request is done.
    
    Usage in routes:
        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
