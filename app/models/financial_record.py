import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Numeric, Enum, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class RecordType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class RecordCategory(str, enum.Enum):
    # Income categories
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    RENTAL = "rental"
    BUSINESS = "business"
    OTHER_INCOME = "other_income"

    # Expense categories
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    RENT = "rent"
    TAX = "tax"
    OTHER_EXPENSE = "other_expense"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    amount: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )

    type: Mapped[RecordType] = mapped_column(
        Enum(RecordType), nullable=False, index=True
    )

    category: Mapped[RecordCategory] = mapped_column(
        Enum(RecordCategory), nullable=False, index=True
    )

    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete — keeps audit history intact
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Track who created this record
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    created_by_user: Mapped["User"] = relationship(
        "User", back_populates="financial_records"
    )

    def __repr__(self) -> str:
        return f"<FinancialRecord id={self.id} type={self.type} amount={self.amount}>"