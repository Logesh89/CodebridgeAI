"""Application logging configuration."""

import logging
import os
import sys
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]

    is_vercel = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    if not is_vercel:
        try:
            log_dir = Path(settings.logs_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_dir / "app.log"))
        except Exception:
            pass

    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format=log_format,
        handlers=handlers,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
