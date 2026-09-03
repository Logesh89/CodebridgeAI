"""Log repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LogEntry
from app.repositories.base import BaseRepository


class LogRepository(BaseRepository[LogEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(LogEntry, db)

    async def get_recent(self, limit: int = 50, pipeline_id: uuid.UUID | None = None) -> list[LogEntry]:
        query = select(LogEntry).order_by(LogEntry.created_at.desc()).limit(limit)
        if pipeline_id:
            query = query.where(LogEntry.pipeline_id == pipeline_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
