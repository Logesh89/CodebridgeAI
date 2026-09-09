"""Python and SnapLogic execution engine."""

import asyncio
import logging
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import PipelineExecution
from app.services.snaplogic_service import SnapLogicService

logger = logging.getLogger(__name__)
settings = get_settings()


class ExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.snaplogic_service = SnapLogicService()

    async def execute_python(
        self,
        pipeline_id: uuid.UUID,
        python_file_path: str,
    ) -> PipelineExecution:
        logger.info("Executing Python file: %s", python_file_path)
        execution = PipelineExecution(
            pipeline_id=pipeline_id,
            execution_type="python",
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(execution)
        await self.db.flush()

        start_time = time.time()
        import sys
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, python_file_path],
                capture_output=True,
                text=True,
                timeout=300,
            )

            execution.stdout = result.stdout
            execution.stderr = result.stderr
            execution.exit_code = result.returncode
            execution.status = "completed" if result.returncode == 0 else "failed"
            execution.execution_time_ms = (time.time() - start_time) * 1000
            execution.completed_at = datetime.now(timezone.utc)

            output_dir = Path(settings.temp_dir) / "python_output"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pipeline_id}.json"
            output_path.write_text(result.stdout or "{}")
            execution.output_path = str(output_path)
            execution.output_format = "json"

        except subprocess.TimeoutExpired:
            execution.status = "failed"
            execution.stderr = "Execution timed out after 300 seconds"
            execution.exit_code = -1
            execution.execution_time_ms = (time.time() - start_time) * 1000
            execution.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(execution)
        return execution

    async def execute_snaplogic(
        self,
        pipeline_id: uuid.UUID,
        pipeline_path: str,
    ) -> PipelineExecution:
        logger.info("Executing SnapLogic pipeline: %s", pipeline_path)
        execution = PipelineExecution(
            pipeline_id=pipeline_id,
            execution_type="snaplogic",
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(execution)
        await self.db.flush()

        start_time = time.time()
        try:
            run_data = await self.snaplogic_service.execute_pipeline(pipeline_path)
            output_path = await self.snaplogic_service.get_pipeline_output(run_data)

            execution.status = "completed" if run_data.get("status") == "Completed" else "failed"
            execution.output_path = output_path
            execution.output_format = "json"
            execution.stdout = str(run_data)
            execution.exit_code = 0 if execution.status == "completed" else 1
            execution.execution_time_ms = (time.time() - start_time) * 1000
            execution.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            execution.status = "failed"
            execution.stderr = str(e)
            execution.exit_code = -1
            execution.execution_time_ms = (time.time() - start_time) * 1000
            execution.completed_at = datetime.now(timezone.utc)
            logger.error("SnapLogic execution failed: %s", e)

        await self.db.flush()
        await self.db.refresh(execution)
        return execution
