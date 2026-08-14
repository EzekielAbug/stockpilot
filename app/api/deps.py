"""FastAPI dependencies for authentication and authorization"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

# httpbearer

security = HTTPBearer()

# Role Hierarchy

ROLE_HIERARCHY = {
    UserRole.OWNER: 5,
    UserRole.ADMIN: 4,
    UserRole.MANAGER: 3,
    UserRole.STAFF: 2,
    UserRole.VIEWER: 1,
}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT token."""
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the current user's account is active."""

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return current_user

class RoleChecker:
    """Dependency that checks if a user has the required role level."""

    def __init__(self, required_role: UserRole) -> None:
        self.required_role = required_role
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        """Check if the user's role meets the minimum required level."""

        user_role = UserRole(current_user.role)
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        required_level = ROLE_HIERARCHY.get(self.required_role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' does not have sufficient permissions. "
                       f"Requires '{self.required_role.value}' or higher.",
            )
        return current_user