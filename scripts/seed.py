"""
Seed Script — Finance Backend

"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
import random
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.financial_record import FinancialRecord, RecordType, RecordCategory
from sqlalchemy import select


SEED_USERS = [
    {
        "name": "Super Admin",
        "email": "admin@finance.com",
        "password": "Admin@1234",
        "role": UserRole.ADMIN,
    },
    {
        "name": "Alice Analyst",
        "email": "analyst@finance.com",
        "password": "Analyst@1234",
        "role": UserRole.ANALYST,
    },
    {
        "name": "Victor Viewer",
        "email": "viewer@finance.com",
        "password": "Viewer@1234",
        "role": UserRole.VIEWER,
    },
]

INCOME_SAMPLES = [
    (RecordCategory.SALARY,       8500.00, "Monthly salary — March"),
    (RecordCategory.SALARY,       8500.00, "Monthly salary — February"),
    (RecordCategory.SALARY,       8500.00, "Monthly salary — January"),
    (RecordCategory.FREELANCE,    1200.00, "Web design project — client A"),
    (RecordCategory.FREELANCE,     800.00, "API integration — client B"),
    (RecordCategory.INVESTMENT,    650.00, "Dividend payout — Q1"),
    (RecordCategory.INVESTMENT,    320.00, "Mutual fund returns"),
    (RecordCategory.RENTAL,       1500.00, "Rental income — apartment"),
    (RecordCategory.BUSINESS,     2200.00, "SaaS product revenue — Feb"),
    (RecordCategory.OTHER_INCOME,  200.00, "Cashback rewards"),
]

EXPENSE_SAMPLES = [
    (RecordCategory.RENT,          1200.00, "Monthly rent — March"),
    (RecordCategory.RENT,          1200.00, "Monthly rent — February"),
    (RecordCategory.FOOD,           450.00, "Groceries and dining — March"),
    (RecordCategory.FOOD,           380.00, "Groceries and dining — February"),
    (RecordCategory.TRANSPORT,      180.00, "Fuel and cab rides"),
    (RecordCategory.UTILITIES,      120.00, "Electricity and internet bill"),
    (RecordCategory.UTILITIES,       95.00, "Water and gas bill"),
    (RecordCategory.HEALTHCARE,     300.00, "Annual health checkup"),
    (RecordCategory.EDUCATION,      499.00, "Online course subscription"),
    (RecordCategory.ENTERTAINMENT,   89.00, "Streaming subscriptions"),
    (RecordCategory.SHOPPING,       320.00, "Clothing and accessories"),
    (RecordCategory.SHOPPING,       145.00, "Electronics — keyboard"),
    (RecordCategory.TAX,           1100.00, "Quarterly advance tax"),
    (RecordCategory.OTHER_EXPENSE,   60.00, "Miscellaneous — stationery"),
    (RecordCategory.TRANSPORT,      220.00, "Flight ticket — team meetup"),
    (RecordCategory.HEALTHCARE,     150.00, "Pharmacy — prescriptions"),
    (RecordCategory.FOOD,           200.00, "Team lunch — office"),
    (RecordCategory.ENTERTAINMENT,   45.00, "Books and magazines"),
    (RecordCategory.EDUCATION,      199.00, "Conference ticket"),
    (RecordCategory.OTHER_EXPENSE,   80.00, "Bank charges and fees"),
]


def random_date_in_last_90_days() -> date:
    return date.today() - timedelta(days=random.randint(0, 90))


def seed():
    db = SessionLocal()

    try:
        existing = db.scalar(select(User).where(User.email == "admin@finance.com"))
        if existing:
            print("Database already seeded. Skipping.")
            return

        print("Seeding users...")
        created_users = []

        for user_data in SEED_USERS:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            db.add(user)
            created_users.append(user)

        db.flush()

        admin_user = created_users[0]

        print("Seeding financial records...")

        for category, amount, notes in INCOME_SAMPLES:
            record = FinancialRecord(
                amount=amount,
                type=RecordType.INCOME,
                category=category,
                record_date=random_date_in_last_90_days(),
                notes=notes,
                created_by=admin_user.id,
            )
            db.add(record)

        for category, amount, notes in EXPENSE_SAMPLES:
            record = FinancialRecord(
                amount=amount,
                type=RecordType.EXPENSE,
                category=category,
                record_date=random_date_in_last_90_days(),
                notes=notes,
                created_by=admin_user.id,
            )
            db.add(record)

        db.commit()

        print("\nSeed complete.")
        print("-" * 60)
        print(f"  {'Role':<10} {'Email':<25} {'Password'}")
        print("-" * 60)
        for u in SEED_USERS:
            print(f"  {u['role'].value:<10} {u['email']:<25} {u['password']}")
        print("-" * 60)
        print(f"\n  Income records  : {len(INCOME_SAMPLES)}")
        print(f"  Expense records : {len(EXPENSE_SAMPLES)}")
        print(f"  Total records   : {len(INCOME_SAMPLES) + len(EXPENSE_SAMPLES)}\n")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()