"""Main tool definitions for LLM.txt MCP server."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..exceptions import (
    FileOperationError,
    GenerationError,
    ProjectAnalysisError,
    ValidationError,
)
from ..models.service import LLMTextService
from ..utils.logging import get_logger, log_with_context

logger = get_logger(__name__)

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
        # Validate inputs
        if not project_path:
            raise ValidationError("project_path is required", field="project_path")
        
        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise ProjectAnalysisError(
                f"Project path does not exist: {project_path}",
                project_path=project_path,
            )
        
        if not project_path_obj.is_dir():
            raise ProjectAnalysisError(
                f"Project path is not a directory: {project_path}",
                project_path=project_path,
            )

        if scan_depth < 1 or scan_depth > 10:
            raise ValidationError(
                "scan_depth must be between 1 and 10",
                field="scan_depth",
                value=scan_depth,
            )

        log_with_context(
            logger,
            logging.INFO,
            "Generating llms.txt for project",
            context={
                "project_path": project_path,
                "output_path": output_path,
                "include_optional": include_optional,
                "scan_depth": scan_depth,
            },
        )

        service = get_service()
        result = await service.generate_project_llms_txt(
            project_path=project_path,
            output_path=output_path,
            include_optional=include_optional,
            scan_depth=scan_depth,
        )

        log_with_context(
            logger,
            logging.INFO,
            "Successfully generated llms.txt files",
            context={"project_path": project_path, "result": result},
        )
        return result

    except (ValidationError, ProjectAnalysisError, GenerationError) as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error generating llms.txt: {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        logger.exception(f"Unexpected error generating llms.txt for {project_path}")
        raise GenerationError(
            f"Failed to generate llms.txt: {str(e)}",
            generation_type="llms_txt",
        ) from e


async def validate_llms_txt_tool(file_path: str) -> Dict[str, Any]:
    """Validate an llms.txt file."""
    try:
        if not file_path:
            raise ValidationError("file_path is required", field="file_path")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileOperationError(
                f"File does not exist: {file_path}",
                file_path=file_path,
                operation="read",
            )

        log_with_context(
            logger,
            logging.INFO,
            "Validating llms.txt file",
            context={"file_path": file_path},
        )

        service = get_service()
        result = await service.validate_llms_txt(file_path=file_path)

        log_with_context(
            logger,
            logging.INFO,
            "Validation completed",
            context={"file_path": file_path, "is_valid": result.get("is_valid")},
        )
        return result

    except (ValidationError, FileOperationError) as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error validating llms.txt: {e.message}",
            context={"file_path": file_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        logger.exception(f"Unexpected error validating llms.txt file {file_path}")
        raise ValidationError(
            f"Failed to validate llms.txt: {str(e)}",
            field="file_path",
        ) from e


async def update_llms_txt_tool(
    project_path: str,
    regenerate_sections: Optional[List[str]] = None,
    preserve_custom_content: bool = True,
) -> Dict[str, Any]:
    """Update an existing llms.txt file."""
    try:
        if not project_path:
            raise ValidationError("project_path is required", field="project_path")
        
        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise ProjectAnalysisError(
                f"Project path does not exist: {project_path}",
                project_path=project_path,
            )

        log_with_context(
            logger,
            logging.INFO,
            "Updating llms.txt for project",
            context={
                "project_path": project_path,
                "regenerate_sections": regenerate_sections,
                "preserve_custom_content": preserve_custom_content,
            },
        )

        service = get_service()
        result = await service.update_llms_txt(
            project_path=project_path,
            regenerate_sections=regenerate_sections,
            preserve_custom_content=preserve_custom_content,
        )

        log_with_context(
            logger,
            logging.INFO,
            "Successfully updated llms.txt",
            context={"project_path": project_path, "result": result},
        )
        return result

    except (ValidationError, ProjectAnalysisError, FileOperationError) as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error updating llms.txt: {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating llms.txt for {project_path}")
        raise GenerationError(
            f"Failed to update llms.txt: {str(e)}",
            generation_type="update",
        ) from e


async def convert_to_context_tool(
    llms_txt_path: str, output_format: str = "xml", include_optional: bool = False
) -> Dict[str, Any]:
    """Convert llms.txt to LLM context format."""
    try:
        if not llms_txt_path:
            raise ValidationError("llms_txt_path is required", field="llms_txt_path")
        
        if output_format not in ["xml", "json"]:
            raise ValidationError(
                f"Invalid output_format: {output_format}. Must be 'xml' or 'json'",
                field="output_format",
                value=output_format,
            )

        file_path_obj = Path(llms_txt_path)
        if not file_path_obj.exists():
            raise FileOperationError(
                f"File does not exist: {llms_txt_path}",
                file_path=llms_txt_path,
                operation="read",
            )

        log_with_context(
            logger,
            logging.INFO,
            "Converting llms.txt to context format",
            context={
                "llms_txt_path": llms_txt_path,
                "output_format": output_format,
                "include_optional": include_optional,
            },
        )

        service = get_service()
        result = await service.convert_to_context(
            llms_txt_path=llms_txt_path,
            output_format=output_format,
            include_optional=include_optional,
        )

        log_with_context(
            logger,
            logging.INFO,
            "Successfully converted llms.txt",
            context={"llms_txt_path": llms_txt_path, "result": result},
        )
        return result

    except (ValidationError, FileOperationError) as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error converting llms.txt: {e.message}",
            context={"llms_txt_path": llms_txt_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        logger.exception(f"Unexpected error converting llms.txt {llms_txt_path}")
        raise GenerationError(
            f"Failed to convert llms.txt: {str(e)}",
            generation_type="conversion",
        ) from e


async def scan_project_structure_tool(
    project_path: str, scan_depth: int = 3, include_hidden: bool = False
) -> Dict[str, Any]:
    """Scan and analyze project structure."""
    try:
        if not project_path:
            raise ValidationError("project_path is required", field="project_path")
        
        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise ProjectAnalysisError(
                f"Project path does not exist: {project_path}",
                project_path=project_path,
            )

        if scan_depth < 1 or scan_depth > 10:
            raise ValidationError(
                "scan_depth must be between 1 and 10",
                field="scan_depth",
                value=scan_depth,
            )

        log_with_context(
            logger,
            logging.INFO,
            "Scanning project structure",
            context={
                "project_path": project_path,
                "scan_depth": scan_depth,
                "include_hidden": include_hidden,
            },
        )

        service = get_service()
        result = await service.scan_project_structure(
            project_path=project_path, scan_depth=scan_depth, include_hidden=include_hidden
        )

        log_with_context(
            logger,
            logging.INFO,
            "Project structure scan completed",
            context={"project_path": project_path, "result": result},
        )
        return result

    except (ValidationError, ProjectAnalysisError) as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error scanning project structure: {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        logger.exception(f"Unexpected error scanning project structure {project_path}")
        raise ProjectAnalysisError(
            f"Failed to scan project structure: {str(e)}",
            project_path=project_path,
        ) from e


async def generate_from_template_tool(
    project_path: str,
    template_name: str = "generic",
    custom_sections: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Generate llms.txt from a template."""
    try:
        if not project_path:
            raise ValidationError("project_path is required", field="project_path")
        
        if not template_name:
            raise ValidationError("template_name is required", field="template_name")

        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise ProjectAnalysisError(
                f"Project path does not exist: {project_path}",
                project_path=project_path,
            )

        log_with_context(
            logger,
            logging.INFO,
            "Generating llms.txt from template",
            context={
                "project_path": project_path,
                "template_name": template_name,
                "has_custom_sections": custom_sections is not None,
            },
        )

        service = get_service()
        result = await service.generate_from_template(
            project_path=project_path, template_name=template_name, custom_sections=custom_sections
        )

        log_with_context(
            logger,
            logging.INFO,
            "Template generation completed",
            context={
                "project_path": project_path,
                "template_name": template_name,
                "result": result,
            },
        )
        return result

    except (ValidationError, ProjectAnalysisError, GenerationError) as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error generating from template: {e.message}",
            context={
                "project_path": project_path,
                "template_name": template_name,
                "error": e.to_dict(),
            },
        )
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error generating from template {template_name} for {project_path}"
        )
        raise GenerationError(
            f"Failed to generate from template: {str(e)}",
            generation_type="template",
        ) from e


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
