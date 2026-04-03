# Importing all models here ensures Alembic detects them
# during migrations via Base.metadata

from app.models.user import User, UserRole
from app.models.financial_record import FinancialRecord, RecordType, RecordCategory

__all__ = [
    "User",
    "UserRole",
    "FinancialRecord",
    "RecordType",
    "RecordCategory",
]