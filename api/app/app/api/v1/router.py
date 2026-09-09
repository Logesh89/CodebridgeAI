"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import auth, dashboard, excel, interpreter, pipelines, reports, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(dashboard.router)
api_router.include_router(excel.router)
api_router.include_router(interpreter.router)
api_router.include_router(pipelines.router)
api_router.include_router(reports.reports_router)
api_router.include_router(reports.logs_router)
api_router.include_router(reports.downloads_router)
api_router.include_router(reports.notifications_router)
