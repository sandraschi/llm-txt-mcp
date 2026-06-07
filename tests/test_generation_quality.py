"""Integration tests for quality-aware manifest generation."""

from pathlib import Path

import pytest

from llm_txt_mcp.models.service import LLMTextService


@pytest.mark.asyncio
async def test_generate_excludes_junk_and_sanitizes(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo MCP\n\n> Short summary for bots.\n\n## Features\n\nFastMCP server.\n",
        encoding="utf-8",
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "INSTALL.md").write_text("# Install\n\nUse uv sync.\n", encoding="utf-8")
    (tmp_path / "debug_output.txt").write_text(
        '{"mcpServers": {"x": {"cwd": "D:/Dev/repos/secret-mcp"}}}',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")

    service = LLMTextService()
    result = await service.generate_project_llms_txt(str(tmp_path))

    llms = Path(result["llms_txt_path"]).read_text(encoding="utf-8")
    full = Path(result["llms_full_txt_path"]).read_text(encoding="utf-8")

    assert "llms-full.txt" in llms
    assert "debug_output" not in llms.lower()
    assert "D:/Dev/repos" not in full
    assert "Curated" in full or "excerpt" in full.lower()
    assert "README.md" in llms
