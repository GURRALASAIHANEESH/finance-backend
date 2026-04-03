from pydantic import BaseModel, Field, model_validator
from datetime import datetime, date
from typing import Optional
from app.models.financial_record import RecordType, RecordCategory


INCOME_CATEGORIES = {
    RecordCategory.SALARY,
    RecordCategory.FREELANCE,
    RecordCategory.INVESTMENT,
    RecordCategory.RENTAL,
    RecordCategory.BUSINESS,
    RecordCategory.OTHER_INCOME,
}

EXPENSE_CATEGORIES = {
    RecordCategory.FOOD,
    RecordCategory.TRANSPORT,
    RecordCategory.UTILITIES,
    RecordCategory.HEALTHCARE,
    RecordCategory.EDUCATION,
    RecordCategory.ENTERTAINMENT,
    RecordCategory.SHOPPING,
    RecordCategory.RENT,
    RecordCategory.TAX,
    RecordCategory.OTHER_EXPENSE,
}


class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    type: RecordType
    category: RecordCategory
    record_date: date
    notes: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def category_matches_type(self) -> "RecordCreate":
        if self.type == RecordType.INCOME and self.category not in INCOME_CATEGORIES:
            raise ValueError(
                f"Category '{self.category}' is not valid for income records. "
                f"Valid income categories: {[c.value for c in INCOME_CATEGORIES]}"
            )
        if self.type == RecordType.EXPENSE and self.category not in EXPENSE_CATEGORIES:
            raise ValueError(
                f"Category '{self.category}' is not valid for expense records. "
                f"Valid expense categories: {[c.value for c in EXPENSE_CATEGORIES]}"
            )
        return self


class RecordUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[RecordCategory] = None
    record_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    model_config = {"extra": "forbid"}

    # Note: type is intentionally NOT updatable — changing income to expense
    # would break audit history. Create a new record instead.


class RecordRead(BaseModel):
    id: str
    amount: float
    type: RecordType
    category: RecordCategory
    record_date: date
    notes: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecordFilter(BaseModel):
    type: Optional[RecordType] = None
    category: Optional[RecordCategory] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @model_validator(mode="after")
    def date_range_valid(self) -> "RecordFilter":
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from cannot be after date_to")
        return self


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[RecordRead]