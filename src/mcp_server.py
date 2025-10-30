"""MCP server implementation for Ollama search agent."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from ollama import web_fetch, web_search

from .mcp_tools import get_all_tools
from .search_agent import SearchAgent

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

logger = logging.getLogger(__name__)


class OllamaSearchMCPServer:
    """MCP Server that exposes Ollama search capabilities as MCP tools."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("ollama-search-server")
        self.agent_cache: dict[str, SearchAgent] = {}
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools.

            Returns:
                List of Tool objects describing available capabilities
            """
            tools = get_all_tools()
            return [
                Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["inputSchema"],
                )
                for tool in tools
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool execution requests.

            Args:
                name: Name of the tool to execute
                arguments: Tool arguments

            Returns:
                List of TextContent responses

            Raises:
                ValueError: If tool name is unknown
            """
            if name == "ollama_web_search":
                return await self._handle_web_search(arguments)
            elif name == "ollama_web_fetch":
                return await self._handle_web_fetch(arguments)
            elif name == "ollama_intelligent_search":
                return await self._handle_intelligent_search(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_web_search(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle web search tool calls.

        Args:
            arguments: Tool arguments containing 'query' and optional 'verbose'

        Returns:
            List with single TextContent containing search results
        """
        query = arguments.get("query", "")
        verbose = arguments.get("verbose", False)

        if verbose:
            logger.info("Executing web search: %s", query)

        try:
            result = web_search(query=query)
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.error("Web search failed: %s", str(e))
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_web_fetch(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle web fetch tool calls.

        Args:
            arguments: Tool arguments containing 'url' and optional 'verbose'

        Returns:
            List with single TextContent containing fetched content
        """
        url = arguments.get("url", "")
        verbose = arguments.get("verbose", False)

        if verbose:
            logger.info("Fetching URL: %s", url)

        try:
            result = web_fetch(url=url)
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.error("Web fetch failed: %s", str(e))
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_intelligent_search(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle intelligent search tool calls.

        Args:
            arguments: Tool arguments containing 'query', optional 'model' and 'verbose'

        Returns:
            List with single TextContent containing the search response
        """
        query = arguments.get("query", "")
        model = arguments.get("model", "mistral:7b-instruct")
        verbose = arguments.get("verbose", False)

        if verbose:
            logger.info("Executing intelligent search: %s (model: %s)", query, model)

        # Get or create agent for this model
        if model not in self.agent_cache:
            self.agent_cache[model] = SearchAgent(model=model)

        agent = self.agent_cache[model]

        try:
            # Run the search in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, agent.search, query, verbose
            )
            return [TextContent(type="text", text=response)]
        except Exception as e:
            logger.error("Intelligent search failed: %s", str(e))
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self) -> None:
        """Run the MCP server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Ollama Search MCP Server starting...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main() -> None:
    """Main entry point for the MCP server."""
    import sys

    # Handle --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Ollama Search MCP Server")
        print("\nUsage: ollama-mcp-server")
        print("\nThis is an MCP (Model Context Protocol) server that runs in stdio mode.")
        print("It is designed to be launched by MCP clients (like VS Code Chat).")
        print("\nThe server exposes 3 tools:")
        print("  - ollama_web_search: Search the web using Ollama")
        print("  - ollama_web_fetch: Fetch content from a URL")
        print("  - ollama_intelligent_search: AI-powered search combining both")
        print("\nFor testing, use:")
        print("  npx @modelcontextprotocol/inspector python3 src/mcp_server.py")
        print("\nFor integration, add to your MCP client config:")
        print('  {"command": "python3", "args": ["/path/to/src/mcp_server.py"]}')
        sys.exit(0)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    server = OllamaSearchMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
