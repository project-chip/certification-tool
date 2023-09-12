from __future__ import annotations

import logging
import sys
from pathlib import Path
from types import FrameType

from loguru import logger
from notifiers.logging import NotificationHandler

from app.core.config import settings


class LoggingConfigError(Exception):
    """Raised when config parameters are missing or don't align"""


class InterceptHandler(logging.Handler):
    """This class is used to intercept the standard python logging.
    To enable it, you must call.

    This is based on boilerplate code from the loguru project

    `logging.basicConfig(handlers=[InterceptHandler()], level=0)`
    """

    # used when extracting depth from stack trace
    __initial_stack_depth = 2

    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def __init__(self, log_source: str) -> None:
        super().__init__()
        self.log_source = log_source

    def emit(self, record: logging.LogRecord) -> None:
        """This will be called by the standard logging module on each log call

        Args:
            record (logging.LogRecord): The log record intercepted from the standard
            logging module
        """

        # Attempt to extract the log-level from the log record
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        # Extract the depth
        frame: FrameType = logging.currentframe()
        depth = self.__initial_stack_depth
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back is not None:
                frame = frame.f_back
                depth += 1
            else:
                depth += 1
                break

        # add log_source as extra info to all log-records for loguru
        app_logger = logger.bind(log_source=self.log_source)

        # add log entry in loguru log, matching the original log record from the
        # standard logging module
        app_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    project_root = Path(Path(__file__).parents[1])
    log_file_path = (
        project_root / Path(settings.LOGGING_PATH) / settings.LOGGING_FILENAME
    )
    __configure_logging(
        filepath=log_file_path,
        level=settings.LOGGING_LEVEL,
        rotation=settings.LOGGING_ROTATION,
        retention=settings.LOGGING_RETENTION,
        format=settings.LOGGING_FORMAT,
    )

    __configure_notifier_handler()


def __configure_notifier_handler() -> None:
    if settings.NOTIFIER_ENABLE_NOTIFICATIONS is False:
        logger.info("Exception notifier not enabled")
        return

    defaults = {
        "username": settings.NOTIFIER_USERNAME,
        "password": settings.NOTIFIER_PASSWORD,
        "to": settings.NOTIFIER_TO,
        "subject": settings.NOTIFIER_SUBJECT,
    }

    handler = NotificationHandler("gmail", defaults=defaults)
    logger.add(handler, level=logging.ERROR)


def __configure_logging(
    filepath: Path, level: str, rotation: str, retention: str, format: str
) -> None:
    # Configure default log source
    logger.configure(extra={"log_source": "unknown"})

    # Reset (Remove all sinks from logger)
    logger.remove()

    # Add logging output to stdout (colorize when stdout is attach to a real terminal)
    colorize = sys.stdout.isatty()
    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        level=level.upper(),
        format=format,
        colorize=colorize,
    )

    # Add logging output to file
    logger.add(
        str(filepath),
        rotation=rotation,
        retention=retention,
        enqueue=True,
        backtrace=True,
        level=level.upper(),
        format=format,
    )

    # Configure standard logging to be Intercepted.
    logging.basicConfig(
        handlers=[InterceptHandler(log_source="standard logging")], level=0
    )

    # Intercept all uvicorn and fastapi logging.
    for _log in [
        "uvicorn",
        "uvicorn.asgi",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "websockets",
    ]:
        _logger = logging.getLogger(_log)
        _logger.propagate = False
        _logger.handlers = [InterceptHandler(log_source=_log)]
