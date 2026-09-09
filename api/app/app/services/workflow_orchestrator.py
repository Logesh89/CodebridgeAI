"""Pipeline conversion workflow orchestrator."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, JobStatus, PipelineStatus
from app.repositories.pipeline_repository import PipelineRepository
from app.services.ai_conversion_service import AIConversionService
from app.services.datadog_service import DatadogService
from app.services.execution_service import ExecutionService
from app.services.notification_service import NotificationService
from app.services.snaplogic_service import SnapLogicService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pipeline_repo = PipelineRepository(db)
        self.snaplogic_service = SnapLogicService()
        self.ai_service = AIConversionService(db)
        self.execution_service = ExecutionService(db)
        self.validation_service = ValidationService(db)
        self.notification_service = NotificationService(db)
        self.datadog = DatadogService()

    async def run_full_conversion(self, pipeline_id: uuid.UUID, user_id: uuid.UUID, user_email: str) -> dict:
        pipeline = await self.pipeline_repo.get_by_id(pipeline_id)
        if not pipeline:
            raise ValueError("Pipeline not found")

        job = Job(
            pipeline_id=pipeline_id,
            job_type="full_conversion",
            status=JobStatus.RUNNING,
            progress=0,
        )
        self.db.add(job)
        await self.db.flush()

        try:
            pipeline.status = PipelineStatus.RUNNING
            await self.pipeline_repo.update(pipeline)
            await self.notification_service.notify_conversion_started(user_id, pipeline.name, user_email)
            self.datadog.increment("conversion.started", tags=[f"pipeline:{pipeline.name}"])

            job.progress = 10
            import json
            from pathlib import Path
            if pipeline.snaplogic_json_path and Path(pipeline.snaplogic_json_path).exists():
                json_path = pipeline.snaplogic_json_path
                xml_path = str(Path(json_path).with_suffix(".xml"))
                if not Path(xml_path).exists():
                    try:
                        content = json.loads(Path(json_path).read_text(encoding="utf-8", errors="ignore"))
                        xml_content = self.snaplogic_service._convert_to_xml(content)
                        Path(xml_path).write_text(xml_content, encoding="utf-8")
                    except Exception:
                        Path(xml_path).write_text("<pipeline></pipeline>", encoding="utf-8")
            else:
                json_path, xml_path = await self.snaplogic_service.download_and_store(
                    pipeline.path, str(pipeline_id)
                )
                pipeline.snaplogic_json_path = json_path
                pipeline.snaplogic_xml_path = xml_path

            pipeline.status = PipelineStatus.CONVERTING
            await self.pipeline_repo.update(pipeline)
            job.progress = 30

            conversion = await self.ai_service.convert_pipeline(str(pipeline_id), json_path, xml_path)
            job.progress = 50

            pipeline.status = PipelineStatus.EXECUTING
            await self.pipeline_repo.update(pipeline)

            snap_exec = await self.execution_service.execute_snaplogic(pipeline_id, pipeline.path)
            job.progress = 65

            python_exec = await self.execution_service.execute_python(
                pipeline_id, conversion.output_file_path or ""
            )
            job.progress = 80

            pipeline.status = PipelineStatus.VALIDATING
            await self.pipeline_repo.update(pipeline)

            report = await self.validation_service.compare_outputs(
                pipeline_id,
                snap_exec.output_path or "",
                python_exec.output_path or "",
            )
            job.progress = 100
            job.status = JobStatus.COMPLETED

            if report.status.value == "passed":
                pipeline.status = PipelineStatus.COMPLETED
                await self.pipeline_repo.update(pipeline)
                await self.notification_service.notify_conversion_completed(user_id, pipeline.name, user_email)
                self.datadog.increment("conversion.success")
            else:
                pipeline.status = PipelineStatus.FAILED
                await self.pipeline_repo.update(pipeline)
                await self.notification_service.notify_validation_failed(user_id, pipeline.name, user_email)
                self.datadog.increment("conversion.validation_failed")

            return {
                "pipeline_id": str(pipeline_id),
                "status": report.status.value,
                "job_id": str(job.id),
            }

        except Exception as e:
            logger.error("Workflow failed for pipeline %s: %s", pipeline_id, e)
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            pipeline.status = PipelineStatus.FAILED
            await self.pipeline_repo.update(pipeline)
            self.datadog.increment("conversion.failed")
            raise

        finally:
            await self.db.flush()
