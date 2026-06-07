# LLM.txt MCP Server

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

> Automated generation and management of llms.txt documentation files for AI accessibility

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

The LLM.txt MCP Server provides comprehensive tools for generating, validating, and managing `llms.txt` files that make project documentation accessible to AI systems. Built with FastMCP for seamless integration with Claude Desktop and other MCP-compatible clients.

## Quick Start

```powershell
git clone https://github.com/sandraschi/llm-txt-mcp
cd llm-txt-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:

##  Features

- **Automated Generation**: Scan project directories and auto-generate structured llms.txt files
- **Multi-Language Support**: Detect and handle Python, TypeScript, React, FastAPI, Rust, Go, and more
- **Smart Documentation Discovery**: Intelligently categorize README files, API docs, examples, and configurations
- **Template System**: Pre-built templates for different project types
- **Validation & Updates**: Validate existing llms.txt files and update them while preserving custom content
- **Context Conversion**: Convert llms.txt to XML/JSON formats optimized for LLM consumption
- **Git Integration**: Leverage git repository information for enhanced project analysis

##  Requirements

- Python 3.11 or higher
- FastMCP 3.1.0+
- Git (optional, for enhanced project analysis)

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx llm-txt-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "llm-txt-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/llm-txt-mcp", "run", "llm-txt-mcp"]
  }
}
```
### From Source

```bash
git clone https://github.com/sandraschi/llm-txt-mcp.git
cd llm-txt-mcp
uv pip install -e .
```

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx llm-txt-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "llm-txt-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/llm-txt-mcp", "run", "llm-txt-mcp"]
  }
}
```
##  Configuration

### Claude Desktop Integration (Recommended)

Add to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "llm-txt-mcp": {
      "command": "llm-txt-mcp",
      "args": []
    }
  }
}
```

The server uses stdio transport for optimal performance with Claude Desktop.

### Development/HTTP Mode

For development and testing, you can run the server with HTTP transport:

```bash
llm-txt-mcp --host 127.0.0.1 --port 8000
```

Or use the development script:

```bash
python scripts/run_server.py --stdio  # For Claude Desktop
python scripts/run_server.py --host 127.0.0.1 --port 8000  # For HTTP
```

##  Available Tools

### Core Generation Tools

#### `generate_llms_txt`
Generate a complete llms.txt file for a project directory with automated content discovery.

**Parameters:**
- `project_path` (string): Path to the project directory
- `output_path` (string, optional): Custom output path
- `include_optional` (boolean, optional): Include optional sections (default: true)
- `scan_depth` (integer, optional): Directory scan depth (default: 3)

**Example:**
```python
generate_llms_txt(project_path="/path/to/my-project")
```

#### `validate_llms_txt`
Validate an existing llms.txt file for format compliance and completeness.

**Parameters:**
- `file_path` (string): Path to the llms.txt file to validate

**Returns:**
- Validation status, errors, warnings, and suggestions

#### `update_llms_txt`
Update an existing llms.txt file while preserving custom content and additions.

**Parameters:**
- `project_path` (string): Path to the project directory
- `regenerate_sections` (array, optional): Specific sections to regenerate
- `preserve_custom_content` (boolean, optional): Preserve manual additions (default: true)

#### `convert_to_context`
Convert llms.txt to XML or JSON format optimized for LLM consumption.

**Parameters:**
- `llms_txt_path` (string): Path to the llms.txt file
- `output_format` (string): Output format ("xml" or "json")
- `include_optional` (boolean, optional): Include optional sections

#### `scan_project_structure`
Analyze project structure and provide documentation recommendations.

**Parameters:**
- `project_path` (string): Path to the project directory
- `scan_depth` (integer, optional): Maximum scan depth
- `include_hidden` (boolean, optional): Include hidden files

#### `generate_from_template`
Generate llms.txt from predefined templates for common project types.

**Parameters:**
- `project_path` (string): Path to the project directory
- `template_name` (string): Template to use ("generic", "python", "typescript", "react", "fastapi")
- `custom_sections` (object, optional): Additional custom sections

### Utility Tools

#### `help`
Get comprehensive help information about available tools and server capabilities.

**Parameters:**
- `tool_name` (string, optional): Specific tool to get detailed help for
- `category` (string, optional): Filter tools by category ("generation", "validation", "analysis", "utility")

#### `status`
Get comprehensive server status and health information.

**Parameters:**
- `include_system_info` (boolean, optional): Include detailed system information
- `include_performance_metrics` (boolean, optional): Include performance metrics

#### `health_check`
Perform a quick health check of the server.

#### `analyze_repo`
Analyze repository for AI accessibility and provide comprehensive recommendations.

**Parameters:**
- `repo_path` (string): Path to the repository to analyze
- `include_analysis` (boolean, optional): Include detailed file-by-file analysis
- `output_format` (string, optional): Output format ("text", "json", "markdown")

##  Usage Examples

### Generate llms.txt for a Python Project

```bash
# Via Claude Desktop (MCP)
generate_llms_txt(project_path="/home/user/my-python-app")
```

This will create:
- `llms.txt` — fleet-style index (links to `llms-full.txt`, capped doc list)
- `llms-full.txt` — curated excerpts (secrets/paths sanitized; no debug dumps)

**Quality mode** (default `quality_mode=true`) skips `node_modules`, `.git`, lockfiles,
`debug_output.txt`, megatest guides, and `.env`. Set `quality_mode=false` only if you
need the legacy verbose dump behavior.

### Validate and Update Existing Documentation

```bash
# Validate current llms.txt
validate_llms_txt(file_path="/home/user/my-project/llms.txt")

# Update while preserving custom sections
update_llms_txt(project_path="/home/user/my-project", preserve_custom_content=true)
```

### Convert for LLM Context

```bash
# Generate XML context for Claude
convert_to_context(llms_txt_path="/home/user/my-project/llms.txt", output_format="xml")
```

### Analyze Repository for AI Accessibility

```bash
# Get comprehensive repository analysis
analyze_repo(repo_path="/home/user/my-project", output_format="text")
```

### Get Help and Status

```bash
# Get help for a specific tool
help(tool_name="generate_llms_txt")

# Check server status
status(include_system_info=true)

# Quick health check
health_check()
```

### Development Workflow

```bash
# Scan project structure
scan_project_structure(project_path="/home/user/my-project")

# Generate from template
generate_from_template(project_path="/home/user/my-project", template_name="python")
```

##  Generated File Structure

The tool generates structured documentation:

```
your-project/
 llms.txt              # Main documentation index
 llms-full.txt         # Complete content inclusion
 llms.ctx.xml          # XML context (if converted)
 llms.ctx.json         # JSON context (if converted)
```

### Example llms.txt Output

```markdown
# My Python Project
> A FastAPI application with automated documentation generation

## Docs
- [README](README.md): Project overview and setup instructions
- [API Documentation](docs/api.md): Complete API reference
- [Installation Guide](docs/install.md): Step-by-step installation

## API
- [Main Application](src/main.py): FastAPI application entry point
- [Models](src/models.py): Data models and schemas
- [Routes](src/routes.py): API endpoint definitions

## Examples
- [Basic Usage](examples/basic.py): Simple usage examples
- [Advanced Examples](examples/advanced.py): Complex implementation patterns

## Configuration
- [Project Config](pyproject.toml): Python project configuration and dependencies
- [Environment](config/env.py): Environment variables and settings

## Optional
- [Changelog](CHANGELOG.md): Version history and updates
- [Contributing](CONTRIBUTING.md): Guidelines for contributors
```

##  Project Type Detection

Automatically detects project types based on key files:

| Project Type | Key Files | Special Sections |
|-------------|-----------|------------------|
| **Python** | `pyproject.toml`, `setup.py`, `requirements.txt` | API, Configuration |
| **TypeScript** | `package.json`, `tsconfig.json` | Components, API |
| **React** | `package.json`, `src/App.tsx`, `public/index.html` | Components, Hooks, Styling |
| **FastAPI** | `main.py`, `app.py`, `requirements.txt` | API, Models, Deployment |
| **Rust** | `Cargo.toml`, `Cargo.lock` | API, Examples |
| **Go** | `go.mod`, `go.sum`, `main.go` | API, Examples |
| **Generic** | Any other structure | Docs, Examples, Optional |

##  Smart Documentation Discovery

The system intelligently categorizes documentation:

- **Priority Docs**: README, quickstart, installation, setup
- **API Documentation**: API definitions, endpoints, models, schemas
- **Examples**: Sample code, tutorials, demos
- **Configuration**: Project configs, environment files, settings
- **Optional**: Changelog, contributing guidelines, license info

##  Development

### Running Tests

```bash
pytest
pytest --cov=llm_txt_mcp tests/
```

### Code Quality

```bash
# Linting and formatting (using Ruff)
ruff check .
ruff format .

# Type checking
mypy .
```

### Local Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run the server directly
python -m llm_txt_mcp.server

# Test individual components
python -c "from llm_txt_mcp.service import LLMTextService; print('Service loaded')"
```

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/-feature`)
3. Commit your changes (`git commit -m 'Add  feature'`)
4. Push to the branch (`git push origin feature/-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for seamless MCP integration
- Inspired by the growing need for AI-accessible documentation
- Thanks to the Anthropic team for the MCP specification

##  Related Projects

- [FastMCP](https://github.com/jlowin/fastmcp) - Fast Model Context Protocol implementation
- [llms.txt specification](https://llms-txt.org/) - The standard for AI-readable documentation

---

**Made with  for the AI development community**


##  Webapp Dashboard

This MCP server includes a free, premium web interface for monitoring and control.
By default, the web dashboard runs on port **10836**.
*(Assigned ports: **10836** (Web dashboard frontend), **10837** (Web dashboard backend (API)))*

To start the webapp:
1. Navigate to the `webapp` (or `web`, `frontend`) directory.
2. Run `start.bat` (Windows) or `./start.ps1` (PowerShell).
3. Open `http://localhost:10836` in your browser.
