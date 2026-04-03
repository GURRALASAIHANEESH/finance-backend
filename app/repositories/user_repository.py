from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from typing import Optional


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.scalar(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(
            select(User).where(User.email == email, User.is_deleted == False)
        )

    def get_all(self, page: int, page_size: int) -> tuple[list[User], int]:
        base_query = select(User).where(User.is_deleted == False)

        total = self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        )

        users = self.db.scalars(
            base_query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        return list(users), total

    def create(self, payload: UserCreate) -> User:
        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, payload: UserUpdate) -> User:
        # Only update fields that were explicitly provided
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User) -> None:
        user.is_deleted = True
        user.is_active = False
        self.db.commit()

    def email_exists(self, email: str) -> bool:
        return self.db.scalar(
            select(func.count()).where(User.email == email, User.is_deleted == False)
        ) > 0

    def count_by_role(self, role: UserRole) -> int:
        return self.db.scalar(
            select(func.count()).where(User.role == role, User.is_deleted == False)
        )