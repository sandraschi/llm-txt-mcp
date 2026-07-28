# llm-txt-mcp (MCPB Bundle)

MCP server for generating and managing llms.txt documentation files

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "llm-txt-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "llm_txt_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **generate_llms_txt**: generate_llms_txt

## Requirements

- Python 3.12+
- uv
