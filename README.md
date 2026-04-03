# Finance Data Processing and Access Control Backend

A production-structured REST API built with FastAPI and PostgreSQL for managing financial records with role-based access control. Built as an internship technical assessment for Zorvyn FinTech.

## Tech Stack

- **FastAPI** — API framework with automatic OpenAPI documentation
- **PostgreSQL** — Primary database via Docker
- **SQLAlchemy** — ORM with declarative models
- **Alembic** — Database migrations
- **Argon2** — Password hashing
- **python-jose** — JWT access and refresh tokens
- **Pydantic v2** — Request validation and response serialization
- **Pytest** — 39 tests covering auth, RBAC, CRUD, and dashboard endpoints

## Architecture

The project follows a strict 3-layer architecture:
app/
├── api/v1/ # Route handlers — thin, no business logic
├── services/ # Business logic and validation
├── repositories/ # Database queries — all DB access goes here
├── models/ # SQLAlchemy ORM models
├── schemas/ # Pydantic v2 request/response schemas
└── core/ # Config, database session, security utilities


Routes never touch the database directly. Services never import SQLAlchemy. This separation makes each layer independently testable.

## Roles and Permissions

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `GET /users/me` | ✅ | ✅ | ✅ |
| `GET /users/` | ❌ | ❌ | ✅ |
| `POST /users/` | ❌ | ❌ | ✅ |
| `PATCH /users/{id}` | ❌ | ❌ | ✅ |
| `DELETE /users/{id}` | ❌ | ❌ | ✅ |
| `GET /records/` | ❌ | ✅ | ✅ |
| `GET /records/{id}` | ❌ | ✅ | ✅ |
| `POST /records/` | ❌ | ❌ | ✅ |
| `PATCH /records/{id}` | ❌ | ❌ | ✅ |
| `DELETE /records/{id}` | ❌ | ❌ | ✅ |
| `GET /dashboard/summary` | ✅ | ✅ | ✅ |
| `GET /dashboard/categories` | ✅ | ✅ | ✅ |
| `GET /dashboard/recent` | ✅ | ✅ | ✅ |
| `GET /dashboard/trends/monthly` | ❌ | ✅ | ✅ |
| `GET /dashboard/trends/weekly` | ❌ | ✅ | ✅ |

## Local Setup

**Prerequisites:** Docker Desktop, Python 3.12, Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/finance-backend.git
cd finance-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY`. All other defaults work for local development.

### 5. Start the database

```bash
docker-compose up -d
```

This starts PostgreSQL on port `5434` (non-default to avoid conflicts with any local PostgreSQL installation).

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Seed the database

```bash
python scripts/seed.py
```

This creates three users and 30 financial records:

| Email | Password | Role |
|---|---|---|
| admin@finance.com | Admin@1234 | Admin |
| analyst@finance.com | Analyst@1234 | Analyst |
| viewer@finance.com | Viewer@1234 | Viewer |

### 8. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

API docs available at: [http://localhost:8080/docs](http://localhost:8080/docs)

## Running Tests

```bash
pytest tests/ -v
```

The test suite uses a separate in-memory SQLite database and never touches the development database.

## API Overview

### Authentication
POST /api/v1/auth/login — Returns access + refresh tokens
POST /api/v1/auth/refresh — Exchanges refresh token for a new access token


### Users
GET /api/v1/users/ — List all users (paginated)
POST /api/v1/users/ — Create a user
GET /api/v1/users/me — Get current user profile
GET /api/v1/users/{id} — Get user by ID
PATCH /api/v1/users/{id} — Update user role or status
DELETE /api/v1/users/{id} — Soft delete a user


### Financial Records
GET /api/v1/records/ — List records with filters (type, category, date range, pagination)
POST /api/v1/records/ — Create a record
GET /api/v1/records/{id} — Get record by ID
PATCH /api/v1/records/{id} — Update a record
DELETE /api/v1/records/{id} — Soft delete a record


### Dashboard
GET /api/v1/dashboard/summary — Total income, expenses, net balance, health indicator
GET /api/v1/dashboard/categories — Income and expense breakdown by category
GET /api/v1/dashboard/recent — Most recent records (configurable limit)
GET /api/v1/dashboard/trends/monthly — Month-by-month income/expense/net for a given year
GET /api/v1/dashboard/trends/weekly — Week-by-week breakdown for a date range (max 90 days)


## Deployment

Live API: `YOUR_RENDER_URL`

Swagger UI: `YOUR_RENDER_URL/docs`

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Application name | Finance Backend |
| `APP_ENV` | Environment name | development |
| `DEBUG` | Enables debug mode and open CORS | true |
| `SECRET_KEY` | JWT signing key — use a long random string in production | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | 60 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | 7 |
| `ALGORITHM` | JWT signing algorithm | HS256 |
| `DATABASE_URL` | PostgreSQL connection string | — |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | * |
