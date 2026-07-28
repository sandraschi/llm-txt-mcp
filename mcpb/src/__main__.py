"""Main entry point for the LLM.txt MCP server with stdio support."""

import logging
import sys

from .server import LLMTextMCP
from .utils.logging import get_logger, log_with_context, setup_logging

# Set up structured logging
setup_logging(level="INFO", use_json=True, stream=sys.stderr)
logger = get_logger(__name__)

if __name__ == "__main__":
    try:
        server = LLMTextMCP()
        server.run_stdio()
    except KeyboardInterrupt:
        log_with_context(
            logger,
            logging.INFO,
            "Server stopped by user",
            context={"reason": "keyboard_interrupt"},
        )
        sys.exit(0)
    except Exception:
        logger.exception("Server error")
        sys.exit(1)
