"""Core service implementation for LLM.txt generation and management."""

import logging
from pathlib import Path
from typing import Any

import aiofiles
from git import InvalidGitRepositoryError, Repo

from ..utils.generator import LLMTextGenerator
from ..utils.manifest_quality import (
    should_include_api_source,
    should_include_config_link,
    should_include_doc_file,
)

logger = logging.getLogger(__name__)


class DocumentationProject:
    """Represents a project with its documentation structure."""

    def __init__(self, path: Path, scan_depth: int = 6):
        self.path = path
        self.name = path.name
        self.scan_depth = max(1, min(scan_depth, 10))
        self.project_type: str | None = None
        self.documentation_files: list[Path] = []
        self.source_files: list[Path] = []
        self.config_files: list[Path] = []
        self.is_git_repo = False
        self.git_repo: Repo | None = None

        self._analyze_project()

    def _analyze_project(self) -> None:
        """Analyze the project structure and type."""
        # Check if it's a git repository
        try:
            self.git_repo = Repo(self.path)
            self.is_git_repo = True
        except InvalidGitRepositoryError:
            self.is_git_repo = False

        # Detect project type based on files
        self.project_type = self._detect_project_type()

        # Scan for documentation and source files
        self._scan_files()

    def _detect_project_type(self) -> str:
        """Detect the project type based on key files."""
        key_files = {
            "python": ["pyproject.toml", "setup.py", "requirements.txt", "poetry.lock"],
            "typescript": ["package.json", "tsconfig.json", "yarn.lock", "pnpm-lock.yaml"],
            "react": ["package.json", "src/App.tsx", "src/App.jsx", "public/index.html"],
            "fastapi": ["main.py", "app.py", "requirements.txt", "uvicorn"],
            "nextjs": ["next.config.js", "next.config.ts", "package.json"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "go": ["go.mod", "go.sum", "main.go"],
            "cpp": ["CMakeLists.txt", "Makefile", "*.cpp", "*.hpp"],
            "csharp": ["*.csproj", "*.sln", "Program.cs"],
            "java": ["pom.xml", "build.gradle", "*.java"],
        }

        for project_type, files in key_files.items():
            if any((self.path / f).exists() or list(self.path.glob(f)) for f in files):
                return project_type

        return "generic"

    def _scan_files(self) -> None:
        """Scan for documentation and source files (quality-filtered)."""
        doc_candidates: list[Path] = []

        for pattern in ("*.md", "*.rst"):
            doc_candidates.extend(self.path.glob(pattern))

        for folder in ("docs", "documentation"):
            docs_root = self.path / folder
            if docs_root.is_dir():
                for pattern in ("**/*.md", "**/*.rst"):
                    doc_candidates.extend(docs_root.glob(pattern))

        seen: set[Path] = set()
        for file in doc_candidates:
            resolved = file.resolve()
            if resolved in seen:
                continue
            if should_include_doc_file(file, self.path, self.scan_depth):
                seen.add(resolved)
                self.documentation_files.append(file)

        self.documentation_files.sort(key=lambda p: p.as_posix().lower())

        if self.project_type == "python" or (self.path / "src").is_dir():
            for py_file in (self.path / "src").rglob("*.py") if (self.path / "src").is_dir() else []:
                if should_include_api_source(py_file, self.path, self.scan_depth + 2):
                    self.source_files.append(py_file)

        for config_name in ("pyproject.toml", "package.json", "justfile", "glama.json"):
            for cfg in self.path.glob(config_name):
                if should_include_config_link(cfg, self.path):
                    self.config_files.append(cfg)

        self.source_files = list({f.resolve(): f for f in self.source_files}.values())
        self.config_files = list({f.resolve(): f for f in self.config_files}.values())


class LLMTextService:
    """Main service for LLM.txt generation and management."""

    def __init__(self):
        self.generator = LLMTextGenerator()
        self.templates = self._load_templates()

    def _load_templates(self) -> dict[str, dict[str, Any]]:
        """Load predefined templates for different project types."""
        return {
            "generic": {
                "sections": ["docs", "examples", "optional"],
                "description": "Generic project template",
            },
            "python": {
                "sections": ["docs", "api", "examples", "configuration", "optional"],
                "description": "Python project template with API documentation",
            },
            "typescript": {
                "sections": ["docs", "api", "components", "examples", "optional"],
                "description": "TypeScript/JavaScript project template",
            },
            "react": {
                "sections": ["docs", "components", "hooks", "examples", "styling", "optional"],
                "description": "React project template",
            },
            "fastapi": {
                "sections": ["docs", "api", "models", "examples", "deployment", "optional"],
                "description": "FastAPI project template",
            },
        }

    async def generate_project_llms_txt(
        self,
        project_path: str,
        output_path: str | None = None,
        include_optional: bool = True,
        scan_depth: int = 3,
        quality_mode: bool = True,
    ) -> dict[str, Any]:
        """Generate llms.txt and llms-full.txt for a project."""
        project = DocumentationProject(Path(project_path), scan_depth=scan_depth)

        # Generate the main llms.txt content
        llms_content = await self.generator.generate_from_project(
            project, include_optional, scan_depth, quality_mode=quality_mode
        )

        # Determine output paths
        output_dir = Path(output_path).parent if output_path else project.path
        llms_txt_path = output_dir / "llms.txt"
        llms_full_txt_path = output_dir / "llms-full.txt"

        # Write llms.txt file
        async with aiofiles.open(llms_txt_path, "w", encoding="utf-8") as f:
            await f.write(llms_content["llms_txt"])

        # Generate and write llms-full.txt
        full_content = await self.generator.generate_full_context(project, llms_content, quality_mode=quality_mode)
        async with aiofiles.open(llms_full_txt_path, "w", encoding="utf-8") as f:
            await f.write(full_content)

        return {
            "llms_txt_path": str(llms_txt_path),
            "llms_full_txt_path": str(llms_full_txt_path),
            "files_analyzed": len(project.documentation_files),
            "sections_created": len(llms_content["sections"]),
        }

    async def validate_llms_txt(self, file_path: str) -> dict[str, Any]:
        """Validate an llms.txt file."""
        path = Path(file_path)
        if not path.exists():
            return {
                "is_valid": False,
                "errors": [f"File not found: {file_path}"],
                "warnings": [],
                "suggestions": [],
            }

        async with aiofiles.open(path, encoding="utf-8") as f:
            content = await f.read()

        return self.generator.validate_llms_txt_format(content)

    async def update_llms_txt(
        self,
        project_path: str,
        regenerate_sections: list[str] | None = None,
        preserve_custom_content: bool = True,
    ) -> dict[str, Any]:
        """Update an existing llms.txt file."""
        project = DocumentationProject(Path(project_path))
        llms_txt_path = project.path / "llms.txt"

        if not llms_txt_path.exists():
            raise FileNotFoundError(f"No llms.txt found in {project_path}")

        # Read existing content
        async with aiofiles.open(llms_txt_path, encoding="utf-8") as f:
            existing_content = await f.read()

        # Parse and update
        updated_content = await self.generator.update_existing_llms_txt(
            existing_content, project, regenerate_sections, preserve_custom_content
        )

        # Write updated content
        async with aiofiles.open(llms_txt_path, "w", encoding="utf-8") as f:
            await f.write(updated_content["content"])

        return {
            "updated_sections": updated_content["updated_sections"],
            "preserved_content": updated_content["preserved_content"],
            "changes_made": updated_content["changes_made"],
        }

    async def convert_to_context(
        self, llms_txt_path: str, output_format: str = "xml", include_optional: bool = False
    ) -> dict[str, Any]:
        """Convert llms.txt to LLM context format."""
        path = Path(llms_txt_path)

        async with aiofiles.open(path, encoding="utf-8") as f:
            content = await f.read()

        # Parse the llms.txt content
        parsed = self.generator.parse_llms_txt(content)

        # Generate context in requested format
        if output_format.lower() == "xml":
            context = self.generator.generate_xml_context(parsed, include_optional)
            output_ext = ".xml"
        elif output_format.lower() == "json":
            context = self.generator.generate_json_context(parsed, include_optional)
            output_ext = ".json"
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Write output file
        output_path = path.with_suffix(f".ctx{output_ext}")
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(context)

        return {
            "output_path": str(output_path),
            "format": output_format,
            "token_count": len(context.split()),
        }

    async def scan_project_structure(
        self, project_path: str, scan_depth: int = 3, include_hidden: bool = False
    ) -> dict[str, Any]:
        """Scan and analyze project structure."""
        project = DocumentationProject(Path(project_path))

        # Analyze documentation potential
        suggestions = self._generate_suggestions(project)

        return {
            "project_type": project.project_type,
            "documentation_files": [str(f.relative_to(project.path)) for f in project.documentation_files],
            "source_files": [str(f.relative_to(project.path)) for f in project.source_files[:10]],
            "suggested_sections": suggestions["sections"],
            "recommendations": suggestions["recommendations"],
        }

    async def generate_from_template(
        self,
        project_path: str,
        template_name: str = "generic",
        custom_sections: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """Generate llms.txt from a template."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")

        project = DocumentationProject(Path(project_path))
        template = self.templates[template_name]

        # Generate content using template
        content = await self.generator.generate_from_template(project, template, custom_sections)

        # Write to file
        llms_txt_path = project.path / "llms.txt"
        async with aiofiles.open(llms_txt_path, "w", encoding="utf-8") as f:
            await f.write(content)

        return {
            "template_used": template_name,
            "llms_txt_path": str(llms_txt_path),
            "sections_created": len(template["sections"]),
        }

    def _generate_suggestions(self, project: DocumentationProject) -> dict[str, Any]:
        """Generate suggestions for improving documentation."""
        suggestions = {"sections": [], "recommendations": []}

        # Base sections
        suggestions["sections"].extend(["docs", "examples"])

        # Project-specific suggestions
        if project.project_type == "python":
            suggestions["sections"].extend(["api", "configuration"])
            if not any("requirements" in f.name.lower() for f in project.documentation_files):
                suggestions["recommendations"].append(
                    "Consider adding requirements.txt or pyproject.toml documentation"
                )

        elif project.project_type in ["typescript", "javascript", "react"]:
            suggestions["sections"].extend(["components", "api"])
            if not any("package.json" in f.name for f in project.documentation_files):
                suggestions["recommendations"].append("Consider documenting package.json dependencies")

        # General recommendations
        if not any("readme" in f.name.lower() for f in project.documentation_files):
            suggestions["recommendations"].append("Add a README.md file")

        if not any("example" in f.name.lower() for f in project.documentation_files):
            suggestions["recommendations"].append("Add usage examples")

        return suggestions
