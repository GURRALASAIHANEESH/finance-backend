from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserListResponse
from app.models.user import User, UserRole


class UserService:

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def create_user(self, payload: UserCreate, requesting_user: User) -> UserRead:
        # Only admins can create users
        if self.user_repo.email_exists(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{payload.email}' already exists",
            )

        # Prevent creating another admin unless explicitly intended
        if payload.role == UserRole.ADMIN:
            existing_admins = self.user_repo.count_by_role(UserRole.ADMIN)
            if existing_admins >= 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum admin limit reached. Demote an existing admin first.",
                )

        user = self.user_repo.create(payload)
        return UserRead.model_validate(user)

    def get_user(self, user_id: str) -> UserRead:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )
        return UserRead.model_validate(user)

    def list_users(self, page: int, page_size: int) -> UserListResponse:
        users, total = self.user_repo.get_all(page, page_size)
        return UserListResponse(
            total=total,
            page=page,
            page_size=page_size,
            results=[UserRead.model_validate(u) for u in users],
        )

    def update_user(self, user_id: str, payload: UserUpdate, requesting_user: User) -> UserRead:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )

        # Prevent admin from deactivating themselves
        if str(user.id) == str(requesting_user.id) and payload.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account",
            )

        # Prevent demoting the last admin
        if (
            user.role == UserRole.ADMIN
            and payload.role is not None
            and payload.role != UserRole.ADMIN
        ):
            admin_count = self.user_repo.count_by_role(UserRole.ADMIN)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot demote the last admin in the system",
                )

        updated = self.user_repo.update(user, payload)
        return UserRead.model_validate(updated)

    def delete_user(self, user_id: str, requesting_user: User) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )

        if str(user.id) == str(requesting_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account",
            )

        # Prevent deleting the last admin
        if user.role == UserRole.ADMIN:
            admin_count = self.user_repo.count_by_role(UserRole.ADMIN)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin in the system",
                )

        self.user_repo.soft_delete(user)
        return {"message": f"User '{user.name}' has been deactivated and removed"}