"""Logging configuration."""

import logging
from logging.handlers import RotatingFileHandler


def configure_logging(level: str = "INFO", logfile: str = "app.log") -> None:
    handler = RotatingFileHandler(logfile, maxBytes=1024 * 1024, backupCount=3)
    logging.basicConfig(level=level, handlers=[handler])
