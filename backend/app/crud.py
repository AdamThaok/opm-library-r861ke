import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Member, Book, Loan, Reservation, Fine, BookStatus, LoanStatus, ReservationStatus, FineStatus
from .schemas import MemberCreate, BookCreate, LoanCreateRequest, ReservationCreateRequest, FineCreateRequest
from .exceptions import NotFoundException, ConflictException

# --- Generic CRUD Operations --- #

async def get_all_items(db: AsyncSession, model, skip: int = 0, limit: int = 100, options=None):
    stmt = select(model).offset(skip).limit(limit)
    if options:
        stmt = stmt.options(*options)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_item_by_id(db: AsyncSession, model, item_id: uuid.UUID, options=None):
    stmt = select(model).filter(model.id == item_id)
    if options:
        stmt = stmt.options(*options)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundException(detail=f"{model.__name__} not found")
    return item

async def create_item(db: AsyncSession, model, item_in):
    db_item = model(**item_in.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

# --- Member Operations (O1) --- #

async def get_members(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Member]:
    return await get_all_items(db, Member, skip=skip, limit=limit)

async def get_member(db: AsyncSession, member_id: uuid.UUID) -> Member:
    return await get_item_by_id(db, Member, member_id)

async def create_member(db: AsyncSession, member_in: MemberCreate) -> Member:
    existing_member = await db.execute(select(Member).filter_by(email=member_in.email))
    if existing_member.scalar_one_or_none():
        raise ConflictException(detail=f"Member with email {member_in.email} already exists")
    db_member = Member(id=uuid.uuid4(), **member_in.model_dump())
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)
    return db_member

# --- Book Operations (O2) --- #

async def get_books(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Book]:
    return await get_all_items(db, Book, skip=skip, limit=limit)

async def get_book(db: AsyncSession, book_id: uuid.UUID) -> Book:
    return await get_item_by_id(db, Book, book_id)

async def create_book(db: AsyncSession, book_in: BookCreate) -> Book:
    existing_book = await db.execute(select(Book).filter_by(isbn=book_in.isbn))
    if existing_book.scalar_one_or_none():
        raise ConflictException(detail=f"Book with ISBN {book_in.isbn} already exists")
    db_book = Book(id=uuid.uuid4(), **book_in.model_dump())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

# --- Loan Operations (O3) --- #

async def get_loans(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Loan]:
    return await get_all_items(db, Loan, skip=skip, limit=limit, options=[selectinload(Loan.member), selectinload(Loan.book)])

async def get_loan(db: AsyncSession, loan_id: uuid.UUID) -> Loan:
    return await get_item_by_id(db, Loan, loan_id, options=[selectinload(Loan.member), selectinload(Loan.book)])

# P1 - Borrow Book
async def create_loan(db: AsyncSession, loan_in: LoanCreateRequest) -> Loan:
    member = await get_item_by_id(db, Member, loan_in.member_id)
    book = await get_item_by_id(db, Book, loan_in.book_id)

    # BR1: Book.Available -> Book.Borrowed only via P1
    if book.status != BookStatus.Available:
        raise ConflictException(detail=f"Book '{book.title}' is not available for borrowing. Current status: {book.status.value}")

    # Check if the book is already actively borrowed by this member
    existing_loan = await db.execute(
        select(Loan).filter_by(member_id=loan_in.member_id, book_id=loan_in.book_id, status=LoanStatus.Active)
    )
    if existing_loan.scalar_one_or_none():
        raise ConflictException(detail=f"Member '{member.name}' already has an active loan for '{book.title}'")

    # ISO 19450 §7.3.1 State Transition: Atomic transaction
    async with db.begin():
        book.status = BookStatus.Borrowed
        db.add(book)

        due_date = datetime.now() + timedelta(days=14)
        db_loan = Loan(
            id=uuid.uuid4(),
            member_id=loan_in.member_id,
            book_id=loan_in.book_id,
            loan_date=datetime.now(),
            due_date=due_date,
            status=LoanStatus.Active
        )
        db.add(db_loan)
        await db.flush()
        await db.refresh(db_loan, attribute_names=["member", "book"])
        return db_loan

# P2 - Return Book
async def return_loan(db: AsyncSession, loan_id: uuid.UUID) -> Loan:
    loan = await get_item_by_id(db, Loan, loan_id, options=[selectinload(Loan.book)])

    # BR2: Loan.Active -> Loan.Returned only via P2
    if loan.status != LoanStatus.Active:
        raise ConflictException(detail=f"Loan is not active. Current status: {loan.status.value}")

    # ISO 19450 §7.3.1 State Transition: Atomic transaction
    async with db.begin():
        loan.status = LoanStatus.Returned
        loan.return_date = datetime.now()
        db.add(loan)

        # BR3: Book.Borrowed -> Book.Available only via P2
        if loan.book.status == BookStatus.Borrowed:
            loan.book.status = BookStatus.Available
            db.add(loan.book)
        # If book was Reserved, it might go back to Reserved for the next person
        # For simplicity, we assume it goes to Available if it was Borrowed.
        # More complex logic would involve checking reservations.

        await db.flush()
        await db.refresh(loan, attribute_names=["member", "book"])
        return loan

# --- Reservation Operations (O4) --- #

async def get_reservations(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Reservation]:
    return await get_all_items(db, Reservation, skip=skip, limit=limit, options=[selectinload(Reservation.member), selectinload(Reservation.book)])

async def get_reservation(db: AsyncSession, reservation_id: uuid.UUID) -> Reservation:
    return await get_item_by_id(db, Reservation, reservation_id, options=[selectinload(Reservation.member), selectinload(Reservation.book)])

# P3 - Reserve Book
async def create_reservation(db: AsyncSession, reservation_in: ReservationCreateRequest) -> Reservation:
    member = await get_item_by_id(db, Member, reservation_in.member_id)
    book = await get_item_by_id(db, Book, reservation_in.book_id)

    # BR4: Book.Available -> Book.Reserved only via P3
    if book.status != BookStatus.Available:
        raise ConflictException(detail=f"Book '{book.title}' is not available for reservation. Current status: {book.status.value}")

    # Check if the member already has a pending reservation for this book
    existing_reservation = await db.execute(
        select(Reservation).filter_by(member_id=reservation_in.member_id, book_id=reservation_in.book_id, status=ReservationStatus.Pending)
    )
    if existing_reservation.scalar_one_or_none():
        raise ConflictException(detail=f"Member '{member.name}' already has a pending reservation for '{book.title}'")

    # ISO 19450 §7.3.1 State Transition: Atomic transaction
    async with db.begin():
        book.status = BookStatus.Reserved
        db.add(book)

        db_reservation = Reservation(
            id=uuid.uuid4(),
            member_id=reservation_in.member_id,
            book_id=reservation_in.book_id,
            reservation_date=datetime.now(),
            status=ReservationStatus.Pending
        )
        db.add(db_reservation)
        await db.flush()
        await db.refresh(db_reservation, attribute_names=["member", "book"])
        return db_reservation

# P4 - Cancel Reservation
async def cancel_reservation(db: AsyncSession, reservation_id: uuid.UUID) -> Reservation:
    reservation = await get_item_by_id(db, Reservation, reservation_id, options=[selectinload(Reservation.book)])

    # BR5: Reservation.Pending -> Reservation.Cancelled only via P4
    if reservation.status != ReservationStatus.Pending:
        raise ConflictException(detail=f"Reservation is not pending. Current status: {reservation.status.value}")

    # ISO 19450 §7.3.1 State Transition: Atomic transaction
    async with db.begin():
        reservation.status = ReservationStatus.Cancelled
        db.add(reservation)

        # If the associated book is still Reserved by this specific reservation, make it Available
        # This check ensures we don't change the status if the book was already borrowed by someone else
        if reservation.book.status == BookStatus.Reserved:
            # Check if there are other active reservations for this book
            other_pending_reservations = await db.execute(
                select(Reservation).filter(
                    Reservation.book_id == reservation.book_id,
                    Reservation.status == ReservationStatus.Pending,
                    Reservation.id != reservation.id
                )
            )
            if not other_pending_reservations.scalar_one_or_none():
                # No other pending reservations, so set book to Available
                reservation.book.status = BookStatus.Available
                db.add(reservation.book)

        await db.flush()
        await db.refresh(reservation, attribute_names=["member", "book"])
        return reservation

# --- Fine Operations (O5) --- #

async def get_fines(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Fine]:
    return await get_all_items(db, Fine, skip=skip, limit=limit, options=[selectinload(Fine.member), selectinload(Fine.loan).selectinload(Loan.book)])

async def get_fine(db: AsyncSession, fine_id: uuid.UUID) -> Fine:
    return await get_item_by_id(db, Fine, fine_id, options=[selectinload(Fine.member), selectinload(Fine.loan).selectinload(Loan.book)])

# P5 - Issue Fine
async def create_fine(db: AsyncSession, fine_in: FineCreateRequest) -> Fine:
    await get_item_by_id(db, Member, fine_in.member_id) # Ensure member exists
    if fine_in.loan_id:
        await get_item_by_id(db, Loan, fine_in.loan_id) # Ensure loan exists if provided

    db_fine = Fine(id=uuid.uuid4(), **fine_in.model_dump())
    db.add(db_fine)
    await db.commit()
    await db.refresh(db_fine, attribute_names=["member", "loan"])
    return db_fine

# P6 - Pay Fine
async def pay_fine(db: AsyncSession, fine_id: uuid.UUID) -> Fine:
    fine = await get_item_by_id(db, Fine, fine_id)

    # BR6: Fine.Unpaid -> Fine.Paid only via P6
    if fine.status != FineStatus.Unpaid:
        raise ConflictException(detail=f"Fine is not unpaid. Current status: {fine.status.value}")

    # ISO 19450 §7.3.1 State Transition: Atomic transaction
    async with db.begin():
        fine.status = FineStatus.Paid
        db.add(fine)
        await db.flush()
        await db.refresh(fine, attribute_names=["member", "loan"])
        return fine
