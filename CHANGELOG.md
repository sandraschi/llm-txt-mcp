# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-07

### Added
- `manifest_quality` module: skip lists for junk dirs/files, excerpt embedding, PII/path sanitization
- `quality_mode` parameter on `generate_llms_txt` (default `true`) — fleet-style index + curated corpus
- Validation checks for `.git` links, machine paths, and missing `llms-full.txt` reference
- Tests: `test_manifest_quality.py`, `test_generation_quality.py`

### Changed
- `llms-full.txt` uses bounded excerpts instead of pasting entire repo files
- Doc scan limited to priority root markdown + `docs/` tree (no broad `*.txt` rglob)
- Index caps at 12 doc links; skips debug dumps, lockfiles, `.env`, megatest guides

## [0.1.0] - 2025-11-19

### Added
- Initial release of LLM.txt MCP Server
- Core generation engine for llms.txt files
- Project type detection (Python, TypeScript, React, Rust, Go, etc.)
- Smart documentation discovery and categorization
- Validation tool for llms.txt format compliance
- Update mechanism preserving custom content
- Context conversion to XML/JSON formats
- Repository analysis with AI accessibility scoring
- Template system for common project types
- FastMCP integration for Claude Desktop
- Comprehensive test suite (11 tests)
- Full documentation and examples

### Tools Implemented
- `generate_llms_txt`: Generate complete llms.txt files
- `validate_llms_txt`: Validate existing llms.txt files
- `update_llms_txt`: Update while preserving custom content
- `convert_to_context`: Convert to XML/JSON for LLM consumption
- `scan_project_structure`: Analyze project structure
- `generate_from_template`: Generate from predefined templates
- `analyze_repo`: Comprehensive repository analysis
- `help`: Get tool information and usage
- `status`: Server status and health information
- `health_check`: Quick health check

### Technical Stack
- Python 3.11+
- FastMCP 2.12.0+
- Ruff 0.14.5 (linting and formatting)
- MyPy 1.0+ (type checking)
- Pytest 7.0+ (testing)
- Pydantic 2.0+ (validation)

### Documentation
- Comprehensive README with examples
- API documentation for all tools
- Installation and configuration guides
- Development setup instructions
- MCP integration guide for Claude Desktop

---

## Release Notes Format

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

---

[Unreleased]: https://github.com/sandraschi/llm-txt-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sandraschi/llm-txt-mcp/releases/tag/v0.1.0
