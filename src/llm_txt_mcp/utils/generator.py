"""LLM.txt content generation and formatting utilities."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import aiofiles

if TYPE_CHECKING:
    from ..models.service import DocumentationProject


class LLMTextGenerator:
    """Handles the generation and formatting of llms.txt content."""

    def __init__(self) -> None:
        self.section_order = [
            "docs",
            "api",
            "components",
            "examples",
            "configuration",
            "deployment",
            "optional",
        ]

    async def generate_from_project(
        self,
        project: "DocumentationProject",
        include_optional: bool = True,
        scan_depth: int = 3,
    ) -> Dict[str, Any]:
        """Generate llms.txt content from a project."""
        sections = {}

        # Generate header
        header = self._generate_header(project)

        # Process documentation files by category
        docs_section = await self._process_documentation_files(project)
        if docs_section:
            sections["docs"] = docs_section

        # Process source files for API documentation
        api_section = await self._process_api_files(project)
        if api_section:
            sections["api"] = api_section

        # Generate examples section
        examples_section = await self._process_examples(project)
        if examples_section:
            sections["examples"] = examples_section

        # Generate configuration section
        config_section = await self._process_configuration(project)
        if config_section:
            sections["configuration"] = config_section

        # Generate optional section
        if include_optional:
            optional_section = await self._process_optional_content(project)
            if optional_section:
                sections["optional"] = optional_section

        # Build final llms.txt content
        llms_txt_content = self._build_llms_txt(header, sections)

        return {"llms_txt": llms_txt_content, "sections": sections, "header": header}

    def _generate_header(self, project: "DocumentationProject") -> str:
        """Generate the header section of llms.txt."""
        # Try to extract description from README
        description = self._extract_project_description(project)

        if not description:
            project_type = project.project_type or "unknown"
            description = f"{project_type.title()} project with automated documentation generation"

        return f"# {project.name}\n> {description}\n"

    def _extract_project_description(self, project: "DocumentationProject") -> Optional[str]:
        """Extract project description from README or other files."""
        readme_files = [f for f in project.documentation_files if "readme" in f.name.lower()]

        if not readme_files:
            return None

        try:
            with open(readme_files[0], "r", encoding="utf-8") as f:
                content = f.read()

            # Look for first paragraph after title
            lines = content.split("\n")
            description_lines = []

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line and not line.startswith("!") and not line.startswith("["):
                    description_lines.append(line)
                    if len(" ".join(description_lines)) > 200:
                        break

            description = " ".join(description_lines)
            return description[:200] + "..." if len(description) > 200 else description

        except Exception:
            return None

    async def _process_documentation_files(
        self, project: "DocumentationProject"
    ) -> List[Dict[str, str]]:
        """Process documentation files into links."""
        docs = []

        # Prioritize important documentation
        priority_docs = [
            "readme",
            "quickstart",
            "getting-started",
            "installation",
            "setup",
        ]

        # Add priority docs first
        for priority in priority_docs:
            matching_files = [
                f
                for f in project.documentation_files
                if priority in f.name.lower() and f.suffix in [".md", ".rst", ".txt"]
            ]
            for file in matching_files:
                docs.append(
                    {
                        "title": self._format_title(file.name),
                        "url": str(file.relative_to(project.path)),
                        "description": await self._extract_file_description(file),
                    }
                )

        # Add other documentation files
        added_files = {d["url"] for d in docs}
        for file in project.documentation_files:
            rel_path = str(file.relative_to(project.path))
            if rel_path not in added_files and file.suffix in [".md", ".rst", ".txt"]:
                docs.append(
                    {
                        "title": self._format_title(file.name),
                        "url": rel_path,
                        "description": await self._extract_file_description(file),
                    }
                )

        return docs[:10]  # Limit to avoid clutter

    async def _process_api_files(self, project: "DocumentationProject") -> List[Dict[str, str]]:
        """Process source files to generate API documentation links."""
        api_docs = []

        # Look for API-related files
        api_patterns = ["api", "endpoints", "routes", "models", "schemas"]

        for pattern in api_patterns:
            matching_files = [
                f
                for f in project.source_files
                if pattern in f.name.lower() or pattern in str(f.parent).lower()
            ]

            for file in matching_files[:3]:  # Limit per pattern
                api_docs.append(
                    {
                        "title": self._format_title(file.name),
                        "url": str(file.relative_to(project.path)),
                        "description": f"{pattern.title()} definitions and implementations",
                    }
                )

        return api_docs

    async def _process_examples(self, project: "DocumentationProject") -> List[Dict[str, str]]:
        """Process example files and directories."""
        examples = []

        # Look for example directories and files
        example_patterns = ["example", "sample", "demo", "tutorial"]

        for pattern in example_patterns:
            # Check for directories
            example_dirs = [
                d for d in project.path.iterdir() if d.is_dir() and pattern in d.name.lower()
            ]

            for dir_path in example_dirs:
                examples.append(
                    {
                        "title": self._format_title(dir_path.name),
                        "url": str(dir_path.relative_to(project.path)) + "/",
                        "description": f"{pattern.title()} code and implementations",
                    }
                )

            # Check for files
            example_files = [
                f
                for f in project.documentation_files + project.source_files
                if pattern in f.name.lower()
            ]

            for file in example_files[:2]:  # Limit per pattern
                examples.append(
                    {
                        "title": self._format_title(file.name),
                        "url": str(file.relative_to(project.path)),
                        "description": f"{pattern.title()} usage and code samples",
                    }
                )

        return examples[:5]  # Limit total examples

    async def _process_configuration(self, project: "DocumentationProject") -> List[Dict[str, str]]:
        """Process configuration files."""
        config_docs = []

        # Configuration file patterns
        config_patterns = {
            "pyproject.toml": "Python project configuration and dependencies",
            "package.json": "Node.js project configuration and dependencies",
            "Cargo.toml": "Rust project configuration and dependencies",
            "go.mod": "Go module configuration and dependencies",
            ".env": "Environment variables and configuration",
            "config": "Application configuration files",
            "settings": "Application settings and configuration",
        }

        for pattern, description in config_patterns.items():
            matching_files = [f for f in project.path.rglob(pattern) if f.is_file()]
            for file in matching_files[:1]:  # One per pattern
                config_docs.append(
                    {
                        "title": self._format_title(file.name),
                        "url": str(file.relative_to(project.path)),
                        "description": description,
                    }
                )

        return config_docs

    async def _process_optional_content(
        self, project: "DocumentationProject"
    ) -> List[Dict[str, str]]:
        """Process optional/secondary content."""
        optional = []

        # Secondary documentation
        secondary_patterns = [
            "changelog",
            "contributing",
            "license",
            "history",
            "roadmap",
        ]

        for pattern in secondary_patterns:
            matching_files = [f for f in project.documentation_files if pattern in f.name.lower()]
            for file in matching_files[:1]:  # One per pattern
                optional.append(
                    {
                        "title": self._format_title(file.name),
                        "url": str(file.relative_to(project.path)),
                        "description": f"Project {pattern} information",
                    }
                )

        return optional

    async def _extract_file_description(self, file_path: Path) -> str:
        """Extract description from a file's content."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

            # For markdown files, look for first paragraph
            if file_path.suffix == ".md":
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("!"):
                        return line[:100] + "..." if len(line) > 100 else line

            # For Python files, look for module docstring
            elif file_path.suffix == ".py":
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    docstring = docstring_match.group(1).strip()
                    return docstring.split("\n")[0][:100]

            # Default based on filename
            return f"Documentation for {file_path.stem}"

        except Exception:
            return f"Documentation for {file_path.stem}"

    def _format_title(self, filename: str) -> str:
        """Format filename into a readable title."""
        # Remove extension
        title = filename.split(".")[0]

        # Replace separators with spaces
        title = re.sub(r"[_-]", " ", title)

        # Title case
        title = title.title()

        return title

    def _build_llms_txt(self, header: str, sections: Dict[str, List[Dict[str, str]]]) -> str:
        """Build the final llms.txt content."""
        content = [header]

        # Add project context
        content.append(
            "This project includes automated llms.txt generation for AI accessibility.\n"
        )

        # Add sections in order
        for section_name in self.section_order:
            if section_name in sections and sections[section_name]:
                content.append(f"## {section_name.title()}")

                for item in sections[section_name]:
                    title = item["title"]
                    url = item["url"]
                    description = item["description"]
                    content.append(f"- [{title}]({url}): {description}")

                content.append("")  # Empty line between sections

        return "\n".join(content)

    async def generate_full_context(
        self, project: "DocumentationProject", llms_content: Dict[str, Any]
    ) -> str:
        """Generate llms-full.txt with complete content."""
        full_content = [llms_content["header"]]
        full_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Include all file contents
        for section_name, items in llms_content["sections"].items():
            full_content.append(f"## {section_name.title()} - Full Content\n")

            for item in items:
                file_path = project.path / item["url"]
                if file_path.is_file() and file_path.stat().st_size < 100000:  # Max 100KB per file
                    try:
                        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                            content = await f.read()

                        full_content.append(f"### {item['title']}")
                        full_content.append(f"Source: {item['url']}")
                        full_content.append("```")
                        full_content.append(content)
                        full_content.append("```\n")

                    except Exception:
                        full_content.append(f"### {item['title']}")
                        full_content.append(f"Source: {item['url']}")
                        full_content.append("*Content could not be read*\n")

        return "\n".join(full_content)

    def validate_llms_txt_format(self, content: str) -> Dict[str, Any]:
        """Validate llms.txt format."""
        errors = []
        warnings = []
        suggestions = []

        lines = content.split("\n")

        # Check for H1 header
        if not any(line.startswith("# ") for line in lines):
            errors.append("Missing H1 header with project name")

        # Check for blockquote summary
        if not any(line.startswith("> ") for line in lines):
            warnings.append("Consider adding a blockquote summary after the title")

        # Check for sections
        sections = [line for line in lines if line.startswith("## ")]
        if not sections:
            warnings.append("No H2 sections found")

        # Check for links
        links = [line for line in lines if "- [" in line and "](" in line]
        if not links:
            warnings.append("No markdown links found in sections")

        # Suggestions
        if len(sections) < 3:
            suggestions.append("Consider adding more sections (docs, examples, optional)")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
        }

    def parse_llms_txt(self, content: str) -> Dict[str, Any]:
        """Parse llms.txt content into structured data."""
        lines = content.split("\n")

        parsed = {"title": "", "summary": "", "info": "", "sections": {}}

        current_section = None
        current_content: List[str] = []

        for line in lines:
            line = line.strip()

            if line.startswith("# "):
                parsed["title"] = line[2:].strip()
            elif line.startswith("> "):
                parsed["summary"] = line[2:].strip()
            elif line.startswith("## "):
                # Save previous section
                if current_section:
                    parsed["sections"][current_section] = current_content

                # Start new section
                current_section = line[3:].strip().lower()
                current_content = []
            elif line.startswith("- [") and current_section:
                current_content.append(line)
            elif not line.startswith("#") and not current_section and line:
                parsed["info"] += line + "\n"

        # Save last section
        if current_section:
            parsed["sections"][current_section] = current_content

        return parsed

    def generate_xml_context(self, parsed: Dict[str, Any], include_optional: bool = False) -> str:
        """Generate XML context from parsed llms.txt."""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append("<llms_context>")
        xml_lines.append(f"  <title>{parsed['title']}</title>")
        xml_lines.append(f"  <summary>{parsed['summary']}</summary>")

        if parsed["info"]:
            xml_lines.append(f"  <info>{parsed['info'].strip()}</info>")

        xml_lines.append("  <sections>")

        for section_name, items in parsed["sections"].items():
            if section_name == "optional" and not include_optional:
                continue

            xml_lines.append(f'    <section name="{section_name}">')
            for item in items:
                xml_lines.append(f"      <item>{item}</item>")
            xml_lines.append("    </section>")

        xml_lines.append("  </sections>")
        xml_lines.append("</llms_context>")

        return "\n".join(xml_lines)

    def generate_json_context(self, parsed: Dict[str, Any], include_optional: bool = False) -> str:
        """Generate JSON context from parsed llms.txt."""
        context = {
            "title": parsed["title"],
            "summary": parsed["summary"],
            "info": parsed["info"].strip(),
            "sections": {},
        }

        for section_name, items in parsed["sections"].items():
            if section_name == "optional" and not include_optional:
                continue
            context["sections"][section_name] = items

        return json.dumps(context, indent=2, ensure_ascii=False)

    async def generate_from_template(
        self,
        project: "DocumentationProject",
        template: Dict[str, Any],
        custom_sections: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """Generate llms.txt from a template."""
        header = self._generate_header(project)
        content = [header]

        # Add template description
        content.append(f"Generated from {template['description']}.\n")

        # Generate sections based on template
        for section_name in template["sections"]:
            content.append(f"## {section_name.title()}")

            # Add placeholder content for each section
            if section_name == "docs":
                content.append("- [README](README.md): Project overview and setup instructions")
                content.append("- [API Documentation](docs/api.md): Complete API reference")
            elif section_name == "examples":
                content.append("- [Basic Usage](examples/basic.md): Simple usage examples")
                content.append(
                    "- [Advanced Examples](examples/advanced.md): Complex implementation patterns"
                )
            elif section_name == "configuration":
                content.append(
                    "- [Environment Setup](config/env.md): Environment configuration guide"
                )
                content.append("- [Settings](config/settings.md): Application settings and options")
            elif section_name == "optional":
                content.append("- [Changelog](CHANGELOG.md): Version history and updates")
                content.append("- [Contributing](CONTRIBUTING.md): Guidelines for contributors")

            # Add custom sections if provided
            if custom_sections and section_name in custom_sections:
                for custom_item in custom_sections[section_name]:
                    content.append(f"- {custom_item}")

            content.append("")  # Empty line

        return "\n".join(content)

    async def update_existing_llms_txt(
        self,
        existing_content: str,
        project: "DocumentationProject",
        regenerate_sections: Optional[List[str]] = None,
        preserve_custom_content: bool = True,
    ) -> Dict[str, Any]:
        """Update existing llms.txt content."""
        # Parse existing content
        parsed = self.parse_llms_txt(existing_content)

        # Generate new content
        new_content = await self.generate_from_project(project)

        # Merge content
        updated_sections = []
        preserved_content = []
        changes_made = []

        if regenerate_sections:
            # Only update specified sections
            for section in regenerate_sections:
                if section in new_content["sections"]:
                    parsed["sections"][section] = new_content["sections"][section]
                    updated_sections.append(section)
                    changes_made.append(f"Regenerated {section} section")
        else:
            # Update all sections
            for section, content in new_content["sections"].items():
                if section in parsed["sections"] and preserve_custom_content:
                    # Check if custom content exists
                    existing_items = len(parsed["sections"][section])
                    new_items = len(content)
                    if existing_items > new_items:
                        preserved_content.append(f"Preserved custom content in {section}")

                parsed["sections"][section] = content
                updated_sections.append(section)
                changes_made.append(f"Updated {section} section")

        # Rebuild content
        rebuilt_content = self._build_llms_txt(
            f"# {parsed['title']}\n> {parsed['summary']}\n", parsed["sections"]
        )

        return {
            "content": rebuilt_content,
            "updated_sections": updated_sections,
            "preserved_content": preserved_content,
            "changes_made": changes_made,
        }
