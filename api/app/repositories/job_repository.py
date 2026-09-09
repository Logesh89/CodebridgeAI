"""Job repository."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, JobStatus
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)

    async def count_by_status(self, status: JobStatus) -> int:
        result = await self.db.execute(
            select(func.count(Job.id)).where(Job.status == status)
        )
        return result.scalar() or 0

    async def get_running_jobs(self) -> list[Job]:
        result = await self.db.execute(
            select(Job).where(Job.status == JobStatus.RUNNING).order_by(Job.started_at.desc())
        )
        return list(result.scalars().all())
