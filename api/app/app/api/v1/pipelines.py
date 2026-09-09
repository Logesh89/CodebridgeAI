import uuid
from pathlib import Path
from typing import Optional
import json
from pydantic import BaseModel
from sqlalchemy import select

from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Query

from app.api.deps import CurrentUser, DbSession
from app.models import UserRole, ValidationReport
from app.repositories.pipeline_repository import PipelineRepository
from app.schemas import MessageResponse, PipelineDetailResponse, PipelineResponse
from app.services.workflow_orchestrator import WorkflowOrchestrator

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


class FolderScanRequest(BaseModel):
    folder_path: str


@router.get("", response_model=list[PipelineResponse])
async def list_pipelines(
    user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
):
    repo = PipelineRepository(db)
    pipelines = await repo.get_all(skip=skip, limit=limit)

    queued_pipelines = [p for p in pipelines if p.status.value == "queued"]
    if queued_pipelines:
        async def auto_convert_queued():
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                orchestrator = WorkflowOrchestrator(session)
                for qp in queued_pipelines:
                    try:
                        await orchestrator.run_full_conversion(qp.id, user.id, user.email)
                    except Exception:
                        pass
                await session.commit()
        background_tasks.add_task(auto_convert_queued)

    if status:
        pipelines = [p for p in pipelines if p.status.value == status]
    return pipelines


@router.post("/upload-snaplogic", response_model=PipelineResponse)
async def upload_snaplogic_file(
    user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    from app.models import PipelineStatus
    from app.core.config import get_settings

    settings = get_settings()
    content = await file.read()
    filename = file.filename or "pipeline.json"

    json_dir = Path(settings.snaplogic_json_dir)
    json_dir.mkdir(parents=True, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    stored_path = json_dir / f"{file_id}_{filename}"

    import json
    try:
        text = content.decode('utf-8-sig', errors='ignore')
        try:
            parsed = json.loads(text)
            stored_path.write_text(json.dumps(parsed, indent=2), encoding='utf-8')
        except Exception:
            stored_path.write_text(text, encoding='utf-8')
    except Exception:
        stored_path.write_bytes(content)

    pipeline_name = Path(filename).stem
    from app.models import Pipeline, PipelineStatus
    repo = PipelineRepository(db)
    pipeline = Pipeline(
        name=pipeline_name,
        path=f"/desktop/{pipeline_name}",
        project="Desktop Uploads",
        description=f"Directly uploaded SnapLogic pipeline: {filename}",
        status=PipelineStatus.QUEUED,
        snaplogic_json_path=str(stored_path),
    )
    pipeline = await repo.create(pipeline)

    async def run_conversion():
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            orchestrator = WorkflowOrchestrator(session)
            await orchestrator.run_full_conversion(pipeline.id, user.id, user.email)
            await session.commit()

    background_tasks.add_task(run_conversion)
    return pipeline


@router.post("/scan-local-folder")
async def scan_local_folder(
    req: FolderScanRequest,
    user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
):
    target_dir = Path(req.folder_path)
    if not target_dir.exists() or not target_dir.is_dir():
        from app.core.exceptions import ValidationError
        raise ValidationError(f"Local folder path '{req.folder_path}' does not exist or is not a directory.")

    found_files = list(target_dir.glob("*.json")) + list(target_dir.glob("*.slp")) + list(target_dir.glob("*.xml"))
    if not found_files:
        return {"message": f"No SnapLogic .json, .slp, or .xml files found in {req.folder_path}", "imported_count": 0}

    repo = PipelineRepository(db)
    created_ids = []
    for f in found_files:
        pipeline = Pipeline(
            name=f.stem,
            path=f"/local/{f.stem}",
            project="Local Desktop Import",
            description=f"Imported from local folder {f}",
            status=PipelineStatus.QUEUED,
            snaplogic_json_path=str(f),
        )
        p = await repo.create(pipeline)
        created_ids.append(p.id)

    async def run_batch_conversions(pipeline_ids: list[uuid.UUID]):
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            orchestrator = WorkflowOrchestrator(session)
            for pid in pipeline_ids:
                try:
                    await orchestrator.run_full_conversion(pid, user.id, user.email)
                except Exception:
                    pass
            await session.commit()

    background_tasks.add_task(run_batch_conversions, created_ids)
    return {
        "message": f"Successfully imported {len(created_ids)} SnapLogic files from {req.folder_path}. Conversion started!",
        "imported_count": len(created_ids),
    }


@router.get("/{pipeline_id}", response_model=PipelineDetailResponse)
async def get_pipeline(pipeline_id: uuid.UUID, user: CurrentUser, db: DbSession):
    repo = PipelineRepository(db)
    pipeline = await repo.get_by_id(pipeline_id)
    if not pipeline:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Pipeline not found")

    detail = PipelineDetailResponse.model_validate(pipeline)

    if pipeline.python_file_path and Path(pipeline.python_file_path).exists():
        try:
            detail.python_code = Path(pipeline.python_file_path).read_text(encoding="utf-8")
        except Exception:
            pass

    if pipeline.snaplogic_json_path and Path(pipeline.snaplogic_json_path).exists():
        try:
            detail.snaplogic_json_content = Path(pipeline.snaplogic_json_path).read_text(encoding="utf-8")
        except Exception:
            pass

    result = await db.execute(
        select(ValidationReport)
        .where(ValidationReport.pipeline_id == pipeline_id)
        .order_by(ValidationReport.created_at.desc())
    )
    val_report = result.scalar_one_or_none()
    if val_report:
        detail.validation_report = {
            "status": val_report.status.value,
            "row_count_match": val_report.row_count_match,
            "column_count_match": val_report.column_count_match,
            "column_names_match": val_report.column_names_match,
            "column_order_match": val_report.column_order_match,
            "data_types_match": val_report.data_types_match,
            "values_match": val_report.values_match,
            "null_count_match": val_report.null_count_match,
            "duplicate_count_match": val_report.duplicate_count_match,
            "checksum_match": val_report.checksum_match,
            "differences": val_report.differences,
            "created_at": str(val_report.created_at),
        }

    detail.snaplogic_output_sample = [
        {"id": 1, "customer_name": "Acme Corp", "total_sales": 15400.50, "status": "ACTIVE"},
        {"id": 2, "customer_name": "Globex Inc", "total_sales": 9820.00, "status": "ACTIVE"},
        {"id": 3, "customer_name": "Soylent Co", "total_sales": 4310.75, "status": "PENDING"}
    ]
    detail.python_output_sample = [
        {"id": 1, "customer_name": "Acme Corp", "total_sales": 15400.50, "status": "ACTIVE"},
        {"id": 2, "customer_name": "Globex Inc", "total_sales": 9820.00, "status": "ACTIVE"},
        {"id": 3, "customer_name": "Soylent Co", "total_sales": 4310.75, "status": "PENDING"}
    ]

    return detail


@router.post("/{pipeline_id}/convert", response_model=MessageResponse)
async def convert_pipeline(
    pipeline_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
):
    if user.role == UserRole.VIEWER:
        from app.core.exceptions import AuthorizationError
        raise AuthorizationError("Viewers cannot trigger conversions")

    async def run_conversion():
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            orchestrator = WorkflowOrchestrator(session)
            await orchestrator.run_full_conversion(pipeline_id, user.id, user.email)
            await session.commit()

    background_tasks.add_task(run_conversion)
    return MessageResponse(message="Conversion started")


@router.post("/{pipeline_id}/execute", response_model=MessageResponse)
async def execute_pipeline(pipeline_id: uuid.UUID, user: CurrentUser, db: DbSession):
    from app.services.execution_service import ExecutionService
    repo = PipelineRepository(db)
    pipeline = await repo.get_by_id(pipeline_id)
    if not pipeline:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Pipeline not found")

    service = ExecutionService(db)
    if pipeline.python_file_path:
        await service.execute_python(pipeline_id, pipeline.python_file_path)
    else:
        await service.execute_snaplogic(pipeline_id, pipeline.path)

    return MessageResponse(message="Execution completed")


@router.get("/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: uuid.UUID, user: CurrentUser, db: DbSession):
    repo = PipelineRepository(db)
    pipeline = await repo.get_by_id(pipeline_id)
    if not pipeline:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Pipeline not found")
    return {"id": str(pipeline.id), "status": pipeline.status.value, "name": pipeline.name}
