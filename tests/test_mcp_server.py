"""Tests for the MCP server implementation."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path so we can import src as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import OllamaSearchMCPServer
from src.mcp_tools import get_all_tools


def test_get_all_tools():
    """Test that all tools are returned correctly."""
    tools = get_all_tools()
    assert len(tools) == 3
    tool_names = [tool["name"] for tool in tools]
    assert "ollama_web_search" in tool_names
    assert "ollama_web_fetch" in tool_names
    assert "ollama_intelligent_search" in tool_names


def test_tool_schemas():
    """Test that tool schemas have required fields."""
    tools = get_all_tools()
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert "type" in tool["inputSchema"]
        assert "properties" in tool["inputSchema"]
        assert "required" in tool["inputSchema"]


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """Test MCP server initialization."""
    server = OllamaSearchMCPServer()
    assert server.server is not None
    assert server.agent_cache == {}


@pytest.mark.asyncio
@patch("src.mcp_server.web_search")
async def test_handle_web_search(mock_web_search):
    """Test web search handler."""
    mock_web_search.return_value = "Search results"
    server = OllamaSearchMCPServer()

    result = await server._handle_web_search({"query": "test query"})

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Search results" in result[0].text
    mock_web_search.assert_called_once_with(query="test query")


@pytest.mark.asyncio
@patch("src.mcp_server.web_fetch")
async def test_handle_web_fetch(mock_web_fetch):
    """Test web fetch handler."""
    mock_web_fetch.return_value = "Page content"
    server = OllamaSearchMCPServer()

    result = await server._handle_web_fetch({"url": "https://example.com"})

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Page content" in result[0].text
    mock_web_fetch.assert_called_once_with(url="https://example.com")


@pytest.mark.asyncio
@patch("src.mcp_server.SearchAgent")
async def test_handle_intelligent_search(mock_agent_class):
    """Test intelligent search handler."""
    mock_agent = MagicMock()
    mock_agent.search.return_value = "Intelligent response"
    mock_agent_class.return_value = mock_agent

    server = OllamaSearchMCPServer()

    result = await server._handle_intelligent_search({"query": "test query"})

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Intelligent response" in result[0].text


@pytest.mark.asyncio
async def test_handle_web_search_error():
    """Test web search error handling."""
    with patch("src.mcp_server.web_search", side_effect=Exception("Search failed")):
        server = OllamaSearchMCPServer()
        result = await server._handle_web_search({"query": "test"})

        assert len(result) == 1
        assert "Error:" in result[0].text
        assert "Search failed" in result[0].text


@pytest.mark.asyncio
async def test_agent_caching():
    """Test that agents are cached per model."""
    with patch("src.mcp_server.SearchAgent") as mock_agent_class:
        mock_agent = MagicMock()
        mock_agent.search.return_value = "Response"
        mock_agent_class.return_value = mock_agent

        server = OllamaSearchMCPServer()

        await server._handle_intelligent_search(
            {"query": "test1", "model": "model1"}
        )
        await server._handle_intelligent_search(
            {"query": "test2", "model": "model1"}
        )
        await server._handle_intelligent_search(
            {"query": "test3", "model": "model2"}
        )

        assert len(server.agent_cache) == 2
        assert "model1" in server.agent_cache
        assert "model2" in server.agent_cache
        assert mock_agent_class.call_count == 2
