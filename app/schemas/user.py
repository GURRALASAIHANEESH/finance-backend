from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    role: UserRole = UserRole.VIEWER

    @model_validator(mode="after")
    def password_strength(self) -> "UserCreate":
        pw = self.password
        if not any(c.isupper() for c in pw):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in pw):
            raise ValueError("Password must contain at least one digit")
        return self


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    model_config = {"extra": "forbid"}  # reject unknown fields


class UserRead(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[UserRead]