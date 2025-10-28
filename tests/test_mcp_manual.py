#!/usr/bin/env python3
"""Test script to verify MCP server functionality."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import src as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import OllamaSearchMCPServer


async def test_list_tools():
    """Test that tools can be listed."""
    print("Testing tool listing...")

    # Verify tools are defined in the schema
    from src.mcp_tools import get_all_tools

    tool_schemas = get_all_tools()
    print(f"✓ Found {len(tool_schemas)} tools defined:")
    for tool in tool_schemas:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")

    # Verify server can be created
    server = OllamaSearchMCPServer()
    print("✓ MCP Server initialized successfully")
    print(f"✓ Server name: {server.server.name}")

    return tool_schemas


async def test_web_search():
    """Test web search functionality."""
    print("\nTesting web search...")
    server = OllamaSearchMCPServer()

    try:
        result = await server._handle_web_search(
            {"query": "ollama web search", "verbose": True}
        )
        print("✓ Web search executed successfully")
        print(f"  Result preview: {result[0].text[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Web search failed: {e}")
        return False


async def test_web_fetch():
    """Test web fetch functionality."""
    print("\nTesting web fetch...")
    server = OllamaSearchMCPServer()

    try:
        result = await server._handle_web_fetch(
            {"url": "https://ollama.com", "verbose": True}
        )
        print("✓ Web fetch executed successfully")
        print(f"  Result preview: {result[0].text[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Web fetch failed: {e}")
        return False


async def test_intelligent_search():
    """Test intelligent search functionality."""
    print("\nTesting intelligent search...")
    server = OllamaSearchMCPServer()

    try:
        result = await server._handle_intelligent_search(
            {
                "query": "What is Ollama?",
                "model": "mistral:7b-instruct",
                "verbose": False,
            }
        )
        print("✓ Intelligent search executed successfully")
        print(f"  Result preview: {result[0].text[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Intelligent search failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Server Functionality Tests")
    print("=" * 60)

    tools = await test_list_tools()

    print("\nNote: Skipping integration tests (web_search, web_fetch, intelligent_search)")
    print("These require Ollama to be running and can be slow.")
    print("Run them individually if needed for full verification.")

    # Uncomment to run full integration tests (requires Ollama running):
    # await test_web_search()
    # await test_web_fetch()
    # await test_intelligent_search()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)
    print(f"\nThe MCP server exposes {len(tools)} tools for MCP clients.")
    print("Use 'make run-mcp' to start the server for MCP client connections.")


if __name__ == "__main__":
    asyncio.run(main())
