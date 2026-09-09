"""Dashboard metrics and analytics service."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DashboardMetric, JobStatus, LogEntry, Pipeline, PipelineExecution, PipelineStatus, ValidationReport
from app.repositories.job_repository import JobRepository
from app.repositories.log_repository import LogRepository
from app.repositories.pipeline_repository import PipelineRepository
from app.schemas import DashboardResponse


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pipeline_repo = PipelineRepository(db)
        self.job_repo = JobRepository(db)
        self.log_repo = LogRepository(db)

    async def get_dashboard(self) -> DashboardResponse:
        status_counts = await self.pipeline_repo.count_by_status()
        total = sum(status_counts.values())
        converted = status_counts.get(PipelineStatus.COMPLETED.value, 0)
        failed = status_counts.get(PipelineStatus.FAILED.value, 0)

        running_jobs = await self.job_repo.count_by_status(JobStatus.RUNNING)
        queued_jobs = await self.job_repo.count_by_status(JobStatus.QUEUED)

        avg_time = await self._get_average_execution_time()
        success_rate = (converted / total * 100) if total > 0 else 0.0
        failure_rate = (failed / total * 100) if total > 0 else 0.0

        recent_pipelines = await self.pipeline_repo.get_recent(10)
        recent_activity = [
            {
                "id": str(p.id),
                "name": p.name,
                "status": p.status.value,
                "updated_at": p.updated_at.isoformat(),
            }
            for p in recent_pipelines
        ]

        daily = await self._get_daily_conversions()
        monthly = await self._get_monthly_conversions()
        error_stats = await self._get_error_statistics()
        top_failed = await self._get_top_failed()

        latest_reports = await self._get_latest_reports()
        latest_logs = await self._get_latest_logs()

        return DashboardResponse(
            total_pipelines=total,
            converted_pipelines=converted,
            failed_pipelines=failed,
            running_jobs=running_jobs,
            queued_jobs=queued_jobs,
            average_execution_time_ms=avg_time,
            success_rate=round(success_rate, 2),
            failure_rate=round(failure_rate, 2),
            recent_activity=recent_activity,
            pipeline_status=status_counts,
            daily_conversions=daily,
            monthly_conversions=monthly,
            error_statistics=error_stats,
            top_failed_pipelines=top_failed,
            airflow_status={"status": "healthy", "active_dags": 1},
            datadog_status={"status": "connected", "monitors_active": True},
            latest_reports=latest_reports,
            latest_logs=latest_logs,
        )

    async def _get_average_execution_time(self) -> float:
        result = await self.db.execute(
            select(func.avg(PipelineExecution.execution_time_ms)).where(
                PipelineExecution.execution_time_ms.isnot(None)
            )
        )
        return float(result.scalar() or 0)

    async def _get_daily_conversions(self) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        bind = self.db.get_bind()
        is_sqlite = bind.dialect.name == "sqlite"
        date_col = func.strftime("%Y-%m-%d", Pipeline.created_at) if is_sqlite else func.date(Pipeline.created_at)
        result = await self.db.execute(
            select(
                date_col.label("date"),
                func.count(Pipeline.id).label("count"),
            )
            .where(Pipeline.created_at >= since)
            .group_by(date_col)
            .order_by(date_col)
        )
        return [{"date": str(row.date), "count": row.count} for row in result.all()]

    async def _get_monthly_conversions(self) -> list[dict]:
        bind = self.db.get_bind()
        is_sqlite = bind.dialect.name == "sqlite"
        month_col = func.strftime("%Y-%m", Pipeline.created_at) if is_sqlite else func.date_trunc("month", Pipeline.created_at)
        result = await self.db.execute(
            select(
                month_col.label("month"),
                func.count(Pipeline.id).label("count"),
            )
            .group_by(month_col)
            .order_by(month_col)
        )
        return [{"month": str(row.month), "count": row.count} for row in result.all()]

    async def _get_error_statistics(self) -> list[dict]:
        result = await self.db.execute(
            select(LogEntry.level, func.count(LogEntry.id))
            .where(LogEntry.level.in_(["ERROR", "WARNING"]))
            .group_by(LogEntry.level)
        )
        return [{"level": level, "count": count} for level, count in result.all()]

    async def _get_top_failed(self) -> list[dict]:
        failed = await self.pipeline_repo.get_failed_pipelines(5)
        return [{"id": str(p.id), "name": p.name, "path": p.path} for p in failed]

    async def _get_latest_reports(self) -> list[dict]:
        result = await self.db.execute(
            select(ValidationReport).order_by(ValidationReport.created_at.desc()).limit(5)
        )
        reports = result.scalars().all()
        return [
            {
                "id": str(r.id),
                "pipeline_id": str(r.pipeline_id),
                "status": r.status.value,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ]

    async def _get_latest_logs(self) -> list[dict]:
        logs = await self.log_repo.get_recent(10)
        return [
            {
                "id": str(log.id),
                "level": log.level,
                "module": log.module,
                "message": log.message[:200],
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]

    async def record_metric(self, name: str, value: float, extra: dict | None = None) -> None:
        metric = DashboardMetric(
            metric_name=name,
            metric_value=value,
            metric_date=datetime.now(timezone.utc),
            extra_data=extra,
        )
        self.db.add(metric)
        await self.db.flush()
