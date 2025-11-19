"""Main entry point for the LLM.txt MCP server with stdio support."""

import logging
import sys

from .server import LLMTextMCP

# Configure logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        server = LLMTextMCP()
        server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
