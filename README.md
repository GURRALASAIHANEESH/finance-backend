# Finance Data Processing and Access Control Backend

A production-structured REST API built with FastAPI and PostgreSQL for managing financial records, featuring secure role-based access control (RBAC).

***

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (Docker locally, Neon in production) |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Password Hashing | Argon2 |
| Authentication | JWT via python-jose |
| Validation | Pydantic v2 |
| Testing | Pytest — 39 tests |

***

## Architecture

3-layer separation — routes never touch the database, services never import SQLAlchemy directly:

    app/
    ├── api/v1/         Route handlers — thin, delegate to services
    ├── services/       Business logic and validation
    ├── repositories/   All database queries
    ├── models/         SQLAlchemy ORM models
    ├── schemas/        Pydantic v2 request/response schemas
    └── core/           Config, database session, security utilities

***

## Role-Based Access Control

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| POST /auth/login | Yes | Yes | Yes |
| GET /users/me | Yes | Yes | Yes |
| GET /users/ | No | No | Yes |
| POST /users/ | No | No | Yes |
| PATCH /users/{id} | No | No | Yes |
| DELETE /users/{id} | No | No | Yes |
| GET /records/ | No | Yes | Yes |
| GET /records/{id} | No | Yes | Yes |
| POST /records/ | No | No | Yes |
| PATCH /records/{id} | No | No | Yes |
| DELETE /records/{id} | No | No | Yes |
| GET /dashboard/summary | Yes | Yes | Yes |
| GET /dashboard/categories | Yes | Yes | Yes |
| GET /dashboard/recent | Yes | Yes | Yes |
| GET /dashboard/trends/monthly | No | Yes | Yes |
| GET /dashboard/trends/weekly | No | Yes | Yes |

***

## Local Setup

**Prerequisites:** Docker Desktop, Python 3.12, Git

**1. Clone the repository**

    git clone https://github.com/GURRALASAIHANEESH/finance-backend.git
    cd finance-backend

**2. Create and activate virtual environment**

    python -m venv venv

    # Windows
    venv\Scripts\activate

    # macOS / Linux
    source venv/bin/activate

**3. Install dependencies**

    pip install -r requirements.txt

**4. Configure environment**

    cp .env.example .env

Edit `.env` and set a strong `SECRET_KEY`. All other defaults work for local development.

**5. Start the database**

    docker-compose up -d

PostgreSQL starts on port `5434` — a non-default port to avoid conflicts with any existing local PostgreSQL installation.

**6. Run migrations**

    alembic upgrade head

**7. Seed the database**

    python scripts/seed.py

This creates three users and 30 financial records:

| Email | Password | Role |
|---|---|---|
| admin@finance.com | Admin@1234 | Admin |
| analyst@finance.com | Analyst@1234 | Analyst |
| viewer@finance.com | Viewer@1234 | Viewer |

**8. Start the server**

    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

Swagger UI: http://localhost:8080/docs

***

## Running Tests

    pytest tests/ -v

The test suite uses an isolated in-memory SQLite database. It never touches the development database and can be run without Docker.

***

## API Reference

### Authentication

    POST /api/v1/auth/login      Returns access token and refresh token
    POST /api/v1/auth/refresh    Exchanges refresh token for a new access token

### Users

    GET    /api/v1/users/         List all users with pagination
    POST   /api/v1/users/         Create a new user
    GET    /api/v1/users/me       Get the profile of the currently authenticated user
    GET    /api/v1/users/{id}     Get a user by ID
    PATCH  /api/v1/users/{id}     Update user role or status
    DELETE /api/v1/users/{id}     Soft delete a user

### Financial Records

    GET    /api/v1/records/       List records — filter by type, category, date range, pagination
    POST   /api/v1/records/       Create a new financial record
    GET    /api/v1/records/{id}   Get a record by ID
    PATCH  /api/v1/records/{id}   Update a record
    DELETE /api/v1/records/{id}   Soft delete a record

### Dashboard

    GET /api/v1/dashboard/summary            Total income, expenses, net balance, health indicator
    GET /api/v1/dashboard/categories         Income and expense breakdown by category
    GET /api/v1/dashboard/recent             Most recent records (configurable limit up to 50)
    GET /api/v1/dashboard/trends/monthly     Month-by-month breakdown for a given year
    GET /api/v1/dashboard/trends/weekly      Week-by-week breakdown for a date range (max 90 days)

***

## Deployment

Live API: https://finance-backend.onrender.com

Swagger UI: https://finance-backend.onrender.com/docs

***

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| APP_NAME | Application name | Finance Backend |
| APP_ENV | Environment name | development |
| DEBUG | Enables debug mode and open CORS | true |
| SECRET_KEY | JWT signing key — use a long random string in production | required |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime in minutes | 60 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime in days | 7 |
| ALGORITHM | JWT signing algorithm | HS256 |
| DATABASE_URL | PostgreSQL connection string | required |
| ALLOWED_ORIGINS | Comma-separated list of allowed CORS origins | * |
| FIRST_ADMIN_EMAIL | Email for the seed admin user | admin@finance.com |
| FIRST_ADMIN_PASSWORD | Password for the seed admin user | Admin@1234 |
| FIRST_ADMIN_NAME | Display name for the seed admin user | Super Admin |