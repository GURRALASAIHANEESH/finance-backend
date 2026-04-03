from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Login and get tokens")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password.
    Returns an access token (short-lived) and refresh token (long-lived).
    """
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    """
    return AuthService(db).refresh(payload)


@router.get("/me", response_model=UserRead, summary="Get current authenticated user")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    Accessible by all roles.
    """
    return UserRead.model_validate(current_user)