"""Datadog monitoring integration."""

import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatadogService:
    def __init__(self):
        self._initialized = False
        if settings.dd_api_key and settings.dd_trace_enabled:
            try:
                from ddtrace import patch_all
                patch_all()
                self._initialized = True
                logger.info("Datadog tracing initialized")
            except ImportError:
                logger.warning("ddtrace not available")

    def increment(self, metric: str, value: int = 1, tags: list[str] | None = None) -> None:
        if not settings.dd_api_key:
            logger.debug("Datadog metric (local): %s=%d tags=%s", metric, value, tags)
            return
        try:
            from datadog import initialize, statsd
            initialize(api_key=settings.dd_api_key, app_key=settings.dd_app_key)
            statsd.increment(metric, value, tags=tags or [])
        except Exception as e:
            logger.error("Failed to send Datadog metric: %s", e)

    def gauge(self, metric: str, value: float, tags: list[str] | None = None) -> None:
        if not settings.dd_api_key:
            logger.debug("Datadog gauge (local): %s=%f", metric, value)
            return
        try:
            from datadog import initialize, statsd
            initialize(api_key=settings.dd_api_key, app_key=settings.dd_app_key)
            statsd.gauge(metric, value, tags=tags or [])
        except Exception as e:
            logger.error("Failed to send Datadog gauge: %s", e)

    def log_event(self, title: str, text: str, alert_type: str = "info", tags: list[str] | None = None) -> None:
        logger.info("Datadog event: %s - %s", title, text)
        if not settings.dd_api_key:
            return
        try:
            from datadog import api, initialize
            initialize(api_key=settings.dd_api_key, app_key=settings.dd_app_key)
            api.Event.create(title=title, text=text, alert_type=alert_type, tags=tags or [])
        except Exception as e:
            logger.error("Failed to send Datadog event: %s", e)

    def get_status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "service": settings.dd_service,
            "env": settings.dd_env,
            "trace_enabled": settings.dd_trace_enabled,
            "status": "connected" if settings.dd_api_key else "not_configured",
        }
