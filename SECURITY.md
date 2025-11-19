# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of LLM.txt MCP Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email**: sandra@sandraschi.dev
- **Subject**: [SECURITY] LLM.txt MCP Vulnerability Report

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., XSS, SQL injection, path traversal, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

### What to Expect

After you submit a report, we will:

1. Confirm receipt of your vulnerability report
2. Investigate and validate the vulnerability
3. Determine the severity and impact
4. Develop and test a fix
5. Release a security patch
6. Publicly disclose the vulnerability (with credit to you, if desired)

### Security Best Practices

When using LLM.txt MCP Server:

1. **File System Access**: The server respects `.gitignore` and file permissions
2. **Path Traversal**: All file paths are validated and sanitized
3. **Input Validation**: All user inputs are validated using Pydantic models
4. **Dependencies**: Keep dependencies up to date
5. **Environment Variables**: Use environment variables for sensitive configuration
6. **Permissions**: Run with minimal required permissions

### Known Security Considerations

- **File Access**: The server can read files in the project directory
- **Git Integration**: Requires git repository access if enabled
- **External Tools**: May execute external commands (git)

### Security Updates

Security updates will be released as patch versions (e.g., 0.1.1) and announced via:
- GitHub Security Advisories
- GitHub Releases
- Repository README

### Disclosure Policy

We follow coordinated vulnerability disclosure:
- We will work with you to understand and resolve the issue
- We will credit you for the discovery (unless you prefer to remain anonymous)
- We will publicly disclose the vulnerability after a fix is released

## Security Hall of Fame

We appreciate the security researchers who help keep LLM.txt MCP Server safe:

<!-- Contributors will be listed here -->

---

**Last Updated**: 2025-11-19  
**Contact**: sandra@sandraschi.dev
