"""Tests for manifest quality filters."""

from pathlib import Path

from llm_txt_mcp.utils.manifest_quality import (
    excerpt_markdown,
    sanitize_embedded_text,
    should_embed_file,
    should_include_doc_file,
    validate_manifest_links,
)


def test_skips_debug_and_llms_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Hi", encoding="utf-8")
    (tmp_path / "debug_output.txt").write_text("secret", encoding="utf-8")
    (tmp_path / "llms-full.txt").write_text("old", encoding="utf-8")

    assert should_include_doc_file(tmp_path / "README.md", tmp_path)
    assert not should_include_doc_file(tmp_path / "debug_output.txt", tmp_path)
    assert not should_embed_file(tmp_path / "llms-full.txt", tmp_path)


def test_skips_git_and_node_modules(tmp_path: Path) -> None:
    git_doc = tmp_path / ".git" / "hooks" / "README.md"
    git_doc.parent.mkdir(parents=True)
    git_doc.write_text("nope", encoding="utf-8")
    nm_doc = tmp_path / "node_modules" / "pkg" / "readme.md"
    nm_doc.parent.mkdir(parents=True)
    nm_doc.write_text("nope", encoding="utf-8")

    assert not should_include_doc_file(git_doc, tmp_path)
    assert not should_include_doc_file(nm_doc, tmp_path)


def test_allows_docs_tree(tmp_path: Path) -> None:
    doc = tmp_path / "docs" / "INSTALL.md"
    doc.parent.mkdir()
    doc.write_text("# Install", encoding="utf-8")
    assert should_include_doc_file(doc, tmp_path)


def test_sanitize_redacts_secrets_and_paths() -> None:
    raw = "api_key=sk-live-abc\npath D:\\Dev\\repos\\foo\nuser C:\\Users\\alice\\AppData"
    out = sanitize_embedded_text(raw)
    assert "sk-live" not in out
    assert "<redacted>" in out
    assert "{REPOS_DIR}" in out
    assert "alice" not in out


def test_excerpt_truncates_long_markdown() -> None:
    lines = ["# Title", "> summary"] + [f"line {i}" for i in range(200)]
    text = "\n".join(lines)
    out = excerpt_markdown(text, max_lines=20, max_chars=500)
    assert "truncated" in out.lower()
    assert len(out) < len(text)


def test_validate_manifest_links_flags_git() -> None:
    bad = "# x\n> y\n## Docs\n- [Git](.git/config): bad\n"
    result = validate_manifest_links(bad)
    assert result["errors"]


def test_validate_manifest_links_warns_missing_full() -> None:
    content = "# x\n> y\n## Docs\n- [Readme](README.md): ok\n"
    result = validate_manifest_links(content)
    assert any("llms-full" in w for w in result["warnings"])
