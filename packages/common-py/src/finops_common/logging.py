"""Structured logging with trace context."""
import logging
import sys
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from finops_common.context import get_org_id, get_request_id, get_tenant_id, get_user_id


class ContextJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that includes request context."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields including context to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add context fields
        request_id = get_request_id()
        if request_id:
            log_record["request_id"] = request_id

        org_id = get_org_id()
        if org_id:
            log_record["org_id"] = org_id

        tenant_id = get_tenant_id()
        if tenant_id:
            log_record["tenant_id"] = tenant_id

        user_id = get_user_id()
        if user_id:
            log_record["user_id"] = user_id

        # Add standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # Add trace context if available (from OpenTelemetry)
        try:
            from opentelemetry import trace

            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                ctx = span.get_span_context()
                log_record["trace_id"] = format(ctx.trace_id, "032x")
                log_record["span_id"] = format(ctx.span_id, "016x")
        except ImportError:
            pass


def setup_logging(
    level: str = "INFO",
    json_logs: bool = True,
    service_name: Optional[str] = None,
) -> None:
    """Setup application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Enable JSON formatted logs
        service_name: Service name to include in logs
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if json_logs:
        formatter = ContextJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            timestamp=True,
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set service name in logger if provided
    if service_name:
        logging.getLogger().name = service_name


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
