#!/usr/bin/env python3
"""
Script to run the LLM.txt MCP server with various options.

This script provides a convenient way to start the MCP server with different
transport modes (stdio for Claude Desktop or HTTP for testing).
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_txt_mcp.server import LLMTextMCP
from llm_txt_mcp.utils.logging import get_logger, setup_logging

# Configure structured logging
setup_logging(level="INFO", use_json=True, stream=sys.stderr)
logger = get_logger(__name__)


def main():
    """Main entry point for the server script."""
    parser = argparse.ArgumentParser(
        description="LLM.txt MCP Server Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio for Claude Desktop
  python scripts/run_server.py --stdio

  # Run HTTP server for testing
  python scripts/run_server.py --host 127.0.0.1 --port 8000

  # Run with debug logging
  python scripts/run_server.py --stdio --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--stdio", action="store_true", help="Run with stdio transport for Claude Desktop"
    )

    parser.add_argument(
        "--host", default="localhost", help="Host for HTTP server (default: localhost)"
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="Port for HTTP server (default: 8000)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Reconfigure logging with requested level
    setup_logging(level=args.log_level, use_json=True, stream=sys.stderr)

    try:
        import logging as log_module

        from llm_txt_mcp.utils.logging import log_with_context

        log_with_context(
            logger,
            log_module.INFO,
            "Starting LLM.txt MCP server",
            context={"log_level": args.log_level},
        )
        server = LLMTextMCP()

        if args.stdio:
            log_with_context(
                logger,
                log_module.INFO,
                "Running with stdio transport for Claude Desktop",
                context={"transport": "stdio"},
            )
            server.run_stdio()
        else:
            log_with_context(
                logger,
                log_module.INFO,
                "Running HTTP server",
                context={"transport": "http", "host": args.host, "port": args.port},
            )
            server.run_http(host=args.host, port=args.port)

    except KeyboardInterrupt:
        log_with_context(
            logger,
            log_module.INFO,
            "Server stopped by user",
            context={"reason": "keyboard_interrupt"},
        )
        sys.exit(0)
    except Exception:
        logger.exception("Server error", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
