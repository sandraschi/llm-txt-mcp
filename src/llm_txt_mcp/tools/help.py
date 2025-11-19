"""Help tool for LLM.txt MCP server."""

import logging
from typing import Any, Dict, List, Optional

# Note: mcp is not imported here to avoid circular imports

logger = logging.getLogger(__name__)


# Tool function without decorator - will be registered in server.py
async def help_tool(
    tool_name: Optional[str] = None, category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive help information about available tools and server capabilities.

    This tool provides detailed information about all available tools in the LLM.txt
    MCP server, including their parameters, return values, and usage examples.

    Parameters:
        tool_name (str, optional): Specific tool to get detailed help for
        category (str, optional): Filter tools by category ("generation", "validation", "analysis")

    Returns:
        dict: Help information including tool descriptions, parameters, and examples
    """
    try:
        logger.info(f"Providing help information (tool: {tool_name}, category: {category})")

        # Get all registered tools
        # Get all registered tools

        # This is a simplified representation - in practice, you'd get this from the MCP server
        all_tools = {
            "generate_llms_txt": {
                "description": "Generate complete llms.txt files for projects",
                "category": "generation",
                "parameters": {
                    "project_path": "Path to project directory",
                    "output_path": "Optional custom output path",
                    "include_optional": "Include optional sections",
                    "scan_depth": "Directory scan depth",
                },
                "example": 'generate_llms_txt(project_path="/path/to/project")',
            },
            "validate_llms_txt": {
                "description": "Validate llms.txt file format and compliance",
                "category": "validation",
                "parameters": {"file_path": "Path to llms.txt file"},
                "example": 'validate_llms_txt(file_path="/path/to/llms.txt")',
            },
            "update_llms_txt": {
                "description": "Update existing llms.txt while preserving custom content",
                "category": "generation",
                "parameters": {
                    "project_path": "Path to project directory",
                    "regenerate_sections": "Specific sections to update",
                    "preserve_custom_content": "Preserve manual additions",
                },
                "example": 'update_llms_txt(project_path="/path/to/project")',
            },
            "convert_to_context": {
                "description": "Convert llms.txt to XML/JSON for LLM consumption",
                "category": "conversion",
                "parameters": {
                    "llms_txt_path": "Path to llms.txt file",
                    "output_format": "Output format (xml/json)",
                    "include_optional": "Include optional sections",
                },
                "example": (
                    'convert_to_context(llms_txt_path="/path/to/llms.txt", ' 'output_format="xml")'
                ),
            },
            "scan_project_structure": {
                "description": "Analyze project structure and provide recommendations",
                "category": "analysis",
                "parameters": {
                    "project_path": "Path to project directory",
                    "scan_depth": "Maximum scan depth",
                    "include_hidden": "Include hidden files",
                },
                "example": 'scan_project_structure(project_path="/path/to/project")',
            },
            "generate_from_template": {
                "description": "Generate llms.txt from predefined templates",
                "category": "generation",
                "parameters": {
                    "project_path": "Path to project directory",
                    "template_name": "Template to use",
                    "custom_sections": "Additional custom sections",
                },
                "example": (
                    'generate_from_template(project_path="/path/to/project", '
                    'template_name="python")'
                ),
            },
            "help": {
                "description": "Get help information about tools",
                "category": "utility",
                "parameters": {
                    "tool_name": "Specific tool to get help for",
                    "category": "Filter tools by category",
                },
                "example": 'help(tool_name="generate_llms_txt")',
            },
            "status": {
                "description": "Get server status and health information",
                "category": "utility",
                "parameters": {},
                "example": "status()",
            },
            "health_check": {
                "description": "Perform a quick health check of the server",
                "category": "utility",
                "parameters": {},
                "example": "health_check()",
            },
            "analyze_repo": {
                "description": (
                    "Analyze repository for AI accessibility and provide recommendations"
                ),
                "category": "analysis",
                "parameters": {
                    "repo_path": "Path to repository",
                    "include_analysis": "Include detailed analysis",
                    "output_format": "Output format for Claude",
                },
                "example": 'analyze_repo(repo_path="/path/to/repo")',
            },
        }

        if tool_name:
            # Return detailed help for specific tool
            if tool_name in all_tools:
                tool_info = all_tools[tool_name]
                return {
                    "tool": tool_name,
                    "description": tool_info["description"],
                    "category": tool_info["category"],
                    "parameters": tool_info["parameters"],
                    "example": tool_info["example"],
                    "usage_notes": f"Use this tool to {tool_info['description'].lower()}",
                }
            else:
                return {
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(all_tools.keys()),
                }

        # Filter by category if specified
        if category:
            filtered_tools = {
                name: info for name, info in all_tools.items() if info["category"] == category
            }
        else:
            filtered_tools = all_tools

        # General help information
        categories: Dict[str, List[Dict[str, str]]] = {}
        for name, info in filtered_tools.items():
            cat = info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({"name": name, "description": info["description"]})

        return {
            "server_name": "LLM.txt MCP Server",
            "version": "0.1.0",
            "description": "MCP server for generating and managing llms.txt documentation files",
            "categories": categories,
            "total_tools": len(filtered_tools),
            "usage": (
                "Use these tools to make your projects AI-accessible through automated "
                "llms.txt generation"
            ),
        }

    except Exception as e:
        logger.error(f"Error providing help: {e}")
        raise


__all__ = ["help_tool"]
