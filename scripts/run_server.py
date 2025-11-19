#!/usr/bin/env python3
"""
Script to run the LLM.txt MCP server with various options.

This script provides a convenient way to start the MCP server with different
transport modes (stdio for Claude Desktop or HTTP for testing).
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_txt_mcp.server import LLMTextMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        logger.info(f"Starting LLM.txt MCP server (log level: {args.log_level})")
        server = LLMTextMCP()

        if args.stdio:
            logger.info("Running with stdio transport for Claude Desktop")
            server.run_stdio()
        else:
            logger.info(f"Running HTTP server on {args.host}:{args.port}")
            server.run_http(host=args.host, port=args.port)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
