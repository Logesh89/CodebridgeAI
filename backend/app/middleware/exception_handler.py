"""Centralized exception handling middleware."""

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AppException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.message, "errors": e.details},
            )
        except Exception as e:
            logger.exception("Unhandled exception: %s", e)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
