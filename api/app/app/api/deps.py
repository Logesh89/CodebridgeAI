"""FastAPI dependencies."""

import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models import User, UserRole
from app.services.auth_service import AuthService

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole):
    async def role_checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise AuthorizationError(f"Required role: {[r.value for r in roles]}")
        return user

    return role_checker
