"""Main tool definitions for LLM.txt MCP server."""

import logging
from typing import Any, Dict, List, Optional

from ..models.service import LLMTextService

logger = logging.getLogger(__name__)

# Global service instance
_service_instance: Optional[LLMTextService] = None


def get_service() -> LLMTextService:
    """Get or create the global service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = LLMTextService()
    return _service_instance


# Tool functions (decorators will be applied when server.py imports this module)
async def generate_llms_txt_tool(
    project_path: str,
    output_path: Optional[str] = None,
    include_optional: bool = True,
    scan_depth: int = 3,
) -> Dict[str, Any]:
    """Generate llms.txt files for a project."""
    try:
        logger.info(f"Generating llms.txt for project: {project_path}")
        service = get_service()

        result = await service.generate_project_llms_txt(
            project_path=project_path,
            output_path=output_path,
            include_optional=include_optional,
            scan_depth=scan_depth,
        )

        logger.info(f"Successfully generated llms.txt files: {result}")
        return result

    except Exception as e:
        logger.error(f"Error generating llms.txt for {project_path}: {e}")
        raise


async def validate_llms_txt_tool(file_path: str) -> Dict[str, Any]:
    """Validate an llms.txt file."""
    try:
        logger.info(f"Validating llms.txt file: {file_path}")
        service = get_service()

        result = await service.validate_llms_txt(file_path=file_path)

        logger.info(f"Validation completed for {file_path}: {result}")
        return result

    except Exception as e:
        logger.error(f"Error validating llms.txt file {file_path}: {e}")
        raise


async def update_llms_txt_tool(
    project_path: str,
    regenerate_sections: Optional[List[str]] = None,
    preserve_custom_content: bool = True,
) -> Dict[str, Any]:
    """Update an existing llms.txt file."""
    try:
        logger.info(f"Updating llms.txt for project: {project_path}")
        service = get_service()

        result = await service.update_llms_txt(
            project_path=project_path,
            regenerate_sections=regenerate_sections,
            preserve_custom_content=preserve_custom_content,
        )

        logger.info(f"Successfully updated llms.txt: {result}")
        return result

    except Exception as e:
        logger.error(f"Error updating llms.txt for {project_path}: {e}")
        raise


async def convert_to_context_tool(
    llms_txt_path: str, output_format: str = "xml", include_optional: bool = False
) -> Dict[str, Any]:
    """Convert llms.txt to LLM context format."""
    try:
        logger.info(f"Converting llms.txt to {output_format}: {llms_txt_path}")
        service = get_service()

        result = await service.convert_to_context(
            llms_txt_path=llms_txt_path,
            output_format=output_format,
            include_optional=include_optional,
        )

        logger.info(f"Successfully converted llms.txt: {result}")
        return result

    except Exception as e:
        logger.error(f"Error converting llms.txt {llms_txt_path}: {e}")
        raise


async def scan_project_structure_tool(
    project_path: str, scan_depth: int = 3, include_hidden: bool = False
) -> Dict[str, Any]:
    """Scan and analyze project structure."""
    try:
        logger.info(f"Scanning project structure: {project_path}")
        service = get_service()

        result = await service.scan_project_structure(
            project_path=project_path, scan_depth=scan_depth, include_hidden=include_hidden
        )

        logger.info(f"Project structure scan completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error scanning project structure {project_path}: {e}")
        raise


async def generate_from_template_tool(
    project_path: str,
    template_name: str = "generic",
    custom_sections: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Generate llms.txt from a template."""
    try:
        logger.info(f"Generating llms.txt from template '{template_name}' for: {project_path}")
        service = get_service()

        result = await service.generate_from_template(
            project_path=project_path, template_name=template_name, custom_sections=custom_sections
        )

        logger.info(f"Template generation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error generating from template {template_name} for {project_path}: {e}")
        raise


# Include additional tools

# Export tool functions for registration
__all__ = [
    "generate_llms_txt_tool",
    "validate_llms_txt_tool",
    "update_llms_txt_tool",
    "convert_to_context_tool",
    "scan_project_structure_tool",
    "generate_from_template_tool",
    "get_service",
]
