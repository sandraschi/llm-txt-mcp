"""Unit tests for LLMTextService."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from llm_txt_mcp.models.service import DocumentationProject, LLMTextService


class TestDocumentationProject:
    """Test cases for DocumentationProject."""

    def test_project_initialization(self):
        """Test project initialization and analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "README.md").write_text("# Test Project\n> Test description")

            project = DocumentationProject(project_path)

            assert project.name == project_path.name
            assert project.path == project_path
            assert project.project_type == "generic"
            assert len(project.documentation_files) > 0

    def test_project_type_detection(self):
        """Test project type detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Test Python project
            (project_path / "pyproject.toml").write_text('[project]\nname = "test"')
            project = DocumentationProject(project_path)
            assert project.project_type == "python"

            # Test TypeScript project
            (project_path / "pyproject.toml").unlink()
            (project_path / "package.json").write_text('{"name": "test"}')
            project = DocumentationProject(project_path)
            assert project.project_type == "typescript"


class TestLLMTextService:
    """Test cases for LLMTextService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return LLMTextService()

    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, "generator")
        assert hasattr(service, "templates")
        assert "python" in service.templates
        assert "generic" in service.templates

    @pytest.mark.asyncio
    async def test_generate_project_llms_txt(self, service):
        """Test llms.txt generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "README.md").write_text("# Test Project\n> Test description")

            with patch.object(
                service.generator, "generate_from_project", new_callable=AsyncMock
            ) as mock_generate:
                mock_generate.return_value = {
                    "llms_txt": "# Test\n> Description\n## Docs\n- [README](README.md): Test",
                    "sections": {"docs": []},
                    "header": "# Test",
                }

                result = await service.generate_project_llms_txt(str(project_path))

                assert "llms_txt_path" in result
                assert "llms_full_txt_path" in result
                assert result["llms_txt_path"].endswith("llms.txt")
                assert result["llms_full_txt_path"].endswith("llms-full.txt")

    @pytest.mark.asyncio
    async def test_validate_llms_txt(self, service):
        """Test llms.txt validation."""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write("test content")

            with patch.object(service.generator, "validate_llms_txt_format") as mock_validate:
                mock_validate.return_value = {
                    "is_valid": True,
                    "errors": [],
                    "warnings": [],
                    "suggestions": [],
                }

                result = await service.validate_llms_txt(temp_path)

                assert result["is_valid"] is True
                assert len(result["errors"]) == 0
        finally:
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_scan_project_structure(self, service):
        """Test project structure scanning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "README.md").write_text("# Test")

            result = await service.scan_project_structure(str(project_path))

            assert "project_type" in result
            assert "documentation_files" in result
            assert "recommendations" in result

    def test_template_loading(self, service):
        """Test template loading."""
        templates = service.templates

        assert isinstance(templates, dict)
        assert "generic" in templates
        assert "python" in templates

        generic_template = templates["generic"]
        assert "sections" in generic_template
        assert "description" in generic_template
