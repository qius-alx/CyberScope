# src/osint/core/logger.py
import logging
import os
from rich.logging import RichHandler
from osint.core.config import settings

def configure_logger():
    """
    Configures the root logger for the application.
    This function should be called once at the beginning of the application,
    after settings have been loaded.
    """
    log = logging.getLogger("osint_framework")
    log.setLevel(settings.log_level.upper())
    log.propagate = False

    # Clear existing handlers
    if log.hasHandlers():
        log.handlers.clear()

    # Check for NO_COLOR env var for rich handler
    if 'NO_COLOR' in os.environ:
        console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False, enable_link_path=False)
    else:
        console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)

    console_handler.setLevel(settings.log_level.upper())
    log.addHandler(console_handler)

    # File handler for structured logging, if a log file is specified
    if settings.log_file:
        try:
            file_handler = logging.FileHandler(settings.log_file, mode='a')
            file_handler.setLevel(settings.log_level.upper())
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            log.addHandler(file_handler)
        except Exception as e:
            log.error(f"Failed to configure file logger at {settings.log_file}: {e}")

# A logger instance to be used across the application.
# It will be configured by `configure_logger()` at runtime.
logger = logging.getLogger("osint_framework")
