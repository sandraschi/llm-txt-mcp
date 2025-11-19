"""Status tool for LLM.txt MCP server."""

import logging
import platform
from datetime import datetime
from typing import Any, Dict

import psutil

from .tools import get_service

logger = logging.getLogger(__name__)


# Tool functions without decorators - will be registered in server.py
async def status_tool(
    include_system_info: bool = False, include_performance_metrics: bool = False
) -> Dict[str, Any]:
    """
    Get comprehensive server status and health information.

    This tool provides detailed information about the server status, system resources,
    configuration, and operational metrics for monitoring and troubleshooting.

    Parameters:
        include_system_info (bool, optional): Include detailed system information
        include_performance_metrics (bool, optional): Include performance metrics

    Returns:
        dict: Server status with health, configuration, and metrics
    """
    try:
        logger.info("Getting server status")

        status = {
            "server_name": "LLM.txt MCP Server",
            "version": "0.1.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": "N/A",  # Would need to track server start time
            "configuration": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "mcp_server": "FastMCP 2.12+",
                "features": [
                    "llms.txt generation",
                    "validation",
                    "template system",
                    "multi-format conversion",
                    "project analysis",
                ],
            },
            "tools_registered": [
                "generate_llms_txt",
                "validate_llms_txt",
                "update_llms_txt",
                "convert_to_context",
                "scan_project_structure",
                "generate_from_template",
                "help",
                "status",
                "analyze_repo",
            ],
            "errors": [],
            "warnings": [],
        }

        # Add system information if requested
        if include_system_info:
            try:
                status["system"] = {
                    "cpu_count": psutil.cpu_count(),
                    "memory": {
                        "total": psutil.virtual_memory().total,
                        "available": psutil.virtual_memory().available,
                        "percent": psutil.virtual_memory().percent,
                    },
                    "disk": {
                        "total": psutil.disk_usage("/").total,
                        "free": psutil.disk_usage("/").free,
                        "percent": psutil.disk_usage("/").percent,
                    },
                }
            except Exception as e:
                logger.warning(f"Could not get system info: {e}")
                status["warnings"].append("System information unavailable")

        # Add performance metrics if requested
        if include_performance_metrics:
            try:
                status["performance"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": {
                        "read_count": psutil.disk_io_counters().read_count,
                        "write_count": psutil.disk_io_counters().write_count,
                    },
                }
            except Exception as e:
                logger.warning(f"Could not get performance metrics: {e}")
                status["warnings"].append("Performance metrics unavailable")

        # Check service health
        try:
            service = get_service()
            # Test if service is responsive
            templates = service.templates
            if templates:
                status["service_status"] = "healthy"
                status["available_templates"] = list(templates.keys())
            else:
                status["service_status"] = "degraded"
                status["warnings"].append("Service templates not loaded")
        except Exception as e:
            logger.error(f"Service health check failed: {e}")
            status["service_status"] = "unhealthy"
            status["errors"].append(f"Service error: {str(e)}")
            status["status"] = "unhealthy"

        # Overall status determination
        if status["errors"]:
            status["status"] = "unhealthy"
        elif status["warnings"]:
            status["status"] = "degraded"

        logger.info(f"Status check completed: {status['status']}")
        return status

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise


async def health_check_tool() -> Dict[str, Any]:
    """Perform a quick health check of the server."""
    try:
        logger.info("Performing health check")

        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "server_responsive": True,
                "service_available": False,
                "tools_registered": True,
            },
            "issues": [],
        }

        # Test service availability
        try:
            service = get_service()
            if hasattr(service, "templates") and service.templates:
                health["checks"]["service_available"] = True
            else:
                health["issues"].append("Service templates not available")
        except Exception as e:
            health["checks"]["service_available"] = False
            health["issues"].append(f"Service error: {str(e)}")

        # Determine overall health
        if not health["checks"]["service_available"]:
            health["status"] = "unhealthy"

        logger.info(f"Health check completed: {health['status']}")
        return health

    except Exception as e:
        logger.error(f"Error during health check: {e}")
        raise


__all__ = ["status_tool", "health_check_tool"]
