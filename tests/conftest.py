"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Create basic project structure
        (project_path / "README.md").write_text("# Test Project\n> Test description")
        (project_path / "pyproject.toml").write_text('[project]\nname = "test"')

        # Create some source files
        src_dir = project_path / "src" / "test_project"
        src_dir.mkdir(parents=True)
        (src_dir / "main.py").write_text('"""Main module."""\ndef main():\n    pass')

        yield project_path


@pytest.fixture
def temp_llms_txt_file():
    """Create a temporary llms.txt file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# Test Project\n> Test description\n\n## Docs\n- [README](README.md): Test")
        temp_file = f.name

    yield temp_file

    # Cleanup
    Path(temp_file).unlink(missing_ok=True)
