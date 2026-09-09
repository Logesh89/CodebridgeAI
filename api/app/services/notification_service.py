"""Notification service."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification
from app.repositories.notification_repository import NotificationRepository
from app.services.email_service import EmailService


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)
        self.email_service = EmailService()

    async def create_notification(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: str,
        pipeline_id: uuid.UUID | None = None,
        send_email: bool = True,
        user_email: str | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            pipeline_id=pipeline_id,
        )
        await self.repo.create(notification)

        if send_email and user_email:
            await self.email_service.send_notification(user_email, title, message)

        return notification

    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        unread_only: bool = False,
    ) -> list[Notification]:
        return await self.repo.get_by_user(user_id, unread_only)

    async def mark_as_read(self, notification_id: uuid.UUID) -> None:
        notification = await self.repo.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            await self.repo.update(notification)

    async def notify_conversion_started(self, user_id: uuid.UUID, pipeline_name: str, email: str) -> None:
        await self.create_notification(
            user_id=user_id,
            title="Conversion Started",
            message=f"AI conversion started for pipeline: {pipeline_name}",
            notification_type="conversion_started",
            user_email=email,
        )

    async def notify_conversion_completed(self, user_id: uuid.UUID, pipeline_name: str, email: str) -> None:
        await self.create_notification(
            user_id=user_id,
            title="Conversion Completed",
            message=f"Pipeline {pipeline_name} converted successfully",
            notification_type="conversion_completed",
            user_email=email,
        )

    async def notify_validation_failed(self, user_id: uuid.UUID, pipeline_name: str, email: str) -> None:
        await self.create_notification(
            user_id=user_id,
            title="Validation Failed",
            message=f"Validation failed for pipeline: {pipeline_name}",
            notification_type="validation_failed",
            user_email=email,
        )
