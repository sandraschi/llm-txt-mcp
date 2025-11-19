"""Main server implementation for LLM.txt MCP server with stdio support."""

import logging
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .models.service import LLMTextService
from .tools.analyzer import analyze_repo_tool
from .tools.help import help_tool
from .tools.status import health_check_tool, status_tool
from .tools.tools import (
    convert_to_context_tool,
    generate_from_template_tool,
    generate_llms_txt_tool,
    scan_project_structure_tool,
    update_llms_txt_tool,
    validate_llms_txt_tool,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("LLM.txt MCP Server")


# Register all tools with proper decorators
@mcp.tool()
async def generate_llms_txt(
    project_path: str,
    output_path: Optional[str] = None,
    include_optional: bool = True,
    scan_depth: int = 3,
) -> Dict[str, Any]:
    """Generate a complete llms.txt file for a project directory."""
    return await generate_llms_txt_tool(project_path, output_path, include_optional, scan_depth)


@mcp.tool()
async def validate_llms_txt(file_path: str) -> Dict[str, Any]:
    """Validate an existing llms.txt file for format compliance and completeness."""
    return await validate_llms_txt_tool(file_path)


@mcp.tool()
async def update_llms_txt(
    project_path: str,
    regenerate_sections: Optional[List[str]] = None,
    preserve_custom_content: bool = True,
) -> Dict[str, Any]:
    """Update an existing llms.txt file while preserving custom content."""
    return await update_llms_txt_tool(project_path, regenerate_sections, preserve_custom_content)


@mcp.tool()
async def convert_to_context(
    llms_txt_path: str, output_format: str = "xml", include_optional: bool = False
) -> Dict[str, Any]:
    """Convert llms.txt to XML or JSON format for LLM consumption."""
    return await convert_to_context_tool(llms_txt_path, output_format, include_optional)


@mcp.tool()
async def scan_project_structure(
    project_path: str, scan_depth: int = 3, include_hidden: bool = False
) -> Dict[str, Any]:
    """Analyze project structure and provide documentation recommendations."""
    return await scan_project_structure_tool(project_path, scan_depth, include_hidden)


@mcp.tool()
async def generate_from_template(
    project_path: str,
    template_name: str = "generic",
    custom_sections: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Generate llms.txt from predefined templates."""
    return await generate_from_template_tool(project_path, template_name, custom_sections)


@mcp.tool()
async def help(tool_name: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive help information about available tools and server capabilities."""
    return await help_tool(tool_name, category)


@mcp.tool()
async def status(
    include_system_info: bool = False, include_performance_metrics: bool = False
) -> Dict[str, Any]:
    """Get comprehensive server status and health information."""
    return await status_tool(include_system_info, include_performance_metrics)


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Perform a quick health check of the server."""
    return await health_check_tool()


@mcp.tool()
async def analyze_repo(
    repo_path: str, include_analysis: bool = False, output_format: str = "text"
) -> Dict[str, Any]:
    """Analyze repository for AI accessibility and provide comprehensive recommendations."""
    return await analyze_repo_tool(repo_path, include_analysis, output_format)


class LLMTextMCP:
    """LLM.txt MCP Server with stdio support for Claude Desktop."""

    def __init__(self):
        self.mcp = mcp
        self.service = LLMTextService()
        logger.info("LLM.txt MCP Server initialized")

    def run_stdio(self):
        """Run the MCP server with stdio transport for Claude Desktop."""
        try:
            logger.info("Starting LLM.txt MCP server with stdio transport")
            self.mcp.run()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            logger.info("LLM.txt MCP server stopped")

    def run_http(self, host: str = "localhost", port: int = 8000):
        """Run the MCP server with HTTP transport (legacy support)."""
        try:
            logger.info(f"Starting LLM.txt MCP server on {host}:{port}")
            self.mcp.run(host=host, port=port)
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            logger.info("LLM.txt MCP server stopped")


def main():
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(description="LLM.txt MCP Server")
    parser.add_argument(
        "--stdio", action="store_true", help="Run with stdio transport for Claude Desktop"
    )
    parser.add_argument(
        "--host", default="localhost", help="Host for HTTP server (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for HTTP server (default: 8000)"
    )

    args = parser.parse_args()

    server = LLMTextMCP()

    if args.stdio:
        server.run_stdio()
    else:
        server.run_http(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
