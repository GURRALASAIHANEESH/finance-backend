from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserRepository(db).get_by_id(payload["sub"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is deactivated. Contact an admin.",
        )

    return user


# Returns a dependency that enforces minimum role requirement.
# Usage: Depends(require_role(UserRole.ADMIN))

def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Required role: "
                    f"{' or '.join(r.value for r in allowed_roles)}. "
                    f"Your role: {current_user.role.value}"
                ),
            )
        return current_user
    return role_checker


# Import these directly in route files for clean, readable code

def viewer_or_above(user: User = Depends(get_current_user)) -> User:
    """All authenticated users — Viewer, Analyst, Admin."""
    return user


def analyst_or_above(
    user: User = Depends(require_role(UserRole.ANALYST, UserRole.ADMIN))
) -> User:
    """Analyst and Admin only."""
    return user


def admin_only(
    user: User = Depends(require_role(UserRole.ADMIN))
) -> User:
    """Admin only."""
    return user