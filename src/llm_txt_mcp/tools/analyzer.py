import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from ..exceptions import ProjectAnalysisError
from ..utils.logging import get_logger, log_with_context
from .tools import get_service

if TYPE_CHECKING:
    from ..models.service import DocumentationProject, LLMTextService

logger = get_logger(__name__)


# Tool function without decorator - will be registered in server.py
async def analyze_repo_tool(
    repo_path: str, include_analysis: bool = False, output_format: str = "text"
) -> Dict[str, Any]:
    """
    Analyze repository for AI accessibility and provide comprehensive recommendations.

    This tool performs a thorough analysis of the repository structure and content,
    providing detailed insights and recommendations for improving AI accessibility
    through better llms.txt implementation. The output is optimized for Claude users.

    Parameters:
        repo_path (str): Path to the repository to analyze
        include_analysis (bool, optional): Include detailed file-by-file analysis
        output_format (str, optional): Output format ("text", "json", "markdown")

    Returns:
        dict: Comprehensive repository analysis with recommendations
    """
    try:
        if not repo_path:
            raise ProjectAnalysisError("repo_path is required", project_path=repo_path or "")

        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            raise ProjectAnalysisError(
                f"Repository path does not exist: {repo_path}",
                project_path=repo_path,
            )

        log_with_context(
            logger,
            logging.INFO,
            "Analyzing repository",
            context={"repo_path": repo_path, "include_analysis": include_analysis},
        )

        # Create project instance for analysis
        project = DocumentationProject(Path(repo_path))

        # Get service for additional analysis
        service = get_service()

        # Perform comprehensive analysis
        analysis = await _perform_comprehensive_analysis(project, service, include_analysis)

        # Format output based on requested format
        if output_format.lower() == "json":
            formatted_output = json.dumps(analysis, indent=2, ensure_ascii=False)
        elif output_format.lower() == "markdown":
            formatted_output = _format_analysis_as_markdown(analysis)
        else:  # text
            formatted_output = _format_analysis_as_text(analysis)

        result = {
            "repo_path": repo_path,
            "project_type": project.project_type,
            "analysis": analysis,
            "formatted_output": formatted_output,
            "output_format": output_format,
            "recommendations_count": len(analysis.get("recommendations", [])),
            "ai_accessibility_score": _calculate_accessibility_score(analysis),
        }

        log_with_context(
            logger,
            logging.INFO,
            "Repository analysis completed",
            context={"repo_path": repo_path, "success": True},
        )
        return result

    except ProjectAnalysisError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error analyzing repository: {e.message}",
            context={"repo_path": repo_path, "error": e.to_dict()},
        )
        raise
    except Exception as e:
        logger.exception(f"Unexpected error analyzing repository {repo_path}")
        raise ProjectAnalysisError(
            f"Failed to analyze repository: {str(e)}",
            project_path=repo_path,
        ) from e


async def _perform_comprehensive_analysis(
    project: "DocumentationProject",
    service: "LLMTextService",
    include_detailed_analysis: bool,
) -> Dict[str, Any]:
    """Perform comprehensive repository analysis."""
    analysis = {
        "project_info": {
            "name": project.name,
            "path": str(project.path),
            "type": project.project_type,
            "is_git_repo": project.is_git_repo,
            "total_files": len(project.documentation_files) + len(project.source_files),
        },
        "documentation_status": {
            "has_readme": any("readme" in f.name.lower() for f in project.documentation_files),
            "has_llms_txt": (project.path / "llms.txt").exists(),
            "has_llms_full_txt": (project.path / "llms-full.txt").exists(),
            "documentation_files_count": len(project.documentation_files),
            "source_files_count": len(project.source_files),
        },
        "ai_accessibility": {
            "current_score": 0,  # Will be calculated
            "max_score": 100,
            "factors": [],
        },
        "recommendations": [],
        "detailed_analysis": {} if include_detailed_analysis else None,
    }

    # Analyze documentation quality
    analysis["ai_accessibility"]["factors"].extend(await _analyze_documentation_quality(project))

    # Analyze project structure
    analysis["ai_accessibility"]["factors"].extend(_analyze_project_structure(project))

    # Analyze content organization
    analysis["ai_accessibility"]["factors"].extend(_analyze_content_organization(project))

    # Generate recommendations
    analysis["recommendations"] = await _generate_recommendations(project, analysis)

    # Calculate accessibility score
    analysis["ai_accessibility"]["current_score"] = _calculate_accessibility_score(analysis)

    # Perform detailed analysis if requested
    if include_detailed_analysis:
        analysis["detailed_analysis"] = await _perform_detailed_analysis(project)

    return analysis


async def _analyze_documentation_quality(project: "DocumentationProject") -> List[Dict[str, Any]]:
    """Analyze documentation quality factors."""
    factors = []

    # Check for comprehensive documentation
    has_comprehensive_docs = len(project.documentation_files) > 3
    factors.append(
        {
            "name": "Documentation Coverage",
            "score": 25 if has_comprehensive_docs else 10,
            "description": "Presence of comprehensive documentation files",
            "details": f"Found {len(project.documentation_files)} documentation files",
        }
    )

    # Check for README quality
    readme_files = [f for f in project.documentation_files if "readme" in f.name.lower()]
    if readme_files:
        try:
            with open(readme_files[0], "r", encoding="utf-8") as f:
                readme_content = f.read()
                has_description = len(readme_content) > 100
                has_installation = "install" in readme_content.lower()
                has_usage = "usage" in readme_content.lower() or "example" in readme_content.lower()

                readme_score = 15 if has_description else 5
                readme_score += 10 if has_installation else 0
                readme_score += 10 if has_usage else 0

                factors.append(
                    {
                        "name": "README Quality",
                        "score": readme_score,
                        "description": "Quality and completeness of README file",
                        "details": (
                            "README contains description, installation, and usage information"
                        ),
                    }
                )
        except Exception:
            factors.append(
                {
                    "name": "README Quality",
                    "score": 5,
                    "description": "README exists but could not be analyzed",
                    "details": "README file present but content analysis failed",
                }
            )
    else:
        factors.append(
            {
                "name": "README Quality",
                "score": 0,
                "description": "No README file found",
                "details": "Missing README.md file",
            }
        )

    # Check for API documentation
    has_api_docs = any("api" in f.name.lower() for f in project.documentation_files)
    factors.append(
        {
            "name": "API Documentation",
            "score": 15 if has_api_docs else 5,
            "description": "Presence of API documentation",
            "details": "API documentation files found"
            if has_api_docs
            else "Limited or no API documentation",
        }
    )

    return factors


def _analyze_project_structure(project: "DocumentationProject") -> List[Dict[str, Any]]:
    """Analyze project structure factors."""
    factors = []

    # Check for organized structure
    has_src_dir = (project.path / "src").exists()
    has_docs_dir = (project.path / "docs").exists()
    has_examples_dir = any(
        (project.path / "examples").exists()
        or any("example" in str(f.parent) for f in project.source_files)
    )

    structure_score = 0
    if has_src_dir:
        structure_score += 10
    if has_docs_dir:
        structure_score += 10
    if has_examples_dir:
        structure_score += 10

    factors.append(
        {
            "name": "Project Structure",
            "score": structure_score,
            "description": "Organization and structure of project files",
            "details": "Well-organized project structure with src/, docs/, and examples/",
        }
    )

    # Check for configuration files
    has_config = any(
        f.name in ["pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
        for f in project.path.glob("*")
        if f.is_file()
    )
    factors.append(
        {
            "name": "Configuration Management",
            "score": 10 if has_config else 2,
            "description": "Presence of configuration files",
            "details": "Project configuration files found"
            if has_config
            else "Missing configuration files",
        }
    )

    return factors


def _analyze_content_organization(project: "DocumentationProject") -> List[Dict[str, Any]]:
    """Analyze content organization factors."""
    factors = []

    # Check for proper categorization
    docs_by_type = {}
    for f in project.documentation_files:
        suffix = f.suffix.lower()
        if suffix not in docs_by_type:
            docs_by_type[suffix] = 0
        docs_by_type[suffix] += 1

    # Calculate organization score
    organization_score = 0
    if len(docs_by_type) > 1:
        organization_score += 10  # Multiple file types
    if any(count > 1 for count in docs_by_type.values()):
        organization_score += 10  # Multiple files per type

    factors.append(
        {
            "name": "Content Organization",
            "score": organization_score,
            "description": "Organization and categorization of documentation",
            "details": f"Documentation organized in {len(docs_by_type)} different formats",
        }
    )

    # Check for source code organization
    if project.source_files:
        source_score = min(15, len(project.source_files) // 10)  # Up to 15 points
        factors.append(
            {
                "name": "Source Code Organization",
                "score": source_score,
                "description": "Organization of source code files",
                "details": f"Found {len(project.source_files)} source files",
            }
        )
    else:
        factors.append(
            {
                "name": "Source Code Organization",
                "score": 0,
                "description": "No source code files found",
                "details": "Repository appears to contain only documentation",
            }
        )

    return factors


async def _generate_recommendations(
    project: "DocumentationProject", analysis: Dict[str, Any]
) -> List[str]:
    """Generate recommendations based on analysis."""
    recommendations = []

    # Basic recommendations
    if not analysis["documentation_status"]["has_llms_txt"]:
        recommendations.append("Generate llms.txt file using generate_llms_txt tool")

    if not analysis["documentation_status"]["has_readme"]:
        recommendations.append("Create a comprehensive README.md file")

    if analysis["documentation_status"]["documentation_files_count"] < 3:
        recommendations.append(
            "Add more documentation files (installation guide, API docs, examples)"
        )

    # Project-type specific recommendations
    if project.project_type == "python":
        recommendations.append("Ensure pyproject.toml or setup.py is well documented")
        recommendations.append("Add API documentation for Python modules and functions")

    elif project.project_type == "typescript":
        recommendations.append("Document package.json dependencies and scripts")
        recommendations.append("Add TypeScript interface and type documentation")

    elif project.project_type == "react":
        recommendations.append("Document React components and their props")
        recommendations.append("Add component usage examples")

    # Structure recommendations
    if not (project.path / "docs").exists():
        recommendations.append("Create a docs/ directory for organized documentation")

    if not any("example" in str(f) for f in project.documentation_files + project.source_files):
        recommendations.append("Add practical usage examples and code samples")

    # Configuration recommendations
    if project.project_type in ["python", "typescript", "rust", "go"]:
        config_files = ["pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
        missing_configs = [f for f in config_files if not (project.path / f).exists()]
        if missing_configs:
            recommendations.append(
                f"Consider adding configuration files: {', '.join(missing_configs)}"
            )

    return recommendations[:10]  # Limit recommendations


async def _perform_detailed_analysis(project: "DocumentationProject") -> Dict[str, Any]:
    """Perform detailed file-by-file analysis."""
    detailed = {
        "documentation_files": [],
        "source_files": [],
        "issues": [],
        "suggestions": [],
    }

    # Analyze documentation files
    for doc_file in project.documentation_files[:20]:  # Limit for performance
        try:
            with open(doc_file, "r", encoding="utf-8") as f:
                content = f.read()

            file_analysis = {
                "file": str(doc_file.relative_to(project.path)),
                "size": len(content),
                "lines": len(content.split("\n")),
                "has_content": len(content.strip()) > 0,
                "type": "documentation",
            }

            # Check for common documentation elements
            file_analysis["has_headers"] = content.count("#") > 0
            file_analysis["has_links"] = "[" in content and "](" in content
            file_analysis["has_code_blocks"] = "```" in content

            detailed["documentation_files"].append(file_analysis)

        except Exception as e:
            detailed["issues"].append(f"Could not analyze {doc_file}: {e}")

    # Analyze source files (sample)
    for src_file in project.source_files[:10]:  # Limit for performance
        try:
            with open(src_file, "r", encoding="utf-8") as f:
                content = f.read()

            file_analysis = {
                "file": str(src_file.relative_to(project.path)),
                "size": len(content),
                "lines": len(content.split("\n")),
                "type": "source",
            }

            # Check for documentation in source
            file_analysis["has_docstring"] = '"""' in content
            file_analysis["has_comments"] = "#" in content or "//" in content or "/*" in content

            detailed["source_files"].append(file_analysis)

        except Exception as e:
            detailed["issues"].append(f"Could not analyze {src_file}: {e}")

    return detailed


def _calculate_accessibility_score(analysis: Dict[str, Any]) -> int:
    """Calculate overall AI accessibility score."""
    total_score = sum(factor["score"] for factor in analysis["ai_accessibility"]["factors"])

    # Bonus points for llms.txt presence
    if analysis["documentation_status"]["has_llms_txt"]:
        total_score += 20

    # Bonus points for comprehensive documentation
    if analysis["documentation_status"]["documentation_files_count"] >= 5:
        total_score += 10

    # Bonus points for good project structure
    if analysis["documentation_status"]["source_files_count"] > 0:
        total_score += 5

    return min(100, total_score)


def _format_analysis_as_text(analysis: Dict[str, Any]) -> str:
    """Format analysis as plain text for Claude."""
    text = []
    text.append(f"# Repository Analysis: {analysis['project_info']['name']}")
    text.append(f"**Project Type:** {analysis['project_info']['type']}")
    text.append(f"**AI Accessibility Score:** {analysis['ai_accessibility']['current_score']}/100")
    text.append("")

    text.append("## Documentation Status")
    status = analysis["documentation_status"]
    text.append(f"- README: {'✅' if status['has_readme'] else '❌'}")
    text.append(f"- llms.txt: {'✅' if status['has_llms_txt'] else '❌'}")
    text.append(f"- llms-full.txt: {'✅' if status['has_llms_full_txt'] else '❌'}")
    text.append(f"- Documentation files: {status['documentation_files_count']}")
    text.append(f"- Source files: {status['source_files_count']}")
    text.append("")

    text.append("## AI Accessibility Factors")
    for factor in analysis["ai_accessibility"]["factors"]:
        text.append(f"- **{factor['name']}:** {factor['score']}/25 - {factor['description']}")
    text.append("")

    text.append("## Recommendations")
    for i, rec in enumerate(analysis["recommendations"], 1):
        text.append(f"{i}. {rec}")
    text.append("")

    text.append("## Next Steps")
    text.append("1. Use `generate_llms_txt` to create llms.txt if missing")
    text.append("2. Use `validate_llms_txt` to check existing documentation")
    text.append("3. Use `scan_project_structure` for detailed project analysis")
    text.append("4. Implement the recommendations above to improve AI accessibility")

    return "\n".join(text)


def _format_analysis_as_markdown(analysis: Dict[str, Any]) -> str:
    """Format analysis as markdown for Claude."""
    # Similar to text but with markdown formatting
    return _format_analysis_as_text(analysis)  # For now, reuse text formatting


__all__ = ["analyze_repo_tool"]
