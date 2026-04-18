# OPM to Code Traceability Matrix

This document maps the OPM (Object-Process Methodology) IR and derived system specification elements to their corresponding implementations in the generated code, adhering to ISO 19450 rules.

## 1. Domain Model (Entities & Persistence)

**ISO 19450 §5.2 Informatical Objects:** All OPM Objects are persisted as rows in PostgreSQL tables via SQLAlchemy ORM models.

| OPM ID | OPM Object | Database Table | SQLAlchemy Model (`backend/app/models.py`) | Pydantic Schema (`backend/app/schemas.py`) | Notes |
|--------|------------|----------------|----------------------------------------------|--------------------------------------------|-------|
| O1     | Member     | `members`      | `Member`                                     | `MemberCreate`, `MemberResponse`           | `id` is UUID, `email` is unique. |
| O2     | Book       | `books`        | `Book`                                       | `BookCreate`, `BookResponse`               | `id` is UUID, `isbn` is unique. `status` is SQLAlchemy Enum. |
| O3     | Loan       | `loans`        | `Loan`                                       | `LoanCreate`, `LoanResponse`               | `id` is UUID. FKs to `Member` (O1) and `Book` (O2). `status` is SQLAlchemy Enum. |
| O4     | Reservation| `reservations` | `Reservation`                                | `ReservationCreate`, `ReservationResponse` | `id` is UUID. FKs to `Member` (O1) and `Book` (O2). `status` is SQLAlchemy Enum. |
| O5     | Fine       | `fines`        | `Fine`                                       | `FineCreate`, `FineResponse`               | `id` is UUID. FKs to `Member` (O1) and `Loan` (O3). `status` is SQLAlchemy Enum. |

**ISO 19450 §6.5.2 Aggregation-Participation:** `Loan` (O3) stores foreign keys `member_id` and `book_id` to link to `Member` (O1) and `Book` (O2), respectively. This is implemented in `backend/app/models.py` with `ForeignKey` and `relationship` fields.

## 2. API Endpoints (Processes & Interactions)

**ISO 19450 §6.2 Result Link:** OPM Processes create new OPM Objects as results.
**ISO 19450 §7.3.1 State Transition:** Atomic transactions are used to manage state changes, with `409 Conflict` responses for invalid transitions.
**ISO 19450 §5.4 Agent Link:** `Member` (O1) acts as an agent in `Loan` and `Reservation` processes, enforced by requiring `member_id` and checking its existence.

| OPM ID | OPM Process / Derived | API Endpoint (`backend/app/main.py`) | CRUD Function (`backend/app/crud.py`) | Frontend Component (`frontend/src/pages/`) | ISO 19450 Rules & Notes |
|--------|-----------------------|--------------------------------------|-----------------------------------------|---------------------------------------------|-------------------------|
| P1     | Borrow Book           | `POST /loans`                        | `create_loan`                           | `Loans.jsx` (Borrow button/form)            | **Result Link:** Creates O3 (Loan). **State Transition:** `Book.Available -> Book.Borrowed` (BR1). Atomic transaction. Checks `Book.status` for `Available`. **Agent Link:** Requires `member_id` (O1). |
| derived| List Loans            | `GET /loans`                         | `get_loans`                             | `Loans.jsx` (List display)                  | Includes associated `Member` and `Book` details. |
| derived| Get Loan by ID        | `GET /loans/{id}`                    | `get_loan`                              | `Loans.jsx` (Detail view)                   | Includes associated `Member` and `Book` details. |
| P2     | Return Book           | `POST /loans/{id}/return`            | `return_loan`                           | `Loans.jsx` (Return button)                 | **State Transition:** `Loan.Active -> Loan.Returned` (BR2) and `Book.Borrowed -> Book.Available` (BR3). Atomic transaction. Checks `Loan.status` for `Active`. **Agent Link:** Requires `member_id` (O1). |
| P3     | Reserve Book          | `POST /reservations`                 | `create_reservation`                    | `Reservations.jsx` (Reserve button/form)    | **Result Link:** Creates O4 (Reservation). **State Transition:** `Book.Available -> Book.Reserved` (BR4). Atomic transaction. Checks `Book.status` for `Available`. **Agent Link:** Requires `member_id` (O1). |
| derived| List Reservations     | `GET /reservations`                  | `get_reservations`                      | `Reservations.jsx` (List display)           | Includes associated `Member` and `Book` details. |
| derived| Get Reservation by ID | `GET /reservations/{id}`             | `get_reservation`                       | `Reservations.jsx` (Detail view)            | Includes associated `Member` and `Book` details. |
| P4     | Cancel Reservation    | `POST /reservations/{id}/cancel`     | `cancel_reservation`                    | `Reservations.jsx` (Cancel button)          | **State Transition:** `Reservation.Pending -> Reservation.Cancelled` (BR5). Atomic transaction. Checks `Reservation.status` for `Pending`. If book is `Reserved` by this reservation, `Book.Reserved -> Book.Available`. **Agent Link:** Requires `member_id` (O1). |
| P5     | Issue Fine            | `POST /fines`                        | `create_fine`                           | `Fines.jsx` (Issue Fine button/form)        | **Result Link:** Creates O5 (Fine). **Instrument Link:** `Loan` (O3.Overdue) is context if `loan_id` provided. |
| derived| List Fines            | `GET /fines`                         | `get_fines`                             | `Fines.jsx` (List display)                  | Includes associated `Member` and `Loan` details. |
| derived| Get Fine by ID        | `GET /fines/{id}`                    | `get_fine`                              | `Fines.jsx` (Detail view)                   | Includes associated `Member` and `Loan` details. |
| P6     | Pay Fine              | `POST /fines/{id}/pay`               | `pay_fine`                              | `Fines.jsx` (Pay button)                    | **State Transition:** `Fine.Unpaid -> Fine.Paid` (BR6). Atomic transaction. Checks `Fine.status` for `Unpaid`. **Consumption Link:** `Fine` (O5) state advances irreversibly. |
| derived| List Members          | `GET /members`                       | `get_members`                           | `Members.jsx` (List display)                | |
| derived| Get Member by ID      | `GET /members/{id}`                  | `get_member`                            | `Members.jsx` (Detail view)                 | |
| derived| List Books            | `GET /books`                         | `get_books`                             | `Books.jsx` (List display)                  | |
| derived| Get Book by ID        | `GET /books/{id}`                    | `get_book`                              | `Books.jsx` (Detail view)                   | |

## 3. Business Rules (BR) Implementation

All Business Rules are enforced in the backend's `crud.py` module, specifically within the functions responsible for state transitions, ensuring data integrity and adherence to ISO 19450 §7.3.1 State Transition principles.

| OPM ID | Business Rule                                   | Implementation Location (`backend/app/crud.py`) | Notes |
|--------|-------------------------------------------------|-------------------------------------------------|-------|
| BR1    | `Book.Available -> Book.Borrowed` only via P1   | `create_loan` function                          | Checks `book.status == BookStatus.Available` before update. |
| BR2    | `Loan.Active -> Loan.Returned` only via P2      | `return_loan` function                          | Checks `loan.status == LoanStatus.Active` before update. |
| BR3    | `Book.Borrowed -> Book.Available` only via P2   | `return_loan` function                          | Updates associated `book.status` after `Loan` is returned. |
| BR4    | `Book.Available -> Book.Reserved` only via P3   | `create_reservation` function                   | Checks `book.status == BookStatus.Available` before update. |
| BR5    | `Reservation.Pending -> Reservation.Cancelled` only via P4 | `cancel_reservation` function                   | Checks `reservation.status == ReservationStatus.Pending` before update. Conditionally updates `Book.status` if `Reserved` by this reservation. |
| BR6    | `Fine.Unpaid -> Fine.Paid` only via P6          | `pay_fine` function                             | Checks `fine.status == FineStatus.Unpaid` before update. |
