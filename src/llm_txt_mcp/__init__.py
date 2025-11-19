"""
LLM.txt MCP - MCP server for generating and managing llms.txt documentation files.

This package provides tools for automatically generating, updating, and managing
llms.txt files for projects to make them AI-readable.
"""

from typing import Optional

# Import core components
from .models.service import DocumentationProject, LLMTextService
from .server import LLMTextMCP
from .server import main as server_main
from .utils.generator import LLMTextGenerator

# Package metadata
__version__ = "0.1.0"
__author__ = "Sandra Schipal <sandra@sandraschi.dev>"
__license__ = "MIT"

# Public API
__all__ = [
    "LLMTextService",
    "DocumentationProject",
    "LLMTextMCP",
    "LLMTextGenerator",
    "server_main",
    "generate_llms_txt",
    "create_service",
]

# Global service instance
_service_instance: Optional[LLMTextService] = None


def create_service() -> LLMTextService:
    """
    Create and return a new LLMTextService instance.

    Returns:
        LLMTextService: A new instance of LLMTextService
    """
    return LLMTextService()


def generate_llms_txt(
    project_path: str,
    output_path: Optional[str] = None,
    service: Optional[LLMTextService] = None,
) -> str:
    """
    Convenience function to generate llms.txt for a project.

    Args:
        project_path: Path to the project directory
        output_path: Optional custom output path for llms.txt
        service: Optional LLMTextService instance

    Returns:
        str: Path to the generated llms.txt file
    """
    global _service_instance

    if service is None:
        if _service_instance is None:
            _service_instance = LLMTextService()
        service = _service_instance

    return service.generate_project_llms_txt(project_path, output_path)


def run_server(host: str = "localhost", port: int = 8000) -> None:
    """
    Run the LLMTextMCP server.

    Args:
        host: Host to bind to (default: localhost)
        port: Port to listen on (default: 8000)
    """
    server = LLMTextMCP()
    server.run(host=host, port=port)


def main():
    """Main entry point for the MCP server."""
    from .server import LLMTextMCP

    server = LLMTextMCP()
    server.run_stdio()


# Add type hints for better IDE support
if False:  # pragma: no cover
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from .models.service import DocumentationProject, LLMTextService
        from .server import LLMTextMCP
        from .utils.generator import LLMTextGenerator
