"""
Thread-safe, structured logging system for Quiz Studio using Rich and Python standard logging.
Provides colorized console output and detailed file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler

from config import config

# Singleton Console for Rich
console = Console()


class QuizStudioLogger:
    """Centralized logging framework supporting console and file outputs."""

    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Retrieves or initializes the global thread-safe logger."""
        if cls._logger is not None:
            return cls._logger

        logger_name = "QuizStudio"
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
        logger.propagate = False

        if not logger.handlers:
            # Rich Console Handler
            rich_handler = RichHandler(
                console=console,
                rich_tracebacks=True,
                show_time=True,
                show_path=False,
                markup=True,
            )
            rich_handler.setLevel(logging.INFO)
            rich_format = logging.Formatter("%(message)s")
            rich_handler.setFormatter(rich_format)
            logger.addHandler(rich_handler)

            # Log File Handler
            log_dir = config.paths.base_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "quiz_studio.log"

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(threadName)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

        cls._logger = logger
        return cls._logger


# Global Logger Singleton
logger = QuizStudioLogger.get_logger()
