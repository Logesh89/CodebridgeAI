"""Authentication API routes."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyOTPRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


from pydantic import BaseModel

class GoogleLoginRequest(BaseModel):
    email: str


@router.post("/google", response_model=TokenResponse)
async def google_login(request: GoogleLoginRequest, db: DbSession):
    auth_service = AuthService(db)
    return await auth_service.google_login(request.email)


@router.post("/login")
async def login(request: LoginRequest, db: DbSession):
    auth_service = AuthService(db)
    return await auth_service.login(request)


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTPRequest, db: DbSession):
    auth_service = AuthService(db)
    return await auth_service.verify_otp(request)


@router.post("/logout", response_model=MessageResponse)
async def logout(user: CurrentUser, db: DbSession):
    auth_service = AuthService(db)
    await auth_service.logout(user.id)
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, db: DbSession):
    auth_service = AuthService(db)
    result = await auth_service.forgot_password(request.email)
    return MessageResponse(message=result["message"])


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, db: DbSession):
    auth_service = AuthService(db)
    result = await auth_service.reset_password(request.token, request.new_password)
    return MessageResponse(message=result["message"])


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: DbSession):
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser):
    return user
