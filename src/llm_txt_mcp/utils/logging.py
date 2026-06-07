"""Structured logging configuration for LLM.txt MCP server."""

import json
import logging
import sys
from datetime import datetime
from typing import Any


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add context if present
        if hasattr(record, "context"):
            log_data["context"] = record.context

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    use_json: bool = True,
    stream: Any | None = None,
) -> None:
    """
    Set up structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (default: True)
        stream: Output stream (default: sys.stderr for MCP compatibility)
    """
    if stream is None:
        stream = sys.stderr  # Use stderr to avoid conflicts with stdio transport

    log_level = getattr(logging, level.upper(), logging.INFO)

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(log_level)

    # Set formatter
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
    """
    Log a message with additional context.

    Args:
        logger: Logger instance
        level: Logging level
        message: Log message
        context: Additional context dictionary
        **kwargs: Additional fields to include in log
    """
    extra: dict[str, Any] = {}
    if context:
        extra["context"] = context
    if kwargs:
        extra["extra_fields"] = kwargs

    logger.log(level, message, extra=extra)
