"""
agent.logger
============

Structured logging for the ReAct agent.

Provides a single configured ``logging.Logger`` named "agent" that writes to:
  - the console (stdout) at INFO level, and
  - a rotating file ``logs/agent.log`` at DEBUG level
    (max 5 MB per file, 3 rotated backups — all configurable).

All other modules obtain the logger via ``get_logger()`` so configuration
happens exactly once.
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

# Module-level flag ensures setup runs only once even if called repeatedly.
_LOGGER_INITIALIZED: bool = False
_LOGGER: Optional[logging.Logger] = None

# The canonical logger name used across the whole project.
LOGGER_NAME = "agent"


def setup_logging(config: Any) -> logging.Logger:
    """
    Configure and return the shared "agent" logger.

    Parameters
    ----------
    config:
        The loaded Config object. Expected to expose a ``logging`` section with
        keys: log_dir, console_level, file_level, max_bytes, backup_count,
        filename, log_truncate_chars.

    Returns
    -------
    logging.Logger
        The configured logger instance.
    """
    global _LOGGER_INITIALIZED, _LOGGER

    if _LOGGER_INITIALIZED and _LOGGER is not None:
        return _LOGGER

    log_cfg = config.logging
    log_dir = Path(str(log_cfg.get("log_dir", "logs")))
    # Create the log directory eagerly so the file handler never fails.
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter levels.
    # Prevent duplicate handlers if this is somehow called twice before the flag
    # is set (e.g. during tests).
    logger.handlers.clear()
    logger.propagate = False  # avoid double-printing via the root logger.

    # --- Console handler (INFO) -------------------------------------------------
    console_level = _parse_level(str(log_cfg.get("console_level", "INFO")))
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(console_handler)

    # --- Rotating file handler (DEBUG) -----------------------------------------
    file_level = _parse_level(str(log_cfg.get("file_level", "DEBUG")))
    file_path = log_dir / str(log_cfg.get("filename", "agent.log"))
    file_handler = RotatingFileHandler(
        filename=str(file_path),
        maxBytes=int(log_cfg.get("max_bytes", 5 * 1024 * 1024)),
        backupCount=int(log_cfg.get("backup_count", 3)),
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(
        logging.Formatter(
            fmt=(
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    _LOGGER = logger
    _LOGGER_INITIALIZED = True
    logger.debug("Logging initialized. File target: %s", file_path)
    return logger


def get_logger() -> logging.Logger:
    """
    Return the shared "agent" logger.

    If logging has not been set up yet (e.g. a module is imported before
    ``main`` calls ``setup_logging``), a bare logger is returned with a
    console handler so messages are still visible. This makes modules safe to
    import in any order.
    """
    global _LOGGER_INITIALIZED, _LOGGER
    if _LOGGER_INITIALIZED and _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def _parse_level(name: str) -> int:
    """Map a level string ('DEBUG', 'INFO', ...) to a logging int."""
    level = getattr(logging, name.upper(), None)
    if not isinstance(level, int):
        return logging.INFO
    return level


def truncate(text: str, max_chars: int = 500) -> str:
    """
    Truncate a string to ``max_chars`` characters, appending an ellipsis when
    truncated. Used to keep log entries readable.
    """
    if text is None:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"... [+{len(text) - max_chars} chars]"
