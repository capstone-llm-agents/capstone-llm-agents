"""Logging utilities for the application."""

import logging
from pathlib import Path


def setup_file_only_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Create a logger that only writes to file, no console output."""
    # ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # remove any existing handlers to start fresh
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # prevent propagation to root logger (this prevents console output)
    logger.propagate = False

    return logger


APP_LOGGER = setup_file_only_logger("textual_app", "./logs/app.log", logging.DEBUG)
