"""Central bounded logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_file_logging(
    log_file: Path,
    *,
    level: int = logging.INFO,
    max_bytes: int = 2_000_000,
    backup_count: int = 3,
) -> logging.Logger:
    """Create one bounded UTF-8 rotating logger without duplicate handlers."""

    if max_bytes <= 0:
        raise ValueError("max_bytes must be greater than zero")
    if backup_count < 0:
        raise ValueError("backup_count must not be negative")

    log_file = log_file.expanduser().resolve(strict=False)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("mastercore")
    logger.setLevel(level)
    logger.propagate = False

    resolved = str(log_file)
    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            if str(Path(handler.baseFilename).resolve(strict=False)) == resolved:
                handler.setLevel(level)
                return logger

    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    )
    logger.addHandler(handler)
    return logger
