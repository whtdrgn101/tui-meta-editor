"""Logging configuration for Media Organizer."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int | str = logging.INFO,
    logger_name: str = "media_organizer",
) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        level: Logging level (int or string like "INFO", "DEBUG").
        logger_name: Name for the logger.

    Returns:
        Configured logger instance.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger(logger_name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name. If None, returns the root media_organizer logger.
              If provided, returns a child logger (media_organizer.name).

    Returns:
        Logger instance.
    """
    base_name = "media_organizer"
    if name:
        return logging.getLogger(f"{base_name}.{name}")
    return logging.getLogger(base_name)
