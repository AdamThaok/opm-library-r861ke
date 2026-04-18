import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from .models import BookStatus, LoanStatus, ReservationStatus, FineStatus

# Base Schema for common fields
class BaseSchema(BaseModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # For SQLAlchemy ORM compatibility

# Member Schemas
class MemberCreate(BaseModel):
    name: str
    email: str

class MemberResponse(BaseSchema):
    name: str
    email: str

# Book Schemas
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    status: BookStatus = BookStatus.Available

class BookResponse(BaseSchema):
    title: str
    author: str
    isbn: str
    status: BookStatus

# Loan Schemas
class LoanCreateRequest(BaseModel):
    member_id: uuid.UUID
    book_id: uuid.UUID

class LoanResponse(BaseSchema):
    member_id: uuid.UUID
    book_id: uuid.UUID
    loan_date: datetime
    return_date: Optional[datetime] = None
    due_date: datetime
    status: LoanStatus
    member: MemberResponse # Nested schema
    book: BookResponse # Nested schema

# Reservation Schemas
class ReservationCreateRequest(BaseModel):
    member_id: uuid.UUID
    book_id: uuid.UUID

class ReservationResponse(BaseSchema):
    member_id: uuid.UUID
    book_id: uuid.UUID
    reservation_date: datetime
    status: ReservationStatus
    member: MemberResponse # Nested schema
    book: BookResponse # Nested schema

# Fine Schemas
class FineCreateRequest(BaseModel):
    member_id: uuid.UUID
    loan_id: Optional[uuid.UUID] = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    reason: str

class FineResponse(BaseSchema):
    member_id: uuid.UUID
    loan_id: Optional[uuid.UUID] = None
    amount: Decimal
    reason: str
    status: FineStatus
    member: MemberResponse # Nested schema
    loan: Optional[LoanResponse] = None # Nested schema, optional
