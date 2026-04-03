import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.financial_record import FinancialRecord, RecordType, RecordCategory
from datetime import date

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_tables():
    yield
    db = TestingSessionLocal()
    db.query(FinancialRecord).delete()
    db.query(User).delete()
    db.commit()
    db.close()


@pytest.fixture
def db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    user = User(
        name="Test Admin",
        email="admin@test.com",
        hashed_password=hash_password("Admin@1234"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def analyst_user(db):
    user = User(
        name="Test Analyst",
        email="analyst@test.com",
        hashed_password=hash_password("Analyst@1234"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def viewer_user(db):
    user = User(
        name="Test Viewer",
        email="viewer@test.com",
        hashed_password=hash_password("Viewer@1234"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    return response.json()["access_token"]


@pytest.fixture
def analyst_token(client, analyst_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "analyst@test.com",
        "password": "Analyst@1234",
    })
    return response.json()["access_token"]


@pytest.fixture
def viewer_token(client, viewer_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "viewer@test.com",
        "password": "Viewer@1234",
    })
    return response.json()["access_token"]


@pytest.fixture
def sample_record(db, admin_user):
    record = FinancialRecord(
        amount=5000.00,
        type=RecordType.INCOME,
        category=RecordCategory.SALARY,
        record_date=date(2026, 3, 1),
        notes="Test salary record",
        created_by=admin_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record