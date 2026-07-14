"""Main server implementation for LLM.txt MCP server with stdio support."""

import logging
import sys
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from .exceptions import LLMTextMCPError, ServiceError
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
from .utils.logging import get_logger, log_with_context, setup_logging

# Set up structured logging
setup_logging(level="INFO", use_json=True, stream=sys.stderr)
logger = get_logger(__name__)

# Initialize the MCP server
mcp = FastMCP("LLM.txt MCP Server")

# ---------------------------------------------------------------------------
# FastAPI Substrate (SOTA 2026)
# ---------------------------------------------------------------------------
# Create the main FastAPI app
app = FastAPI(title="LLM.txt MCP SOTA Substrate")

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted in production, wildcard for local dev convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def api_health():
    """SOTA Health Check for fleet monitoring."""
    return {
        "status": "healthy",
        "service": "llm-txt-mcp",
        "version": "1.19.0",
        "mcp_server": "online",
    }


@app.post("/call")
async def api_call_tool(request: dict[str, Any]):
    """Bridge endpoint for webapp to call MCP tools."""
    name = request.get("name")
    arguments = request.get("arguments", {}) or {}
    if not name:
        raise HTTPException(status_code=400, detail="Tool name is required")

    # Handle SOTA frontend aliases - Frontend often uses 'project_root', 'repository_path' or 'path'
    # but backend tools expect 'project_path' or 'file_path'.
    if "project_root" in arguments:
        root = arguments.pop("project_root")
        if name == "validate_llms_txt":
            if "file_path" not in arguments:
                arguments["file_path"] = f"{root}/llms.txt"
        elif "project_path" not in arguments:
            arguments["project_path"] = root

    if "repository_path" in arguments and "project_path" not in arguments:
        arguments["project_path"] = arguments.pop("repository_path")

    if name == "validate_llms_txt" and "path" in arguments and "file_path" not in arguments:
        arguments["file_path"] = arguments.pop("path")

    try:
        logger.info(f"Calling tool via bridge: {name} with arguments: {arguments}")
        # Call the tool via FastMCP's internal logic
        result = await mcp.call_tool(name, arguments)
        return result
    except Exception as e:
        logger.exception(f"Error calling tool {name} via bridge")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Mount the FastMCP HTTP/SSE application handlers at the root
# This allows standard MCP clients to connect to the root URL
app.mount("/", mcp.http_app(path="/"))


# Register all tools with proper decorators
@mcp.tool()
async def generate_llms_txt(
    project_path: str,
    output_path: str | None = None,
    include_optional: bool = True,
    scan_depth: int = 3,
    quality_mode: bool = True,
) -> dict[str, Any]:
    """Generate complete llms.txt documentation files for a project directory.

    This tool automatically scans a project directory, analyzes its structure and
    documentation files, and generates comprehensive llms.txt files that make the
    project AI-accessible. It intelligently categorizes documentation, source files,
    examples, and configuration files into structured sections following the llms.txt
    specification. The tool creates both a main llms.txt file (with links) and an
    llms-full.txt file (with full content) for maximum AI accessibility.

    Parameters:
        project_path: Absolute or relative path to the project directory to analyze
            - Must be a valid directory path
            - Directory must exist and be readable
            - Supports both absolute and relative paths
            - Example: '/home/user/my-project' or './my-project'

        output_path: Optional custom path for output files (default: None)
            - If None, files are created in the project directory
            - If specified, must be a valid directory path
            - Output files will be named llms.txt and llms-full.txt
            - Example: '/tmp/output' creates /tmp/output/llms.txt

        include_optional: Whether to include optional sections in output (default: True)
            - Optional sections include changelog, contributing, license, etc.
            - Set to False for minimal documentation
            - Recommended: True for comprehensive documentation

        scan_depth: Maximum directory depth to scan for files (default: 3)
            - Must be between 1 and 10
            - Higher values scan deeper but may be slower
            - Recommended: 3 for most projects
            - Use 1-2 for shallow projects, 4-5 for deeply nested structures

        quality_mode: Fleet-quality manifest generation (default: True)
            - Skips debug dumps, lockfiles, .env, megatest guides, node_modules
            - llms-full.txt uses sanitized excerpts, not whole-repo paste
            - Set False only for legacy verbose dumps

    Returns:
        Dictionary containing:
            - llms_txt_path: Path to the generated llms.txt file
            - llms_full_txt_path: Path to the generated llms-full.txt file
            - files_analyzed: Number of documentation files found and processed
            - sections_created: Number of sections created in the llms.txt file

    Usage:
        Use this tool when you want to make a project AI-accessible by generating
        comprehensive llms.txt documentation. It's ideal for:
        - New projects that need initial documentation structure
        - Existing projects that want to improve AI accessibility
        - Projects preparing for AI-assisted development or analysis
        - Documentation maintenance and updates

        The tool automatically detects project type (Python, TypeScript, React, etc.)
        and generates appropriate sections. It prioritizes important documentation
        files like README, API docs, and examples.

    Examples:
        Basic usage for a Python project:
            result = await generate_llms_txt('/home/user/my-python-app')
            # Returns: {
            #     'llms_txt_path': '/home/user/my-python-app/llms.txt',
            #     'llms_full_txt_path': '/home/user/my-python-app/llms-full.txt',
            #     'files_analyzed': 15,
            #     'sections_created': 5
            # }

        Generate with custom output location:
            result = await generate_llms_txt(
                project_path='/home/user/my-project',
                output_path='/tmp/docs',
                include_optional=False,
                scan_depth=2
            )
            # Creates /tmp/docs/llms.txt and /tmp/docs/llms-full.txt

        Minimal documentation without optional sections:
            result = await generate_llms_txt(
                project_path='./my-project',
                include_optional=False
            )
            # Generates only essential sections

    Raises:
        ValidationError: When project_path is empty or scan_depth is out of range
        ProjectAnalysisError: When project path doesn't exist or isn't a directory
        GenerationError: When file generation fails due to I/O errors
        ServiceError: When internal service operations fail

    Notes:
        - The tool automatically detects project type based on key files
        - Generated files use UTF-8 encoding
        - Existing llms.txt files are overwritten without warning
        - Large projects may take several seconds to process
        - Hidden files are excluded unless explicitly included
        - Git repositories are detected and used for enhanced metadata
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: generate_llms_txt",
            context={"project_path": project_path, "output_path": output_path},
        )
        result = await generate_llms_txt_tool(project_path, output_path, include_optional, scan_depth, quality_mode)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: generate_llms_txt",
            context={"project_path": project_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: generate_llms_txt - {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in generate_llms_txt: {e!s}",
            context={"project_path": project_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error in generate_llms_txt")
        raise ServiceError(
            f"Failed to generate llms.txt: {e!s}",
            service_name="generate_llms_txt",
        ) from e


@mcp.tool()
async def validate_llms_txt(file_path: str) -> dict[str, Any]:
    """Validate an existing llms.txt file for format compliance and completeness.

    This tool performs comprehensive validation of an llms.txt file to ensure it
    follows the llms.txt specification and contains all required elements. It checks
    for proper structure, required sections, valid markdown formatting, and provides
    detailed feedback on any issues found. The validation helps ensure that generated
    or manually edited llms.txt files are properly formatted and will work correctly
    with AI systems that consume llms.txt documentation.

    Parameters:
        file_path: Path to the llms.txt file to validate
            - Must be a valid file path
            - File must exist and be readable
            - Supports both absolute and relative paths
            - Example: '/home/user/my-project/llms.txt' or './llms.txt'

    Returns:
        Dictionary containing:
            - is_valid: Boolean indicating if the file passes all validation checks
            - errors: List of error messages for critical issues that must be fixed
            - warnings: List of warning messages for non-critical issues
            - suggestions: List of recommendations for improving the file

    Usage:
        Use this tool to verify that an llms.txt file is properly formatted before
        using it with AI systems. It's particularly useful for:
        - Validating manually edited llms.txt files
        - Checking files generated by other tools
        - Ensuring compliance with llms.txt specification
        - Quality assurance in documentation workflows

        The tool checks for required elements like H1 headers, blockquote summaries,
        section structure, and proper markdown link formatting.

    Examples:
        Validate a file in the current directory:
            result = await validate_llms_txt('./llms.txt')
            # Returns: {
            #     'is_valid': True,
            #     'errors': [],
            #     'warnings': ['Consider adding more sections'],
            #     'suggestions': ['Add examples section']
            # }

        Validate with errors found:
            result = await validate_llms_txt('/path/to/invalid.txt')
            # Returns: {
            #     'is_valid': False,
            #     'errors': ['Missing H1 header with project name'],
            #     'warnings': ['No markdown links found in sections'],
            #     'suggestions': ['Add blockquote summary after title']
            # }

        Check validation status:
            result = await validate_llms_txt('llms.txt')
            if result['is_valid']:
                print('File is valid!')
            else:
                print(f'Errors: {result["errors"]}')

    Raises:
        ValidationError: When file_path is empty or invalid
        FileOperationError: When file doesn't exist or cannot be read
        ServiceError: When validation process fails internally

    Notes:
        - Validation is case-sensitive for section names
        - Markdown formatting is checked but not strictly enforced
        - Empty sections are flagged as warnings, not errors
        - File encoding must be UTF-8 for proper validation
        - Large files may take longer to validate
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: validate_llms_txt",
            context={"file_path": file_path},
        )
        result = await validate_llms_txt_tool(file_path)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: validate_llms_txt",
            context={"file_path": file_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: validate_llms_txt - {e.message}",
            context={"file_path": file_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in validate_llms_txt: {e!s}",
            context={"file_path": file_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to validate llms.txt: {e!s}",
            service_name="validate_llms_txt",
        ) from e


@mcp.tool()
async def update_llms_txt(
    project_path: str,
    regenerate_sections: list[str] | None = None,
    preserve_custom_content: bool = True,
) -> dict[str, Any]:
    """Update an existing llms.txt file while preserving custom content.

    This tool intelligently updates an existing llms.txt file by regenerating
    specified sections while preserving any custom content that was manually added.
    It's designed to keep your documentation up-to-date with project changes while
    maintaining your custom additions. The tool can update all sections or only
    specific ones, and it attempts to preserve manual edits when possible.

    Parameters:
        project_path: Path to the project directory containing llms.txt
            - Must be a valid directory path
            - Directory must contain an existing llms.txt file
            - Supports both absolute and relative paths
            - Example: '/home/user/my-project' or './my-project'

        regenerate_sections: Optional list of specific sections to regenerate (default: None)
            - If None, all sections are regenerated
            - Valid section names: 'docs', 'api', 'examples', 'configuration', 'optional'
            - Case-sensitive section names
            - Example: ['docs', 'api'] regenerates only those sections
            - Other sections remain unchanged

        preserve_custom_content: Whether to preserve manually added content (default: True)
            - When True, attempts to keep custom entries in sections
            - When False, sections are completely regenerated
            - Recommended: True to maintain manual additions
            - Custom content detection is heuristic-based

    Returns:
        Dictionary containing:
            - updated_sections: List of section names that were regenerated
            - preserved_content: List of messages about preserved custom content
            - changes_made: List of descriptions of changes applied

    Usage:
        Use this tool to keep your llms.txt file synchronized with project changes
        without losing manual additions. It's ideal for:
        - Updating documentation after adding new files
        - Refreshing specific sections that changed
        - Maintaining documentation as project evolves
        - Periodic documentation maintenance

        The tool is smart about detecting what's custom vs. auto-generated, but
        manual review is recommended after updates.

    Examples:
        Update all sections while preserving custom content:
            result = await update_llms_txt('/home/user/my-project')
            # Returns: {
            #     'updated_sections': ['docs', 'api', 'examples'],
            #     'preserved_content': ['Preserved custom content in docs'],
            #     'changes_made': ['Updated docs section', 'Updated api section']
            # }

        Update only specific sections:
            result = await update_llms_txt(
                project_path='./my-project',
                regenerate_sections=['docs', 'api']
            )
            # Only docs and api sections are regenerated

        Complete regeneration without preserving custom content:
            result = await update_llms_txt(
                project_path='/path/to/project',
                preserve_custom_content=False
            )
            # All sections completely regenerated

    Raises:
        ValidationError: When project_path is empty or invalid
        ProjectAnalysisError: When project path doesn't exist
        FileOperationError: When llms.txt file doesn't exist or cannot be read/written
        GenerationError: When section regeneration fails
        ServiceError: When update process fails internally

    Notes:
        - Existing llms.txt file is required (use generate_llms_txt for new files)
        - Custom content preservation is best-effort and may not catch all cases
        - File is backed up before modification (check project directory)
        - Large files may take longer to process
        - Section order is maintained from original file when possible
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: update_llms_txt",
            context={
                "project_path": project_path,
                "regenerate_sections": regenerate_sections,
            },
        )
        result = await update_llms_txt_tool(project_path, regenerate_sections, preserve_custom_content)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: update_llms_txt",
            context={"project_path": project_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: update_llms_txt - {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in update_llms_txt: {e!s}",
            context={"project_path": project_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to update llms.txt: {e!s}",
            service_name="update_llms_txt",
        ) from e


@mcp.tool()
async def convert_to_context(
    llms_txt_path: str, output_format: str = "xml", include_optional: bool = False
) -> dict[str, Any]:
    """Convert llms.txt file to XML or JSON format optimized for LLM consumption.

    This tool converts a standard llms.txt markdown file into structured XML or JSON
    formats that are optimized for direct consumption by LLMs. The converted format
    provides better structure for AI systems to parse and understand project
    documentation. XML format is ideal for Claude and other XML-preferring models,
    while JSON format works well for programmatic access and other LLM systems.

    Parameters:
        llms_txt_path: Path to the llms.txt file to convert
            - Must be a valid file path
            - File must exist and be readable
            - Supports both absolute and relative paths
            - Example: '/home/user/my-project/llms.txt' or './llms.txt'

        output_format: Desired output format, either 'xml' or 'json' (default: 'xml')
            - Must be exactly 'xml' or 'json' (case-insensitive)
            - XML format is optimized for Claude and similar models
            - JSON format is better for programmatic access
            - Example: 'xml' or 'json'

        include_optional: Whether to include optional sections in output (default: False)
            - When False, only essential sections are included
            - When True, optional sections (changelog, contributing, etc.) are included
            - Recommended: False for token efficiency, True for completeness

    Returns:
        Dictionary containing:
            - output_path: Path to the generated context file
            - format: The output format used ('xml' or 'json')
            - token_count: Approximate number of tokens in the output

    Usage:
        Use this tool when you need to convert llms.txt for direct LLM consumption
        or when working with systems that prefer structured formats. It's useful for:
        - Preparing documentation for Claude or other LLMs
        - Creating context files for AI assistants
        - Generating structured documentation for API consumption
        - Optimizing documentation for token-limited contexts

        The XML format follows a structured schema that LLMs can easily parse, while
        JSON format provides programmatic access to documentation structure.

    Examples:
        Convert to XML format (default):
            result = await convert_to_context('./llms.txt', 'xml')
            # Returns: {
            #     'output_path': './llms.ctx.xml',
            #     'format': 'xml',
            #     'token_count': 1234
            # }

        Convert to JSON with optional sections:
            result = await convert_to_context(
                llms_txt_path='/path/to/llms.txt',
                output_format='json',
                include_optional=True
            )
            # Creates /path/to/llms.ctx.json with all sections

        Convert for minimal token usage:
            result = await convert_to_context(
                'llms.txt',
                output_format='xml',
                include_optional=False
            )
            # Creates minimal XML context file

    Raises:
        ValidationError: When file_path is empty or output_format is invalid
        FileOperationError: When file doesn't exist or cannot be read/written
        GenerationError: When conversion process fails
        ServiceError: When conversion service fails internally

    Notes:
        - Output file is created in the same directory as input file
        - Output filename follows pattern: {input_name}.ctx.{format}
        - XML format uses UTF-8 encoding with proper escaping
        - JSON format is pretty-printed for readability
        - Token count is approximate and may vary by tokenizer
        - Large files may take longer to convert
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: convert_to_context",
            context={"llms_txt_path": llms_txt_path, "output_format": output_format},
        )
        result = await convert_to_context_tool(llms_txt_path, output_format, include_optional)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: convert_to_context",
            context={"llms_txt_path": llms_txt_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: convert_to_context - {e.message}",
            context={"llms_txt_path": llms_txt_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in convert_to_context: {e!s}",
            context={"llms_txt_path": llms_txt_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to convert llms.txt: {e!s}",
            service_name="convert_to_context",
        ) from e


@mcp.tool()
async def scan_project_structure(
    project_path: str, scan_depth: int = 3, include_hidden: bool = False
) -> dict[str, Any]:
    """Analyze project structure and provide documentation recommendations.

    This tool performs a comprehensive analysis of a project's directory structure,
    file organization, and existing documentation to provide actionable recommendations
    for improving AI accessibility. It identifies documentation gaps, suggests optimal
    section organization, and provides insights into how to structure llms.txt files
    for maximum effectiveness. The analysis helps you understand what documentation
    exists and what might be missing.

    Parameters:
        project_path: Path to the project directory to analyze
            - Must be a valid directory path
            - Directory must exist and be readable
            - Supports both absolute and relative paths
            - Example: '/home/user/my-project' or './my-project'

        scan_depth: Maximum directory depth to scan for files (default: 3)
            - Must be between 1 and 10
            - Higher values provide more comprehensive analysis
            - Recommended: 3 for most projects
            - Use 1-2 for quick scans, 4-5 for deep analysis

        include_hidden: Whether to include hidden files and directories (default: False)
            - When False, files starting with '.' are excluded
            - When True, all files including hidden ones are analyzed
            - Recommended: False for most use cases
            - Set True for projects with important hidden documentation

    Returns:
        Dictionary containing:
            - project_type: Detected project type (python, typescript, react, etc.)
            - documentation_files: List of paths to documentation files found
            - source_files: List of paths to source files (sample, first 10)
            - suggested_sections: List of recommended section names for llms.txt
            - recommendations: List of actionable recommendations for improvement

    Usage:
        Use this tool to understand your project's documentation structure before
        generating llms.txt files. It's helpful for:
        - Planning documentation organization
        - Identifying missing documentation
        - Understanding project structure
        - Getting recommendations before generation

        The tool provides insights that help you make informed decisions about
        how to structure your llms.txt file for optimal AI accessibility.

    Examples:
        Basic project structure scan:
            result = await scan_project_structure('/home/user/my-project')
            # Returns: {
            #     'project_type': 'python',
            #     'documentation_files': ['README.md', 'docs/api.md'],
            #     'source_files': ['src/main.py', 'src/utils.py'],
            #     'suggested_sections': ['docs', 'api', 'examples'],
            #     'recommendations': ['Add usage examples', 'Document API endpoints']
            # }

        Deep scan including hidden files:
            result = await scan_project_structure(
                project_path='./my-project',
                scan_depth=5,
                include_hidden=True
            )
            # Comprehensive analysis including hidden files

        Quick shallow scan:
            result = await scan_project_structure(
                'my-project',
                scan_depth=1
            )
            # Fast analysis of top-level only

    Raises:
        ValidationError: When project_path is empty or scan_depth is out of range
        ProjectAnalysisError: When project path doesn't exist or isn't a directory
        ServiceError: When analysis process fails internally

    Notes:
        - Analysis is read-only and doesn't modify any files
        - Source files list is limited to first 10 for performance
        - Project type detection is based on key files (package.json, pyproject.toml, etc.)
        - Recommendations are based on best practices and common patterns
        - Large projects may take several seconds to analyze
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: scan_project_structure",
            context={"project_path": project_path, "scan_depth": scan_depth},
        )
        result = await scan_project_structure_tool(project_path, scan_depth, include_hidden)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: scan_project_structure",
            context={"project_path": project_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: scan_project_structure - {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in scan_project_structure: {e!s}",
            context={"project_path": project_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to scan project structure: {e!s}",
            service_name="scan_project_structure",
        ) from e


@mcp.tool()
async def generate_from_template(
    project_path: str,
    template_name: str = "generic",
    custom_sections: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Generate llms.txt file from predefined templates for common project types.

    This tool generates llms.txt files using pre-configured templates optimized for
    specific project types. Templates provide a structured starting point with
    appropriate sections and placeholders for different kinds of projects. This is
    ideal for quickly creating documentation structure when you want a standardized
    format rather than auto-generated content. You can customize templates with
    additional sections as needed.

    Parameters:
        project_path: Path to the project directory where llms.txt will be created
            - Must be a valid directory path
            - Directory must exist and be writable
            - Supports both absolute and relative paths
            - Example: '/home/user/my-project' or './my-project'

        template_name: Name of the template to use (default: 'generic')
            - Valid options: 'generic', 'python', 'typescript', 'react', 'fastapi'
            - Case-sensitive template names
            - 'generic' works for any project type
            - Project-specific templates include relevant sections
            - Example: 'python' for Python projects, 'react' for React apps

        custom_sections: Optional dictionary of custom sections to add (default: None)
            - Keys are section names, values are lists of section items
            - Format: {'section_name': ['item1', 'item2', ...]}
            - Merged with template sections
            - Example: {'deployment': ['docker.md', 'kubernetes.md']}
            - None means use only template sections

    Returns:
        Dictionary containing:
            - template_used: Name of the template that was applied
            - llms_txt_path: Path to the generated llms.txt file
            - sections_created: Number of sections created in the file

    Usage:
        Use this tool when you want a quick start with a standardized llms.txt
        structure rather than auto-generated content. It's ideal for:
        - New projects needing initial documentation structure
        - Projects following standard patterns
        - Quick documentation setup
        - Template-based documentation workflows

        Templates provide a solid foundation that you can then customize manually
        or update using the update_llms_txt tool.

    Examples:
        Generate using generic template:
            result = await generate_from_template('./my-project')
            # Returns: {
            #     'template_used': 'generic',
            #     'llms_txt_path': './my-project/llms.txt',
            #     'sections_created': 3
            # }

        Generate for Python project:
            result = await generate_from_template(
                project_path='/home/user/python-app',
                template_name='python'
            )
            # Creates Python-optimized template with API and config sections

        Generate with custom sections:
            result = await generate_from_template(
                'my-project',
                template_name='react',
                custom_sections={
                    'deployment': ['docker.md', 'vercel.md'],
                    'testing': ['jest.md', 'cypress.md']
                }
            )
            # React template with additional deployment and testing sections

    Raises:
        ValidationError: When project_path is empty or template_name is invalid
        ProjectAnalysisError: When project path doesn't exist
        GenerationError: When template generation fails
        ServiceError: When template service fails internally

    Notes:
        - Generated files use template placeholders that should be customized
        - Existing llms.txt files are overwritten without warning
        - Templates are optimized for their respective project types
        - Custom sections are appended to template sections
        - File encoding is UTF-8
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: generate_from_template",
            context={"project_path": project_path, "template_name": template_name},
        )
        result = await generate_from_template_tool(project_path, template_name, custom_sections)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: generate_from_template",
            context={"project_path": project_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: generate_from_template - {e.message}",
            context={"project_path": project_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in generate_from_template: {e!s}",
            context={"project_path": project_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to generate from template: {e!s}",
            service_name="generate_from_template",
        ) from e


@mcp.tool()
async def help(tool_name: str | None = None, category: str | None = None) -> dict[str, Any]:
    """Get comprehensive help information about available tools and server capabilities.

    This tool provides detailed documentation and usage information for all tools
    available in the LLM.txt MCP server. You can get help for a specific tool, filter
    by category, or browse all available tools. The help information includes tool
    descriptions, parameter details, usage examples, and best practices. This is the
    primary way to discover and understand how to use the server's capabilities.

    Parameters:
        tool_name: Optional name of specific tool to get detailed help for (default: None)
            - If None, returns help for all tools
            - Must match exact tool name (case-sensitive)
            - Example: 'generate_llms_txt' or 'validate_llms_txt'
            - Invalid tool names return list of available tools

        category: Optional category to filter tools by (default: None)
            - Valid categories: 'generation', 'validation', 'analysis', 'utility'
            - If None, all categories are included
            - Case-sensitive category names
            - Example: 'generation' shows only generation tools

    Returns:
        Dictionary containing:
            - If tool_name specified: Detailed tool information with description,
              parameters, examples, and usage notes
            - If category specified: Tools filtered by category with descriptions
            - If neither specified: Complete server information with all tools
              organized by category, total tool count, and usage overview

    Usage:
        Use this tool to discover available functionality, understand tool parameters,
        and learn best practices. It's helpful for:
        - Discovering what tools are available
        - Understanding tool parameters and usage
        - Learning best practices and examples
        - Getting started with the server

        This tool is self-documenting and provides the most up-to-date information
        about server capabilities.

    Examples:
        Get help for all tools:
            result = await help()
            # Returns: {
            #     'server_name': 'LLM.txt MCP Server',
            #     'version': '0.1.0',
            #     'categories': {...},
            #     'total_tools': 10
            # }

        Get help for specific tool:
            result = await help(tool_name='generate_llms_txt')
            # Returns: {
            #     'tool': 'generate_llms_txt',
            #     'description': '...',
            #     'parameters': {...},
            #     'example': '...'
            # }

        Filter by category:
            result = await help(category='generation')
            # Returns tools in generation category only

    Raises:
        ServiceError: When help system fails internally

    Notes:
        - Help information is always up-to-date with current server version
        - Examples in help are tested and working
        - Tool names are case-sensitive
        - Categories are predefined and cannot be customized
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: help",
            context={"tool_name": tool_name, "category": category},
        )
        result = await help_tool(tool_name, category)
        return result
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in help: {e!s}",
            context={"tool_name": tool_name, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to provide help: {e!s}",
            service_name="help",
        ) from e


@mcp.tool()
async def status(include_system_info: bool = False, include_performance_metrics: bool = False) -> dict[str, Any]:
    """Get comprehensive server status and health information.

    This tool provides detailed information about the server's current status,
    configuration, and operational health. It includes server version, registered
    tools, service availability, and optionally system resource information and
    performance metrics. Use this tool to monitor server health, troubleshoot
    issues, and understand server configuration. The status information helps
    ensure the server is operating correctly and can help diagnose problems.

    Parameters:
        include_system_info: Whether to include detailed system information (default: False)
            - When True, includes CPU count, memory usage, disk usage
            - When False, only basic server information is included
            - System info collection may take a moment
            - Recommended: False for quick checks, True for diagnostics

        include_performance_metrics: Whether to include performance metrics (default: False)
            - When True, includes CPU usage, memory percentage, disk I/O
            - When False, performance metrics are excluded
            - Metrics collection requires brief measurement period
            - Recommended: False for quick status, True for monitoring

    Returns:
        Dictionary containing:
            - server_name: Name of the MCP server
            - version: Server version string
            - status: Overall health status ('healthy', 'degraded', 'unhealthy')
            - timestamp: ISO format timestamp of status check
            - configuration: Server configuration details
            - tools_registered: List of all registered tool names
            - errors: List of any error conditions found
            - warnings: List of any warning conditions
            - system: System information (if include_system_info is True)
            - performance: Performance metrics (if include_performance_metrics is True)
            - service_status: Status of internal services

    Usage:
        Use this tool to check server health and diagnose issues. It's useful for:
        - Verifying server is running correctly
        - Checking service availability
        - Monitoring system resources
        - Troubleshooting problems
        - Understanding server configuration

        Regular status checks help ensure the server remains healthy and can
        identify issues before they become critical.

    Examples:
        Basic status check:
            result = await status()
            # Returns: {
            #     'server_name': 'LLM.txt MCP Server',
            #     'status': 'healthy',
            #     'tools_registered': [...],
            #     'errors': [],
            #     'warnings': []
            # }

        Full status with system info:
            result = await status(
                include_system_info=True,
                include_performance_metrics=True
            )
            # Returns comprehensive status including system resources

        Check for errors:
            result = await status()
            if result['status'] != 'healthy':
                print(f'Issues: {result["errors"]}')

    Raises:
        ServiceError: When status check fails internally

    Notes:
        - Status check is read-only and doesn't modify server state
        - Performance metrics require a brief measurement period
        - System info collection may fail on some platforms
        - Status reflects current state at time of check
        - Warnings don't necessarily indicate problems
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: status",
            context={
                "include_system_info": include_system_info,
                "include_performance_metrics": include_performance_metrics,
            },
        )
        result = await status_tool(include_system_info, include_performance_metrics)
        return result
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in status: {e!s}",
            context={"error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to get status: {e!s}",
            service_name="status",
        ) from e


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """Perform a quick health check of the server.

    This tool performs a lightweight health check to verify that the server is
    operational and core services are available. It's faster than the full status
    check and focuses on essential health indicators. Use this for quick verification
    that the server is responding and basic functionality is working. The health
    check is designed to be fast and non-intrusive, making it suitable for frequent
    monitoring or automated health checks.

    Parameters:
        None - This tool takes no parameters for maximum speed and simplicity.

    Returns:
        Dictionary containing:
            - status: Overall health status ('healthy' or 'unhealthy')
            - timestamp: ISO format timestamp of health check
            - checks: Dictionary of individual health check results
                - server_responsive: Boolean indicating server is responding
                - service_available: Boolean indicating core services are available
                - tools_registered: Boolean indicating tools are properly registered
            - issues: List of any issues found (empty if healthy)

    Usage:
        Use this tool for quick health verification, especially in automated
        monitoring scenarios. It's ideal for:
        - Quick server availability checks
        - Automated health monitoring
        - Load balancer health checks
        - Pre-flight checks before operations

        This is faster than the full status check but provides less detail.
        Use the status tool for comprehensive information.

    Examples:
        Basic health check:
            result = await health_check()
            # Returns: {
            #     'status': 'healthy',
            #     'timestamp': '2024-01-01T12:00:00Z',
            #     'checks': {
            #         'server_responsive': True,
            #         'service_available': True,
            #         'tools_registered': True
            #     },
            #     'issues': []
            # }

        Check health before operation:
            health = await health_check()
            if health['status'] == 'healthy':
                # Proceed with operation
                result = await generate_llms_txt('/path/to/project')
            else:
                print(f'Server unhealthy: {health["issues"]}')

    Raises:
        ServiceError: When health check fails internally

    Notes:
        - Health check is very fast (typically < 100ms)
        - No system resource information is collected
        - Focuses on core functionality only
        - Suitable for frequent polling
        - Returns quickly even if some services are degraded
    """
    try:
        log_with_context(logger, logging.INFO, "Tool called: health_check")
        result = await health_check_tool()
        return result
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in health_check: {e!s}",
            context={"error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to perform health check: {e!s}",
            service_name="health_check",
        ) from e


@mcp.tool()
async def analyze_repo(repo_path: str, include_analysis: bool = False, output_format: str = "text") -> dict[str, Any]:
    """Analyze repository for AI accessibility and provide comprehensive recommendations.

    This tool performs a thorough analysis of a repository's structure, documentation,
    and organization to assess its AI accessibility and provide actionable recommendations
    for improvement. It evaluates documentation quality, project structure, content
    organization, and calculates an AI accessibility score. The analysis helps you
    understand how well your repository is prepared for AI-assisted development and
    provides specific recommendations for improvement. This is the most comprehensive
    analysis tool available.

    Parameters:
        repo_path: Path to the repository directory to analyze
            - Must be a valid directory path
            - Directory must exist and be readable
            - Supports both absolute and relative paths
            - Example: '/home/user/my-repo' or './my-repo'

        include_analysis: Whether to include detailed file-by-file analysis (default: False)
            - When True, provides detailed analysis of individual files
            - When False, provides summary-level analysis only
            - Detailed analysis takes longer but provides more insights
            - Recommended: False for quick overview, True for comprehensive report

        output_format: Format for the formatted output (default: 'text')
            - Valid options: 'text', 'json', 'markdown'
            - 'text' provides human-readable plain text
            - 'json' provides structured JSON format
            - 'markdown' provides formatted markdown document
            - Example: 'text' for reading, 'json' for programmatic access

    Returns:
        Dictionary containing:
            - repo_path: Path to the analyzed repository
            - project_type: Detected project type
            - analysis: Comprehensive analysis dictionary with:
                - project_info: Basic project information
                - documentation_status: Status of documentation files
                - ai_accessibility: Accessibility score and factors
                - recommendations: List of improvement recommendations
                - detailed_analysis: File-by-file analysis (if include_analysis is True)
            - formatted_output: Formatted analysis in requested format
            - output_format: Format used for formatted output
            - recommendations_count: Number of recommendations provided
            - ai_accessibility_score: Overall accessibility score (0-100)

    Usage:
        Use this tool to get a comprehensive assessment of your repository's AI
        accessibility and detailed recommendations for improvement. It's ideal for:
        - Understanding current AI accessibility status
        - Getting specific improvement recommendations
        - Planning documentation improvements
        - Assessing repository readiness for AI tools

        The analysis provides actionable insights that help you prioritize
        documentation improvements for maximum AI accessibility impact.

    Examples:
        Basic repository analysis:
            result = await analyze_repo('/home/user/my-repo')
            # Returns: {
            #     'repo_path': '/home/user/my-repo',
            #     'ai_accessibility_score': 75,
            #     'recommendations_count': 5,
            #     'analysis': {...},
            #     'formatted_output': '...'
            # }

        Comprehensive analysis with detailed file review:
            result = await analyze_repo(
                repo_path='./my-project',
                include_analysis=True,
                output_format='markdown'
            )
            # Returns detailed analysis with file-by-file breakdown

        Get JSON format for programmatic access:
            result = await analyze_repo(
                'my-repo',
                output_format='json'
            )
            # Returns structured JSON for further processing

    Raises:
        ValidationError: When repo_path is empty or output_format is invalid
        ProjectAnalysisError: When repository path doesn't exist or isn't a directory
        ServiceError: When analysis process fails internally

    Notes:
        - Analysis is read-only and doesn't modify repository files
        - Accessibility score is calculated based on multiple factors
        - Recommendations are prioritized by impact
        - Detailed analysis may take longer for large repositories
        - Score of 80+ indicates good AI accessibility
        - Git repositories get enhanced metadata analysis
    """
    try:
        log_with_context(
            logger,
            logging.INFO,
            "Tool called: analyze_repo",
            context={"repo_path": repo_path, "include_analysis": include_analysis},
        )
        result = await analyze_repo_tool(repo_path, include_analysis, output_format)
        log_with_context(
            logger,
            logging.INFO,
            "Tool completed: analyze_repo",
            context={"repo_path": repo_path, "success": True},
        )
        return result
    except LLMTextMCPError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Tool error: analyze_repo - {e.message}",
            context={"repo_path": repo_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Unexpected error in analyze_repo: {e!s}",
            context={"repo_path": repo_path, "error_type": type(e).__name__},
        )
        logger.exception("Unexpected error")
        raise ServiceError(
            f"Failed to analyze repository: {e!s}",
            service_name="analyze_repo",
        ) from e


class LLMTextMCP:
    """LLM.txt MCP Server with stdio support for Claude Desktop."""

    def __init__(self):
        try:
            self.mcp = mcp
            self.service = LLMTextService()
            log_with_context(
                logger,
                logging.INFO,
                "LLM.txt MCP Server initialized",
                context={"server_name": "LLM.txt MCP Server", "version": "0.1.0"},
            )
        except Exception as e:
            log_with_context(
                logger,
                logging.ERROR,
                f"Failed to initialize server: {e!s}",
                context={"error_type": type(e).__name__},
                exc_info=True,
            )
            raise ServiceError(
                f"Failed to initialize server: {e!s}",
                service_name="LLMTextMCP",
            ) from e

    def run_stdio(self):
        """Run the MCP server with stdio transport for Claude Desktop."""
        try:
            log_with_context(
                logger,
                logging.INFO,
                "Starting LLM.txt MCP server with stdio transport",
                context={"transport": "stdio"},
            )
            self.mcp.run()
        except KeyboardInterrupt:
            log_with_context(
                logger,
                logging.INFO,
                "Server shutdown requested by user",
                context={"reason": "keyboard_interrupt"},
            )
        except Exception as e:
            log_with_context(
                logger,
                logging.ERROR,
                f"Server error: {e!s}",
                context={"error_type": type(e).__name__},
                exc_info=True,
            )
            raise ServiceError(
                f"Server runtime error: {e!s}",
                service_name="LLMTextMCP",
            ) from e
        finally:
            log_with_context(
                logger,
                logging.INFO,
                "LLM.txt MCP server stopped",
                context={"transport": "stdio"},
            )

    def run_http(self, host: str = "localhost", port: int = 8000):
        """Run the MCP server with HTTP transport (legacy support)."""
        try:
            log_with_context(
                logger,
                logging.INFO,
                f"Starting LLM.txt MCP server on {host}:{port}",
                context={"transport": "http", "host": host, "port": port},
            )
            self.mcp.run(host=host, port=port)
        except KeyboardInterrupt:
            log_with_context(
                logger,
                logging.INFO,
                "Server shutdown requested by user",
                context={"reason": "keyboard_interrupt"},
            )
        except Exception as e:
            log_with_context(
                logger,
                logging.ERROR,
                f"Server error: {e!s}",
                context={
                    "transport": "http",
                    "host": host,
                    "port": port,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise ServiceError(
                f"Server runtime error: {e!s}",
                service_name="LLMTextMCP",
            ) from e
        finally:
            log_with_context(
                logger,
                logging.INFO,
                "LLM.txt MCP server stopped",
                context={"transport": "http"},
            )


def main():
    """Main entry point with unified transport handling (FastMCP 2.14.4+)."""
    from .transport import run_server

    run_server(mcp, server_name="llm-txt-mcp")


if __name__ == "__main__":
    main()
