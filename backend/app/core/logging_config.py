"""Application logging configuration."""

import logging
import sys
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    log_dir = Path(settings.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log"),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
