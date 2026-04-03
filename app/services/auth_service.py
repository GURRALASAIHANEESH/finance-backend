from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.models.user import User


class AuthService:

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(payload.email)

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated. Contact an admin.",
            )

        token_data = {"sub": user.id, "role": user.role.value}

        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        token_data = decode_token(payload.refresh_token)

        if not token_data or token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user = self.user_repo.get_by_id(token_data["sub"])

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists or is inactive",
            )

        new_token_data = {"sub": user.id, "role": user.role.value}

        return TokenResponse(
            access_token=create_access_token(new_token_data),
            refresh_token=create_refresh_token(new_token_data),
        )