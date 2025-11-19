# Contributing to LLM.txt MCP Server

Thank you for your interest in contributing to LLM.txt MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, FastMCP version)
- **Error messages** or logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** and motivation
- **Proposed solution** or implementation approach
- **Alternatives considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** (`pytest`)
6. **Ensure linting passes** (`ruff check .`)
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- pip or uv

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/llm-txt-mcp.git
cd llm-txt-mcp

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
ruff format .

# Run type checking
mypy .
```

## Coding Standards

### Python Style

- **Formatter**: Ruff (automatically formats code)
- **Linter**: Ruff (enforces code quality)
- **Type Checker**: MyPy (static type checking)
- **Line Length**: 100 characters maximum

### Code Quality

```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy .
```

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

### Documentation

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Required for all functions
- **Comments**: Explain "why", not "what"

Example:
```python
async def generate_llms_txt(
    project_path: str,
    output_path: Optional[str] = None,
    include_optional: bool = True,
) -> Dict[str, Any]:
    """Generate a complete llms.txt file for a project.
    
    Args:
        project_path: Path to the project directory
        output_path: Optional custom output path
        include_optional: Include optional sections
        
    Returns:
        Dictionary containing generation results
        
    Raises:
        ValueError: If project_path is invalid
    """
```

### Testing

- **Framework**: pytest
- **Coverage**: Aim for 80%+ coverage
- **Async Tests**: Use pytest-asyncio
- **Test Files**: `tests/test_*.py`

Example:
```python
import pytest
from llm_txt_mcp import LLMTextService

@pytest.mark.asyncio
async def test_generate_llms_txt():
    service = LLMTextService()
    result = await service.generate_llms_txt("/path/to/project")
    assert "llms_txt" in result
```

## Project Structure

```
llm-txt-mcp/
├── src/llm_txt_mcp/       # Main package
│   ├── models/            # Data models
│   ├── tools/             # MCP tools
│   ├── utils/             # Utilities
│   └── server.py          # MCP server
├── tests/                 # Test files
├── docs/                  # Documentation
└── scripts/               # Helper scripts
```

## Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(generator): add template system for project types
fix(validator): handle empty llms.txt files correctly
docs(readme): update installation instructions
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will handle the rest

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and discussions
- **Email**: sandra@sandraschi.dev

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes
- Project README (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to LLM.txt MCP Server!**
