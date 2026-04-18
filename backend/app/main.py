import os
import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from . import crud, schemas
from .exceptions import NotFoundException, ConflictException

app = FastAPI(
    title="Library Management System API",
    description="API for managing library members, books, loans, reservations, and fines."
)

# CORS Configuration
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

# --- Startup Events --- #
@app.on_event("startup")
async def startup_event():
    # In Railway/Docker Compose, db_init.py and seed.py are run by wait-for-db.sh
    # For local development without docker-compose, you might run them manually or via a script.
    print("FastAPI application starting up.")
    print(f"CORS allowed origin: {FRONTEND_ORIGIN}")

# --- Root Endpoint --- #
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Library Management System API!"}

# --- Member Endpoints (O1) --- #
@app.post("/members/", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED, tags=["Members"])
async def create_member(member: schemas.MemberCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_member(db=db, member_in=member)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)

@app.get("/members/", response_model=List[schemas.MemberResponse], tags=["Members"])
async def read_members(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    members = await crud.get_members(db, skip=skip, limit=limit)
    return members

@app.get("/members/{member_id}", response_model=schemas.MemberResponse, tags=["Members"])
async def read_member(member_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        member = await crud.get_member(db, member_id=member_id)
        return member
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

# --- Book Endpoints (O2) --- #
@app.post("/books/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(book: schemas.BookCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_book(db=db, book_in=book)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)

@app.get("/books/", response_model=List[schemas.BookResponse], tags=["Books"])
async def read_books(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    books = await crud.get_books(db, skip=skip, limit=limit)
    return books

@app.get("/books/{book_id}", response_model=schemas.BookResponse, tags=["Books"])
async def read_book(book_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        book = await crud.get_book(db, book_id=book_id)
        return book
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

# --- Loan Endpoints (O3) --- #
# P1 - Borrow Book
@app.post("/loans/", response_model=schemas.LoanResponse, status_code=status.HTTP_201_CREATED, tags=["Loans"])
async def borrow_book(loan_request: schemas.LoanCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_loan(db=db, loan_in=loan_request)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@app.get("/loans/", response_model=List[schemas.LoanResponse], tags=["Loans"])
async def read_loans(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    loans = await crud.get_loans(db, skip=skip, limit=limit)
    return loans

@app.get("/loans/{loan_id}", response_model=schemas.LoanResponse, tags=["Loans"])
async def read_loan(loan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        loan = await crud.get_loan(db, loan_id=loan_id)
        return loan
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

# P2 - Return Book
@app.post("/loans/{loan_id}/return", response_model=schemas.LoanResponse, tags=["Loans"])
async def return_book(loan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.return_loan(db=db, loan_id=loan_id)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

# --- Reservation Endpoints (O4) --- #
# P3 - Reserve Book
@app.post("/reservations/", response_model=schemas.ReservationResponse, status_code=status.HTTP_201_CREATED, tags=["Reservations"])
async def reserve_book(reservation_request: schemas.ReservationCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_reservation(db=db, reservation_in=reservation_request)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@app.get("/reservations/", response_model=List[schemas.ReservationResponse], tags=["Reservations"])
async def read_reservations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    reservations = await crud.get_reservations(db, skip=skip, limit=limit)
    return reservations

@app.get("/reservations/{reservation_id}", response_model=schemas.ReservationResponse, tags=["Reservations"])
async def read_reservation(reservation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        reservation = await crud.get_reservation(db, reservation_id=reservation_id)
        return reservation
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

# P4 - Cancel Reservation
@app.post("/reservations/{reservation_id}/cancel", response_model=schemas.ReservationResponse, tags=["Reservations"])
async def cancel_reservation(reservation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.cancel_reservation(db=db, reservation_id=reservation_id)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

# --- Fine Endpoints (O5) --- #
# P5 - Issue Fine
@app.post("/fines/", response_model=schemas.FineResponse, status_code=status.HTTP_201_CREATED, tags=["Fines"])
async def issue_fine(fine_request: schemas.FineCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_fine(db=db, fine_in=fine_request)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@app.get("/fines/", response_model=List[schemas.FineResponse], tags=["Fines"])
async def read_fines(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    fines = await crud.get_fines(db, skip=skip, limit=limit)
    return fines

@app.get("/fines/{fine_id}", response_model=schemas.FineResponse, tags=["Fines"])
async def read_fine(fine_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        fine = await crud.get_fine(db, fine_id=fine_id)
        return fine
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

# P6 - Pay Fine
@app.post("/fines/{fine_id}/pay", response_model=schemas.FineResponse, tags=["Fines"])
async def pay_fine(fine_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.pay_fine(db=db, fine_id=fine_id)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
