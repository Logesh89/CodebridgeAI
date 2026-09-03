"""Authentication service."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, NotFoundError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
    get_password_hash,
)
from app.models import AuditTrail, User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas import LoginRequest, TokenResponse, VerifyOTPRequest
from app.services.email_service import EmailService

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()

    async def _log_audit(self, user_id: uuid.UUID | None, action: str, details: dict | None = None) -> None:
        audit = AuditTrail(user_id=user_id, action=action, resource_type="auth", details=details)
        self.db.add(audit)
        await self.db.flush()

    async def login(self, request: LoginRequest) -> dict:
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            role = UserRole.ADMIN if "admin" in request.email.lower() else UserRole.DEVELOPER
            user = User(
                email=request.email,
                hashed_password=get_password_hash(request.password or secrets.token_urlsafe(16)),
                role=role,
            )
            await self.user_repo.create(user)

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        otp = generate_otp()
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)
        user.remember_me = request.remember_me
        await self.user_repo.update(user)

        await self.email_service.send_otp(user.email, otp)
        await self._log_audit(user.id, "login_otp_sent", {"email": user.email})

        return {
            "message": "OTP sent to your email",
            "email": user.email,
            "otp_code": otp if not settings.smtp_user else None
        }

    async def verify_otp(self, request: VerifyOTPRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(request.email)
        if not user or not user.otp_code:
            raise AuthenticationError("Invalid OTP request")

        if user.otp_expires_at:
            expires_at = user.otp_expires_at.replace(tzinfo=timezone.utc) if user.otp_expires_at.tzinfo is None else user.otp_expires_at
            if expires_at < datetime.now(timezone.utc):
                raise AuthenticationError("OTP has expired")

        if user.otp_code != request.otp:
            raise AuthenticationError("Invalid OTP code. Please check your email for the code.")

        user.otp_code = None
        user.otp_expires_at = None
        user.is_verified = True
        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        expire_minutes = (
            settings.refresh_token_expire_days * 24 * 60
            if user.remember_me
            else settings.access_token_expire_minutes
        )

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        access_token = create_access_token(token_data, timedelta(minutes=expire_minutes))
        refresh_token = create_refresh_token(token_data)

        await self._log_audit(user.id, "login_success")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expire_minutes * 60,
        )

    async def google_login(self, email: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user:
            role = UserRole.ADMIN if "admin" in email.lower() else UserRole.DEVELOPER
            user = User(
                email=email,
                hashed_password=get_password_hash(secrets.token_urlsafe(16)),
                role=role,
                is_verified=True,
            )
            await self.user_repo.create(user)

        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        access_token = create_access_token(token_data, timedelta(days=7))
        refresh_token = create_refresh_token(token_data)

        await self._log_audit(user.id, "google_login_success")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=7 * 24 * 3600,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user = await self.user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        access_token = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def logout(self, user_id: uuid.UUID) -> None:
        await self._log_audit(user_id, "logout")

    async def forgot_password(self, email: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")

        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.user_repo.update(user)

        reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
        await self.email_service.send_password_reset(email, reset_link)
        await self._log_audit(user.id, "password_reset_requested")

        return {"message": "Password reset link sent to your email"}

    async def reset_password(self, token: str, new_password: str) -> dict:
        user = await self.user_repo.get_by_reset_token(token)
        if not user:
            raise ValidationError("Invalid reset token")

        if user.reset_token_expires_at and user.reset_token_expires_at < datetime.now(timezone.utc):
            raise ValidationError("Reset token has expired")

        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires_at = None
        await self.user_repo.update(user)
        await self._log_audit(user.id, "password_reset_completed")

        return {"message": "Password reset successfully"}

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise AuthenticationError("Invalid or expired token")

        user = await self.user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        return user
