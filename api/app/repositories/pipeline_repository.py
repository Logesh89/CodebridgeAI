"""Pipeline repository."""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pipeline, PipelineStatus
from app.repositories.base import BaseRepository


class PipelineRepository(BaseRepository[Pipeline]):
    def __init__(self, db: AsyncSession):
        super().__init__(Pipeline, db)

    async def get_by_path(self, path: str) -> Optional[Pipeline]:
        result = await self.db.execute(select(Pipeline).where(Pipeline.path == path))
        return result.scalar_one_or_none()

    async def get_by_batch(self, batch_id: str) -> list[Pipeline]:
        result = await self.db.execute(select(Pipeline).where(Pipeline.upload_batch_id == batch_id))
        return list(result.scalars().all())

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(Pipeline.status, func.count(Pipeline.id)).group_by(Pipeline.status)
        )
        return {status.value: count for status, count in result.all()}

    async def get_recent(self, limit: int = 10) -> list[Pipeline]:
        result = await self.db.execute(
            select(Pipeline).order_by(Pipeline.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_failed_pipelines(self, limit: int = 10) -> list[Pipeline]:
        result = await self.db.execute(
            select(Pipeline)
            .where(Pipeline.status == PipelineStatus.FAILED)
            .order_by(Pipeline.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
