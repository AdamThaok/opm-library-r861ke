import uuid
from datetime import datetime
from decimal import Decimal
import enum

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class BookStatus(enum.Enum):
    Available = "Available"
    Borrowed = "Borrowed"
    Reserved = "Reserved"
    Lost = "Lost"

class LoanStatus(enum.Enum):
    Active = "Active"
    Returned = "Returned"
    Overdue = "Overdue"

class ReservationStatus(enum.Enum):
    Pending = "Pending"
    Fulfilled = "Fulfilled"
    Cancelled = "Cancelled"

class FineStatus(enum.Enum):
    Unpaid = "Unpaid"
    Paid = "Paid"

class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class Member(Base, TimestampMixin):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    loans = relationship("Loan", back_populates="member")
    reservations = relationship("Reservation", back_populates="member")
    fines = relationship("Fine", back_populates="member")

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}')>"

class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    status = Column(Enum(BookStatus), default=BookStatus.Available, nullable=False)

    loans = relationship("Loan", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', status='{self.status.value}')>"

class Loan(Base, TimestampMixin):
    __tablename__ = "loans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    loan_date = Column(DateTime, server_default=func.now(), nullable=False)
    return_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.Active, nullable=False)

    member = relationship("Member", back_populates="loans")
    book = relationship("Book", back_populates="loans")
    fines = relationship("Fine", back_populates="loan")

    def __repr__(self):
        return f"<Loan(id={self.id}, member_id={self.member_id}, book_id={self.book_id}, status='{self.status.value}')>"

class Reservation(Base, TimestampMixin):
    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    reservation_date = Column(DateTime, server_default=func.now(), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.Pending, nullable=False)

    member = relationship("Member", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(id={self.id}, member_id={self.member_id}, book_id={self.book_id}, status='{self.status.value}')>"

class Fine(Base, TimestampMixin):
    __tablename__ = "fines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(Enum(FineStatus), default=FineStatus.Unpaid, nullable=False)

    member = relationship("Member", back_populates="fines")
    loan = relationship("Loan", back_populates="fines")

    def __repr__(self):
        return f"<Fine(id={self.id}, member_id={self.member_id}, amount={self.amount}, status='{self.status.value}')>"
