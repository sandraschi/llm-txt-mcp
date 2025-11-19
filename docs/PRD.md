# Product Requirements Document (PRD)
# LLM.txt MCP Server

**Version:** 1.0  
**Last Updated:** 2025-11-19  
**Author:** Sandra Schipal  
**Status:** Active Development

---

## Executive Summary

The LLM.txt MCP Server is a Model Context Protocol (MCP) server that automates the generation, validation, and management of `llms.txt` documentation files. It makes project documentation AI-accessible by providing structured, standardized documentation indices that Large Language Models can efficiently consume.

### Vision
Enable every software project to be instantly understandable by AI systems through automated, standardized documentation generation.

### Mission
Provide developers with effortless tools to make their projects AI-accessible, reducing the barrier to AI-assisted development and documentation.

---

## Problem Statement

### Current Challenges
1. **Manual Documentation Burden**: Developers spend significant time creating and maintaining documentation indices for AI consumption
2. **Inconsistent Formats**: Lack of standardization makes it difficult for AI systems to reliably parse project documentation
3. **Documentation Drift**: Documentation quickly becomes outdated as projects evolve
4. **Discovery Difficulty**: AI systems struggle to locate relevant documentation within complex project structures
5. **Context Limitations**: LLMs have token limits, requiring efficient documentation summarization

### Target Users
- **Primary**: Software developers using AI coding assistants (Claude, GPT-4, etc.)
- **Secondary**: Technical writers, DevOps engineers, open-source maintainers
- **Tertiary**: AI researchers working with code understanding systems

---

## Product Goals

### Primary Goals
1. **Automation**: Generate comprehensive `llms.txt` files with minimal manual intervention
2. **Accuracy**: Intelligently categorize and prioritize documentation based on project type
3. **Maintainability**: Enable easy updates while preserving custom content
4. **Integration**: Seamless integration with Claude Desktop and other MCP clients
5. **Flexibility**: Support multiple project types, languages, and documentation structures

### Success Metrics
- **Adoption**: 1000+ active installations within 6 months
- **Quality**: 95%+ accuracy in documentation categorization
- **Performance**: Generate llms.txt for typical projects in <5 seconds
- **User Satisfaction**: 4.5+ star rating on feedback surveys
- **Coverage**: Support for 10+ major programming languages/frameworks

---

## Features & Requirements

### Core Features (MVP)

#### 1. Automated Generation
**Priority:** P0 (Critical)

**Description:** Scan project directories and automatically generate structured `llms.txt` files.

**Requirements:**
- Detect project type from configuration files (pyproject.toml, package.json, etc.)
- Discover and categorize documentation files (README, API docs, examples)
- Generate structured output following llms.txt specification
- Create both `llms.txt` (index) and `llms-full.txt` (full content)
- Support configurable scan depth (default: 3 levels)

**Acceptance Criteria:**
- Successfully generates llms.txt for Python, TypeScript, React, Rust, and Go projects
- Categorizes files into appropriate sections (docs, api, examples, config, optional)
- Completes generation in <5 seconds for projects with <1000 files
- Handles edge cases (empty projects, missing README, etc.)

#### 2. Validation & Quality Checks
**Priority:** P0 (Critical)

**Description:** Validate existing `llms.txt` files for format compliance and completeness.

**Requirements:**
- Check for required H1 header with project name
- Verify blockquote summary presence
- Validate H2 section structure
- Check for proper markdown link formatting
- Provide actionable warnings and suggestions

**Acceptance Criteria:**
- Identifies all format violations per llms.txt spec
- Provides clear, actionable error messages
- Suggests improvements for incomplete documentation
- Returns validation score (0-100)

#### 3. Smart Update Mechanism
**Priority:** P0 (Critical)

**Description:** Update existing `llms.txt` files while preserving custom user additions.

**Requirements:**
- Parse existing llms.txt structure
- Identify custom vs. auto-generated content
- Merge new discoveries with existing content
- Support selective section regeneration
- Track and report changes made

**Acceptance Criteria:**
- Preserves manually added links and sections
- Updates outdated file references
- Adds newly discovered documentation
- Provides diff summary of changes

#### 4. MCP Integration
**Priority:** P0 (Critical)

**Description:** Full integration with Model Context Protocol for Claude Desktop and compatible clients.

**Requirements:**
- Stdio transport support for Claude Desktop
- HTTP transport for development/testing
- Proper tool registration and metadata
- Structured error handling and responses
- Health check and status endpoints

**Acceptance Criteria:**
- Loads successfully in Claude Desktop
- All tools accessible via MCP interface
- Proper error messages returned to client
- <100ms response time for health checks

### Enhanced Features (Post-MVP)

#### 5. Template System
**Priority:** P1 (High)

**Description:** Pre-built templates for common project types with customization options.

**Requirements:**
- Templates for Python, TypeScript, React, FastAPI, Rust, Go
- Custom section support
- Template inheritance and composition
- User-defined template creation

#### 6. Context Conversion
**Priority:** P1 (High)

**Description:** Convert `llms.txt` to optimized formats for LLM consumption.

**Requirements:**
- XML output format
- JSON output format
- Optional section filtering
- Token-optimized output

#### 7. Repository Analysis
**Priority:** P2 (Medium)

**Description:** Comprehensive analysis of repository AI accessibility with recommendations.

**Requirements:**
- AI accessibility scoring (0-100)
- Detailed recommendations by category
- File-by-file analysis option
- Multiple output formats (text, JSON, markdown)

#### 8. Git Integration
**Priority:** P2 (Medium)

**Description:** Leverage git repository information for enhanced analysis.

**Requirements:**
- Detect git repository status
- Use .gitignore for file filtering
- Extract project metadata from git config
- Track documentation changes over time

---

## Technical Architecture

### Technology Stack
- **Language:** Python 3.10+
- **Framework:** FastMCP 2.12.0+
- **Protocol:** Model Context Protocol (MCP)
- **Transport:** Stdio (primary), HTTP (development)
- **Code Quality:** Ruff 0.14.5, MyPy 1.0+
- **Testing:** Pytest 7.0+, pytest-asyncio

### System Components

#### 1. Core Service Layer
- **LLMTextService**: Main service orchestrator
- **DocumentationProject**: Project model and metadata
- **LLMTextGenerator**: Content generation engine

#### 2. Tool Layer
- **Generation Tools**: generate_llms_txt, update_llms_txt, generate_from_template
- **Validation Tools**: validate_llms_txt
- **Analysis Tools**: scan_project_structure, analyze_repo
- **Conversion Tools**: convert_to_context
- **Utility Tools**: help, status, health_check

#### 3. Utility Layer
- **File Discovery**: Smart file categorization and prioritization
- **Template Engine**: Template loading and rendering
- **Parser**: llms.txt format parsing
- **Validator**: Format and content validation

### Data Flow
```
User Request (MCP Client)
    ↓
FastMCP Server (stdio/HTTP)
    ↓
Tool Router
    ↓
Service Layer (LLMTextService)
    ↓
Generator/Validator/Analyzer
    ↓
File System Operations
    ↓
Response (structured JSON)
    ↓
MCP Client
```

---

## User Experience

### Primary Use Cases

#### Use Case 1: First-Time Setup
**Actor:** Developer setting up AI accessibility for a new project

**Flow:**
1. Install llm-txt-mcp via pip
2. Configure in Claude Desktop config
3. Restart Claude Desktop
4. Use `generate_llms_txt(project_path="/path/to/project")`
5. Review generated llms.txt
6. Commit to repository

**Expected Outcome:** Complete, accurate llms.txt generated in <30 seconds

#### Use Case 2: Documentation Update
**Actor:** Developer updating project after adding new features

**Flow:**
1. Add new documentation files
2. Use `update_llms_txt(project_path="/path/to/project")`
3. Review changes summary
4. Verify custom content preserved
5. Commit updated llms.txt

**Expected Outcome:** Updated llms.txt with new content, custom sections preserved

#### Use Case 3: Quality Audit
**Actor:** Technical writer auditing documentation quality

**Flow:**
1. Use `validate_llms_txt(file_path="/path/to/llms.txt")`
2. Review validation report
3. Address errors and warnings
4. Use `analyze_repo()` for comprehensive analysis
5. Implement recommendations

**Expected Outcome:** Clear action items for improving AI accessibility

---

## Non-Functional Requirements

### Performance
- **Generation Speed:** <5 seconds for projects with <1000 files
- **Validation Speed:** <1 second for typical llms.txt files
- **Memory Usage:** <100MB for typical operations
- **Startup Time:** <2 seconds for MCP server initialization

### Reliability
- **Uptime:** 99.9% availability for MCP server
- **Error Handling:** Graceful degradation, no crashes
- **Data Integrity:** No data loss during updates
- **Backward Compatibility:** Support llms.txt spec v1.0+

### Security
- **File Access:** Respect file permissions and .gitignore
- **Path Traversal:** Prevent directory traversal attacks
- **Input Validation:** Sanitize all user inputs
- **No External Calls:** No network requests without explicit user consent

### Usability
- **Documentation:** Comprehensive README and inline help
- **Error Messages:** Clear, actionable error descriptions
- **Defaults:** Sensible defaults requiring minimal configuration
- **Discoverability:** Self-documenting via `help` tool

---

## Development Roadmap

### Phase 1: MVP (Completed)
- ✅ Core generation engine
- ✅ MCP server implementation
- ✅ Basic validation
- ✅ Claude Desktop integration
- ✅ Python 3.10+ support
- ✅ Ruff integration

### Phase 2: Enhancement (Current)
- 🔄 Comprehensive testing suite
- 🔄 Template system
- 🔄 Repository analysis
- 🔄 Documentation improvements
- 🔄 Type safety improvements (MyPy)

### Phase 3: Advanced Features (Planned)
- ⏳ Multi-language support (beyond English)
- ⏳ Custom plugin system
- ⏳ CI/CD integration
- ⏳ Web UI for configuration
- ⏳ Analytics and usage tracking

### Phase 4: Ecosystem (Future)
- ⏳ IDE extensions (VS Code, JetBrains)
- ⏳ GitHub Action
- ⏳ Pre-commit hooks
- ⏳ Community template marketplace

---

## Success Criteria

### Launch Criteria
- [ ] All P0 features implemented and tested
- [ ] Documentation complete (README, API docs, examples)
- [ ] Test coverage >80%
- [ ] Zero critical bugs
- [ ] Claude Desktop integration verified
- [ ] Performance benchmarks met

### Post-Launch Metrics (3 months)
- 500+ GitHub stars
- 100+ active installations
- <10 open critical bugs
- 90%+ positive user feedback
- 5+ community contributions

---

## Risks & Mitigation

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MCP spec changes | High | Medium | Monitor spec, maintain compatibility layer |
| Performance degradation on large repos | Medium | High | Implement caching, configurable limits |
| File encoding issues | Medium | Medium | Robust encoding detection, fallbacks |
| Type checking overhead | Low | Low | Gradual MyPy adoption, pragmatic approach |

### Business Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low adoption | High | Medium | Active marketing, documentation, examples |
| Competing solutions | Medium | High | Focus on quality, MCP integration advantage |
| Maintenance burden | Medium | Medium | Community engagement, clear contribution guidelines |

---

## Appendix

### References
- [llms.txt Specification](https://llms-txt.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

### Glossary
- **MCP**: Model Context Protocol - Standard for AI tool integration
- **llms.txt**: Standardized documentation index file for AI systems
- **Stdio**: Standard input/output transport mechanism
- **FastMCP**: Python framework for building MCP servers

---

**Document Control**
- **Version History:**
  - v1.0 (2025-11-19): Initial PRD creation
- **Approvals:** Sandra Schipal (Author/Owner)
- **Next Review:** 2025-12-19


