"""Integration tests for MCP tools."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_txt_mcp.tools.tools import generate_llms_txt_tool, get_service, validate_llms_txt_tool


class TestMCPTools:
    """Test cases for MCP tools."""

    @pytest.mark.asyncio
    async def test_generate_llms_txt_tool(self):
        """Test the generate_llms_txt tool."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "README.md").write_text("# Test Project\n> Test description")

            with patch("llm_txt_mcp.tools.tools.get_service") as mock_get_service:
                mock_service = MagicMock()
                mock_service.generate_project_llms_txt = AsyncMock(
                    return_value={
                        "llms_txt_path": str(project_path / "llms.txt"),
                        "llms_full_txt_path": str(project_path / "llms-full.txt"),
                        "files_analyzed": 1,
                        "sections_created": 1,
                    }
                )
                mock_get_service.return_value = mock_service

                result = await generate_llms_txt_tool(str(project_path))

                assert "llms_txt_path" in result
                assert "files_analyzed" in result
                mock_service.generate_project_llms_txt.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_llms_txt_tool(self):
        """Test the validate_llms_txt tool."""
        with patch("llm_txt_mcp.tools.tools.get_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.validate_llms_txt = AsyncMock(
                return_value={"is_valid": True, "errors": [], "warnings": [], "suggestions": []}
            )
            mock_get_service.return_value = mock_service

            result = await validate_llms_txt_tool("dummy_path")

            assert "is_valid" in result
            assert result["is_valid"] is True
            mock_service.validate_llms_txt.assert_called_once_with(file_path="dummy_path")

    @pytest.mark.asyncio
    async def test_generate_llms_txt_tool_error_handling(self):
        """Test error handling in generate_llms_txt tool."""
        with patch("llm_txt_mcp.tools.tools.get_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.generate_project_llms_txt = AsyncMock(side_effect=Exception("Test error"))
            mock_get_service.return_value = mock_service

            with pytest.raises(Exception, match="Test error"):
                await generate_llms_txt_tool("invalid_path")

    def test_get_service_singleton(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2
        assert isinstance(service1, object)  # Basic check that it's a service instance
