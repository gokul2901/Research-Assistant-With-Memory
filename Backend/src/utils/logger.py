"""
Structured logging configuration using Loguru.
Provides contextual and formatted log output for development and production.
"""

import sys
import logging
from loguru import logger
from src.config.settings import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard Python logging messages and route them through Loguru.
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure Loguru logging format and handlers."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    log_level = "DEBUG" if settings.DEBUG else "INFO"

    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True,
        enqueue=True,
    )

    # Intercept standard library logging (uvicorn, fastapi, chromadb, litellm)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for uvicorn_logger in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "chromadb", "LiteLLM"):
        logging.getLogger(uvicorn_logger).handlers = [InterceptHandler()]


__all__ = ["logger", "setup_logging"]
