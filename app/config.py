"""
config.py - Application Configuration

Loads settings from environment variables.
We use python-dotenv to read from a .env file during local development.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Database connection URL
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/inventory_db")
