"""Quality rules for llms.txt / llms-full.txt — avoid junk, secrets, and PII in manifests."""

from __future__ import annotations

import re
from pathlib import Path

# Directory names never scanned (any depth)
SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "dist",
        "build",
        ".next",
        ".nuxt",
        "target",
        "__pycache__",
        ".ruff_cache",
        ".pytest_cache",
        ".mypy_cache",
        "htmlcov",
        ".coverage",
        "coverage",
        "_dashboard",
        "scripts/out",
        "agent-tools",
        "test-results",
        "http_cache",
        "markdown",
    }
)

# Never index or embed these file names (lowercase)
SKIP_FILE_NAMES: frozenset[str] = frozenset(
    {
        "llms.txt",
        "llms-full.txt",
        "debug_output.txt",
        "build_log.txt",
        ".env",
        ".env.local",
        ".env.example",
        "tasks.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "uv.lock",
        "config",
    }
)

# Path fragments that indicate test dumps or local-only noise
SKIP_PATH_FRAGMENTS: tuple[str, ...] = (
    "/.git/",
    "\\.git\\",
    "debug_output",
    "megatest",
    "UNIVERSAL_MCP_MEGATEST",
    "_llm_test_scripts",
    "egg-info",
    ".cursor/",
    "agent-tools/",
)

# Root markdown files always allowed (if present)
PRIORITY_ROOT_DOCS: frozenset[str] = frozenset(
    {
        "readme.md",
        "install.md",
        "changelog.md",
        "license.md",
        "prd.md",
        "contributing.md",
        "agents.md",
    }
)

# Safe config files for index links only (never embed secrets from .env)
SAFE_CONFIG_NAMES: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "package.json",
        "cargo.toml",
        "go.mod",
        "justfile",
        "glama.json",
        "manifest.json",
    }
)

MAX_INDEX_DOCS = 12
MAX_EXCERPT_LINES = 80
MAX_EXCERPT_CHARS = 6000
MAX_EMBED_FILE_BYTES = 80_000

_SECRET_LINE = re.compile(r"(?i)(api[_-]?key|secret|token|password|auth_token|bearer)\s*[:=]\s*\S+")
_WIN_USER_PATH = re.compile(r"[A-Za-z]:\\Users\\[^\\]+", re.IGNORECASE)
_WIN_DEV_PATH = re.compile(r"[A-Za-z]:[/\\]Dev[/\\]repos", re.IGNORECASE)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")


def path_has_skip_fragment(rel_posix: str) -> bool:
    lower = rel_posix.lower()
    return any(frag.lower() in lower for frag in SKIP_PATH_FRAGMENTS)


def is_skip_dir_name(name: str) -> bool:
    return name.lower() in SKIP_DIR_NAMES or name.startswith(".")


def relative_depth(path: Path, root: Path) -> int:
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return 99


def should_include_doc_file(path: Path, root: Path, max_depth: int = 6) -> bool:
    """Whether a documentation file belongs in the llms.txt index."""
    if not path.is_file():
        return False
    name_lower = path.name.lower()
    if name_lower in SKIP_FILE_NAMES:
        return False
    if path_has_skip_fragment(path.relative_to(root).as_posix()):
        return False
    if relative_depth(path, root) > max_depth:
        return False

    for part in path.relative_to(root).parts[:-1]:
        if is_skip_dir_name(part):
            return False

    suffix = path.suffix.lower()
    if suffix not in {".md", ".rst"}:
        return False

    rel_parts = path.relative_to(root).parts
    if len(rel_parts) == 1:
        return name_lower in PRIORITY_ROOT_DOCS

    if rel_parts[0].lower() in {"docs", "documentation"}:
        # Skip enormous internal test guides
        if "testing" in rel_parts and "megatest" in name_lower:
            return False
        return True

    return False


def should_include_api_source(path: Path, root: Path, max_depth: int = 8) -> bool:
    """Limited API-ish source files for index (not bulk embed)."""
    if path.suffix.lower() != ".py":
        return False
    if path_has_skip_fragment(path.relative_to(root).as_posix()):
        return False
    if relative_depth(path, root) > max_depth:
        return False
    rel = path.relative_to(root).as_posix().lower()
    if not rel.startswith("src/"):
        return False
    lower_name = path.name.lower()
    if any(x in lower_name for x in ("test_", "_test.py", "conftest")):
        return False
    return any(
        k in lower_name or k in rel for k in ("api_router", "router", "routes", "server.py", "mcp_server", "main.py")
    )


def should_include_config_link(path: Path, root: Path) -> bool:
    if path.name.lower() not in {n.lower() for n in SAFE_CONFIG_NAMES}:
        return False
    if relative_depth(path, root) > 3:
        return False
    return not path_has_skip_fragment(path.relative_to(root).as_posix())


def should_embed_file(path: Path, root: Path) -> bool:
    """Whether file content may appear inside llms-full.txt."""
    if not path.is_file():
        return False
    if path.stat().st_size > MAX_EMBED_FILE_BYTES:
        return False
    name_lower = path.name.lower()
    if name_lower in SKIP_FILE_NAMES:
        return False
    if name_lower.endswith((".json", ".lock", ".toml")) and name_lower not in {
        "pyproject.toml",
        "glama.json",
    }:
        return False
    if name_lower == "pyproject.toml":
        return True
    return should_include_doc_file(path, root)


def sanitize_embedded_text(text: str) -> str:
    """Redact secrets and fingerprint paths in embedded excerpts."""
    lines: list[str] = []
    for line in text.splitlines():
        if _SECRET_LINE.search(line):
            lines.append(_SECRET_LINE.sub(r"\1=<redacted>", line))
            continue
        line = _WIN_USER_PATH.sub("~/", line)
        line = _WIN_DEV_PATH.sub("{REPOS_DIR}", line)
        lines.append(line)
    return "\n".join(lines)


def excerpt_markdown(text: str, max_lines: int = MAX_EXCERPT_LINES, max_chars: int = MAX_EXCERPT_CHARS) -> str:
    """Take a bounded excerpt: title + first sections, not the whole file."""
    lines = text.splitlines()
    out: list[str] = []
    section_count = 0
    for line in lines:
        if line.startswith("## "):
            section_count += 1
            if section_count > 4:
                out.append("\n[... excerpt truncated — see source file in repo ...]")
                break
        out.append(line)
        if len(out) >= max_lines:
            out.append("\n[... excerpt truncated by line limit ...]")
            break
    body = sanitize_embedded_text("\n".join(out))
    if len(body) > max_chars:
        body = body[: max_chars - 48].rstrip() + "\n\n[... excerpt truncated by size limit ...]"
    return body


def validate_manifest_links(content: str) -> dict[str, list[str]]:
    """Extra validation for bot-facing manifests."""
    errors: list[str] = []
    warnings: list[str] = []

    lower = content.lower()
    if "llms-full.txt" not in lower:
        warnings.append("Missing reference to llms-full.txt (fleet index should link to corpus)")

    if ".git/" in lower or ".git\\" in lower:
        errors.append("Manifest links to .git paths — remove")

    for bad in ("debug_output", ".env", "tasks.json", "package-lock.json"):
        if bad in lower:
            warnings.append(f"Manifest may reference local-only artifact: {bad}")

    if "d:/dev/repos" in lower or "d:\\dev\\repos" in lower:
        warnings.append("Manifest contains machine-specific D:/Dev/repos paths")

    return {"errors": errors, "warnings": warnings}
