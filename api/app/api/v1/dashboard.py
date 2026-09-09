"""Dashboard API routes."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(user: CurrentUser, db: DbSession):
    service = DashboardService(db)
    return await service.get_dashboard()
