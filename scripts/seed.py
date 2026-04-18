import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from backend.app.models import Member, Book, Loan, Reservation, Fine, BookStatus, LoanStatus, ReservationStatus, FineStatus

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    exit(1)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("Seeding database with sample data...")

        # Members
        member_data = [
            {"name": "Alice Smith", "email": "alice@example.com"},
            {"name": "Bob Johnson", "email": "bob@example.com"},
            {"name": "Charlie Brown", "email": "charlie@example.com"},
        ]
        members = []
        for data in member_data:
            stmt = select(Member).filter_by(email=data["email"])
            existing_member = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_member:
                member = Member(id=uuid.uuid4(), **data)
                db.add(member)
                members.append(member)
                print(f"Added member: {member.name}")
            else:
                members.append(existing_member)
                print(f"Member already exists: {existing_member.name}")
        await db.flush() # Ensure IDs are available for relationships

        alice = next((m for m in members if m.email == "alice@example.com"), None)
        bob = next((m for m in members if m.email == "bob@example.com"), None)
        charlie = next((m for m in members if m.email == "charlie@example.com"), None)

        # Books
        book_data = [
            {"title": "The Great Adventure", "author": "A. Author", "isbn": "978-0123456789", "status": BookStatus.Available},
            {"title": "Mystery of the Old House", "author": "B. Writer", "isbn": "978-1234567890", "status": BookStatus.Borrowed},
            {"title": "Coding for Dummies", "author": "C. Programmer", "isbn": "978-2345678901", "status": BookStatus.Reserved},
            {"title": "Lost in Space", "author": "D. Explorer", "isbn": "978-3456789012", "status": BookStatus.Available},
        ]
        books = []
        for data in book_data:
            stmt = select(Book).filter_by(isbn=data["isbn"])
            existing_book = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_book:
                book = Book(id=uuid.uuid4(), **data)
                db.add(book)
                books.append(book)
                print(f"Added book: {book.title}")
            else:
                books.append(existing_book)
                print(f"Book already exists: {existing_book.title}")
        await db.flush()

        great_adventure = next((b for b in books if b.isbn == "978-0123456789"), None)
        mystery_house = next((b for b in books if b.isbn == "978-1234567890"), None)
        coding_dummies = next((b for b in books if b.isbn == "978-2345678901"), None)
        lost_in_space = next((b for b in books if b.isbn == "978-3456789012"), None)

        # Loans
        if alice and mystery_house:
            stmt = select(Loan).filter_by(member_id=alice.id, book_id=mystery_house.id, status=LoanStatus.Active)
            existing_loan = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_loan:
                loan = Loan(
                    id=uuid.uuid4(),
                    member_id=alice.id,
                    book_id=mystery_house.id,
                    loan_date=datetime.now() - timedelta(days=5),
                    due_date=datetime.now() + timedelta(days=9),
                    status=LoanStatus.Active
                )
                db.add(loan)
                print(f"Added active loan for {alice.name} - {mystery_house.title}")
            else:
                print(f"Active loan already exists for {alice.name} - {mystery_house.title}")

        if bob and coding_dummies:
            stmt = select(Loan).filter_by(member_id=bob.id, book_id=coding_dummies.id, status=LoanStatus.Returned)
            existing_returned_loan = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_returned_loan:
                returned_loan = Loan(
                    id=uuid.uuid4(),
                    member_id=bob.id,
                    book_id=coding_dummies.id,
                    loan_date=datetime.now() - timedelta(days=30),
                    return_date=datetime.now() - timedelta(days=15),
                    due_date=datetime.now() - timedelta(days=16),
                    status=LoanStatus.Returned
                )
                db.add(returned_loan)
                print(f"Added returned loan for {bob.name} - {coding_dummies.title}")
            else:
                print(f"Returned loan already exists for {bob.name} - {coding_dummies.title}")
        await db.flush()

        # Reservations
        if charlie and great_adventure:
            stmt = select(Reservation).filter_by(member_id=charlie.id, book_id=great_adventure.id, status=ReservationStatus.Pending)
            existing_reservation = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_reservation:
                reservation = Reservation(
                    id=uuid.uuid4(),
                    member_id=charlie.id,
                    book_id=great_adventure.id,
                    reservation_date=datetime.now() - timedelta(days=2),
                    status=ReservationStatus.Pending
                )
                db.add(reservation)
                print(f"Added pending reservation for {charlie.name} - {great_adventure.title}")
            else:
                print(f"Pending reservation already exists for {charlie.name} - {great_adventure.title}")

        if alice and lost_in_space:
            stmt = select(Reservation).filter_by(member_id=alice.id, book_id=lost_in_space.id, status=ReservationStatus.Cancelled)
            existing_cancelled_reservation = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_cancelled_reservation:
                cancelled_reservation = Reservation(
                    id=uuid.uuid4(),
                    member_id=alice.id,
                    book_id=lost_in_space.id,
                    reservation_date=datetime.now() - timedelta(days=10),
                    status=ReservationStatus.Cancelled
                )
                db.add(cancelled_reservation)
                print(f"Added cancelled reservation for {alice.name} - {lost_in_space.title}")
            else:
                print(f"Cancelled reservation already exists for {alice.name} - {lost_in_space.title}")
        await db.flush()

        # Fines
        # Assuming an overdue loan for Alice and Mystery of the Old House (created above)
        active_loan_alice_mystery = (await db.execute(select(Loan).filter_by(member_id=alice.id, book_id=mystery_house.id, status=LoanStatus.Active))).scalar_one_or_none()
        if alice and active_loan_alice_mystery:
            stmt = select(Fine).filter_by(member_id=alice.id, loan_id=active_loan_alice_mystery.id, status=FineStatus.Unpaid)
            existing_fine = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_fine:
                fine = Fine(
                    id=uuid.uuid4(),
                    member_id=alice.id,
                    loan_id=active_loan_alice_mystery.id,
                    amount=Decimal("5.00"),
                    reason="Overdue book",
                    status=FineStatus.Unpaid
                )
                db.add(fine)
                print(f"Added unpaid fine for {alice.name} on loan {active_loan_alice_mystery.id}")
            else:
                print(f"Unpaid fine already exists for {alice.name} on loan {active_loan_alice_mystery.id}")

        if bob:
            stmt = select(Fine).filter_by(member_id=bob.id, status=FineStatus.Paid)
            existing_paid_fine = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_paid_fine:
                paid_fine = Fine(
                    id=uuid.uuid4(),
                    member_id=bob.id,
                    loan_id=None, # Example of a fine not tied to a specific loan
                    amount=Decimal("10.00"),
                    reason="Damaged book cover",
                    status=FineStatus.Paid
                )
                db.add(paid_fine)
                print(f"Added paid fine for {bob.name}")
            else:
                print(f"Paid fine already exists for {bob.name}")

        await db.commit()
        print("Database seeding complete.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_data())
