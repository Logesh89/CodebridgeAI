"""Excel upload API routes."""

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from app.api.deps import CurrentUser, DbSession
from app.schemas import ExcelUploadResponse
from app.services.excel_service import ExcelService

router = APIRouter(prefix="/excel", tags=["Excel"])


@router.post("/upload", response_model=ExcelUploadResponse)
async def upload_excel(
    user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    content = await file.read()
    service = ExcelService(db)
    result = await service.process_upload(content, file.filename or "upload.xlsx", user.id)

    async def auto_convert_batch(batch_id: str, user_id, user_email):
        from app.core.database import AsyncSessionLocal
        from app.repositories.pipeline_repository import PipelineRepository
        from app.services.workflow_orchestrator import WorkflowOrchestrator
        async with AsyncSessionLocal() as session:
            repo = PipelineRepository(session)
            pipelines = await repo.get_all(limit=100)
            batch_pipelines = [p for p in pipelines if p.upload_batch_id == batch_id]
            for p in batch_pipelines:
                try:
                    orchestrator = WorkflowOrchestrator(session)
                    await orchestrator.run_full_conversion(p.id, user_id, user_email)
                except Exception:
                    pass
            await session.commit()

    if result.pipelines_created > 0:
        background_tasks.add_task(auto_convert_batch, result.batch_id, user.id, user.email)

    return result
