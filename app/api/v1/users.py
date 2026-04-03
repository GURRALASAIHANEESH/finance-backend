from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserListResponse
from app.api.deps import get_current_user, admin_only
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserRead,
    status_code=201,
    summary="Create a new user [Admin only]",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Create a new user with a specified role.
    Only admins can perform this action.
    """
    return UserService(db).create_user(payload, requesting_user=current_user)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users [Admin only]",
)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Returns a paginated list of all non-deleted users.
    Only admins can view the full user list.
    """
    return UserService(db).list_users(page, page_size)

@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the currently authenticated user [All roles]",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Returns the profile of the user derived from the JWT token.
    Accessible by any authenticated user regardless of role.
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user by ID [Admin only]",
)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    return UserService(db).get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update user role or status [Admin only]",
)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Update a user's name, role, or active status.
    Record type is intentionally not updatable to preserve audit integrity.
    """
    return UserService(db).update_user(user_id, payload, requesting_user=current_user)


@router.delete(
    "/{user_id}",
    summary="Soft delete a user [Admin only]",
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    return UserService(db).delete_user(user_id, requesting_user=current_user)