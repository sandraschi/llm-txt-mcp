# LLM.txt MCP Server - Product Requirements Document 🎯

**Version:** 1.0  
**Date:** 2025-08-17  
**Project:** llm-txt-mcp  
**Owner:** Sandra Schipal  

## 🎯 Executive Summary

The LLM.txt MCP Server addresses the critical need for AI-readable documentation in modern development workflows. As AI coding assistants become essential tools, projects without structured documentation become invisible to these systems. This MCP server automates the generation and maintenance of llms.txt files, making any codebase instantly accessible to Claude, ChatGPT, and other LLMs.

**Core Value Proposition:** Transform any code repository into an AI-friendly documentation system with zero manual effort, enabling superior AI-assisted development experiences.

## 🚀 Problem Statement

### **Current State Pain Points**
1. **AI Assistants Struggle with HTML/CSS Noise** - Modern documentation sites are JavaScript-heavy, making them unreadable by AI systems
2. **Manual Documentation Maintenance** - Developers avoid creating and updating documentation due to time constraints
3. **Inconsistent Documentation Standards** - No standardized way to present project information to AI systems
4. **Context Window Limitations** - Large documentation sites exceed LLM context windows
5. **Vienna Development Inefficiency** - Sandra's projects lack AI-readable documentation, reducing AI assistant effectiveness

### **Target Users**
- **Primary:** Sandra Schipal and Vienna development team
- **Secondary:** AI-first developers using Claude Desktop, Cursor, and similar tools
- **Tertiary:** Open source maintainers wanting AI-accessible documentation

## 🎯 Product Vision

**"Make every code repository instantly AI-readable through automated llms.txt generation"**

Enable developers to leverage AI assistants more effectively by providing structured, AI-optimized documentation that updates automatically with code changes.

## 🔧 Core Features

### **MVP Features (v0.1.0)**

#### **1. Automated llms.txt Generation**
- **Function:** Scan project directories and generate both `llms.txt` (navigation) and `llms-full.txt` (complete content)
- **Input:** Project directory path
- **Output:** Standardized llms.txt files following official specification
- **Intelligence:** 
  - Project type detection (Python, TypeScript, React, FastAPI, etc.)
  - Smart file prioritization (README, API docs, examples)
  - Content extraction from existing documentation

#### **2. MCP Server Integration**
- **Function:** Expose functionality through FastMCP 2.10+ protocol
- **Integration:** Direct Claude Desktop integration via MCP configuration
- **Tools Provided:**
  - `generate_llms_txt` - Main generation function
  - `validate_llms_txt` - Format validation
  - `scan_project_structure` - Analysis and recommendations
  - `convert_to_context` - XML/JSON output for LLMs

#### **3. Project Type Intelligence**
- **Function:** Automatically detect project characteristics and generate appropriate documentation structure
- **Supported Types:**
  - Python (pyproject.toml, setup.py detection)
  - TypeScript/JavaScript (package.json, tsconfig.json)
  - React (component detection)
  - FastAPI (API endpoint discovery)
  - Generic fallback for any project

#### **4. Template System**
- **Function:** Pre-built templates for common project types
- **Templates:**
  - Generic - Basic docs/examples/optional structure
  - Python - API/configuration/deployment sections
  - React - Components/hooks/styling sections
  - FastAPI - Models/endpoints/deployment sections

#### **5. Content Validation**
- **Function:** Ensure generated llms.txt files comply with specification
- **Validation Rules:**
  - H1 header with project name
  - Blockquote summary section
  - H2-delimited sections
  - Valid markdown link format
  - Appropriate section ordering

### **Advanced Features (v0.2.0+)**

#### **6. Git Integration**
- **Function:** Detect file changes and automatically update documentation
- **Capabilities:**
  - Hook into git commits
  - Incremental updates for changed files only
  - Preserve manual customizations

#### **7. CI/CD Pipeline Integration**
- **Function:** Automated documentation generation in build processes
- **Outputs:**
  - GitHub Actions workflow
  - Pre-commit hooks
  - Build step integration

#### **8. Batch Processing**
- **Function:** Process multiple projects simultaneously
- **Use Case:** Organization-wide documentation standardization

## 🏗️ Technical Architecture

### **Core Components**

#### **1. LLMTextService**
- **Responsibility:** Main business logic and orchestration
- **Key Methods:**
  - `generate_project_llms_txt()` - Main generation workflow
  - `validate_llms_txt()` - Format validation
  - `update_llms_txt()` - Incremental updates
  - `scan_project_structure()` - Project analysis

#### **2. DocumentationProject**
- **Responsibility:** Project structure analysis and file discovery
- **Key Features:**
  - Project type detection
  - File categorization (docs, source, config)
  - Git repository integration
  - Smart content prioritization

#### **3. LLMTextGenerator**
- **Responsibility:** Content generation and formatting
- **Key Features:**
  - Template-based generation
  - Content extraction from existing files
  - Format validation and standardization
  - Multi-format output (Markdown, XML, JSON)

#### **4. FastMCP Server**
- **Responsibility:** MCP protocol implementation
- **Integration:** Claude Desktop, other MCP-compatible tools
- **Error Handling:** Comprehensive error reporting and recovery

### **Technology Stack**
- **Framework:** FastMCP 2.10.1+
- **Language:** Python 3.9+
- **Dependencies:**
  - `aiofiles` - Async file operations
  - `gitpython` - Git repository integration
  - `pathspec` - File pattern matching
  - `markdown` - Content processing
  - `pyyaml` - Configuration handling

### **Performance Requirements**
- **Generation Time:** < 5 seconds for typical project (1000 files)
- **Memory Usage:** < 100MB for large projects (10,000 files)
- **Concurrency:** Support multiple simultaneous requests
- **Reliability:** 99.9% success rate for valid project directories

## 🎯 User Experience

### **Primary Workflow (Claude Desktop Integration)**

1. **Setup:** Add llm-txt-mcp to Claude Desktop configuration
2. **Discovery:** Use `scan_project_structure` to analyze project
3. **Generation:** Use `generate_llms_txt` to create documentation
4. **Validation:** Use `validate_llms_txt` to ensure quality
5. **Consumption:** AI assistants automatically use generated llms.txt files

### **Command-Line Interface**
```bash
# Generate for current directory
llm-txt-mcp generate .

# Scan project structure
llm-txt-mcp scan D:/Dev/repos/ednaficator

# Validate existing file
llm-txt-mcp validate ./llms.txt

# Convert to XML context
llm-txt-mcp convert ./llms.txt --format xml
```

### **Error Handling**
- **Graceful Degradation:** Generate partial documentation if some files are inaccessible
- **Clear Error Messages:** Specific guidance for common issues
- **Recovery Suggestions:** Actionable steps to resolve problems

## 📊 Success Metrics

### **Adoption Metrics**
- **Primary:** Daily usage by Sandra's Vienna development projects
- **Secondary:** Generation success rate > 95%
- **Tertiary:** Integration with all major MCP-compatible tools

### **Quality Metrics**
- **Documentation Coverage:** > 80% of project files documented
- **AI Comprehension:** Successful AI assistant interactions using generated docs
- **Maintenance Overhead:** < 5 minutes per project per month

### **Performance Metrics**
- **Generation Speed:** Average < 3 seconds per project
- **File Size Efficiency:** llms.txt < 50KB, llms-full.txt < 500KB
- **Update Frequency:** Automated updates within 1 hour of code changes

## 🔄 Development Phases

### **Phase 1: MVP (2 days)**
- [x] Core project structure and FastMCP integration
- [x] Basic generation for Python/TypeScript projects
- [x] Essential MCP tools implementation
- [x] Claude Desktop integration testing

### **Phase 2: Enhancement (3 days)**
- [ ] Template system for all project types
- [ ] Advanced content extraction
- [ ] Comprehensive validation
- [ ] Error handling and recovery

### **Phase 3: Integration (2 days)**
- [ ] Git integration for change detection
- [ ] CI/CD pipeline components
- [ ] Batch processing capabilities
- [ ] Performance optimization

### **Phase 4: Polish (1 day)**
- [ ] Documentation and examples
- [ ] DXT packaging
- [ ] GitHub repository setup
- [ ] Community preparation

## 🎯 Vienna Development Integration

### **Immediate Projects**
1. **Ednaficator** - AI concierge system documentation
2. **FastSearch MCP** - Search functionality documentation  
3. **VirtualBox MCP** - VM management documentation
4. **Local LLM MCP** - Local model integration documentation

### **Workflow Integration**
- **Pre-commit Hook:** Automatically update llms.txt on commits
- **Claude Desktop:** Instant access to project documentation
- **Cursor IDE:** Enhanced AI assistance with proper context
- **Development Efficiency:** Reduce context-switching time by 50%

## 🔮 Future Roadmap

### **v0.3.0 - Advanced Intelligence**
- AI-powered content analysis and optimization
- Multi-language documentation support  
- Advanced template customization
- Integration with documentation platforms (Mintlify, GitBook)

### **v0.4.0 - Enterprise Features**
- Organization-wide documentation standards
- Access control and permissions
- Analytics and usage reporting
- API endpoint integration

### **v1.0.0 - Production Ready**
- Commercial-grade reliability and performance
- Enterprise support and SLA
- Advanced customization options
- Comprehensive integration ecosystem

## ⚠️ Risks and Mitigation

### **Technical Risks**
- **Large File Handling:** Implement streaming and chunking
- **File Format Diversity:** Robust parsing with fallback options
- **Performance Scaling:** Async processing and caching

### **Adoption Risks**
- **Learning Curve:** Comprehensive documentation and examples
- **Integration Complexity:** Simple setup processes and templates
- **Maintenance Overhead:** Automated updates and minimal configuration

### **Business Risks**
- **llms.txt Standard Evolution:** Flexible architecture for specification changes
- **Competing Solutions:** Focus on Austrian efficiency and unique Vienna use cases
- **AI Tool Integration Changes:** Modular design for easy adaptation

## 🎯 Success Definition

**Primary Success:** Sandra's Vienna development team achieves 50% improvement in AI assistant effectiveness across all projects within 30 days of deployment.

**Secondary Success:** LLM.txt MCP Server becomes the standard documentation automation tool for Vienna development workflows, with 100% project coverage.

**Tertiary Success:** Open source adoption and community contribution, establishing Vienna as a leader in AI-first development practices.

---

**Next Steps:** Begin Phase 1 implementation with focus on MVP features and Claude Desktop integration testing.
