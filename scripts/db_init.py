import os
from sqlalchemy import create_engine
from backend.app.database import Base
from backend.app.models import *

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    exit(1)

print(f"Initializing database schema for: {DATABASE_URL.split('@')[-1]}")

# Use a synchronous engine for schema creation
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))

try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")

