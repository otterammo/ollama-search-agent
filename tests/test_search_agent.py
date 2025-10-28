"""Tests for the SearchAgent class."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from search_agent import SearchAgent


@pytest.fixture
def mock_chat_response():
    """Create a mock chat response."""
    mock_response = MagicMock()
    mock_response.message.content = "Test response"
    mock_response.message.thinking = None
    mock_response.message.tool_calls = None
    return mock_response


@pytest.fixture
def mock_chat_with_tools():
    """Create a mock chat response with tool calls."""
    mock_response = MagicMock()
    mock_response.message.content = None
    mock_response.message.thinking = "I need to search"
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "web_search"
    mock_tool_call.function.arguments = {"query": "test"}
    mock_response.message.tool_calls = [mock_tool_call]
    return mock_response


@pytest.fixture
def mock_final_response():
    """Create a mock final response after tool use."""
    mock_response = MagicMock()
    mock_response.message.content = "Final answer based on search"
    mock_response.message.thinking = None
    mock_response.message.tool_calls = None
    return mock_response


def test_search_agent_initialization():
    """Test SearchAgent initialization with default parameters."""
    agent = SearchAgent()
    assert agent.model == "mistral:7b-instruct"
    assert agent.max_result_length == 8000
    assert agent.enable_thinking is False
    assert "web_search" in agent.available_tools
    assert "web_fetch" in agent.available_tools


def test_search_agent_custom_parameters():
    """Test SearchAgent initialization with custom parameters."""
    agent = SearchAgent(
        model="llama2:7b",
        max_result_length=4000,
        enable_thinking=False,
    )
    assert agent.model == "llama2:7b"
    assert agent.max_result_length == 4000
    assert agent.enable_thinking is False


@patch("search_agent.chat")
def test_search_simple_query(mock_chat, mock_chat_response):
    """Test a simple search query without tool calls."""
    mock_chat.return_value = mock_chat_response
    agent = SearchAgent()
    response = agent.search("test query", verbose=False)
    assert response == "Test response"
    mock_chat.assert_called_once()


@patch("search_agent.chat")
@patch("search_agent.web_search")
def test_search_with_tool_call(
    mock_web_search, mock_chat, mock_chat_with_tools, mock_final_response
):
    """Test a search query that uses web_search tool."""
    mock_web_search.return_value = "Search results"
    mock_chat.side_effect = [mock_chat_with_tools, mock_final_response]

    agent = SearchAgent()
    response = agent.search("test query", verbose=False)

    assert response == "Final answer based on search"
    assert mock_chat.call_count == 2
    mock_web_search.assert_called_once_with(query="test")


@patch("search_agent.chat")
def test_search_with_history(mock_chat, mock_chat_response):
    """Test search with existing conversation history."""
    mock_chat.return_value = mock_chat_response
    agent = SearchAgent()

    history = [
        {"role": "user", "content": "previous query"},
        {"role": "assistant", "content": "previous response"},
    ]

    response, updated_history = agent.search_with_history(
        "new query", history, verbose=False
    )

    assert response == "Test response"
    assert len(updated_history) > len(history)
    assert updated_history[0] == history[0]
    assert updated_history[1] == history[1]


@patch("search_agent.chat")
def test_search_with_invalid_tool(mock_chat):
    """Test handling of invalid tool calls."""
    mock_response = MagicMock()
    mock_response.message.content = None
    mock_response.message.thinking = None
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "invalid_tool"
    mock_tool_call.function.arguments = {}
    mock_response.message.tool_calls = [mock_tool_call]

    mock_final = MagicMock()
    mock_final.message.content = "Error handled"
    mock_final.message.thinking = None
    mock_final.message.tool_calls = None

    mock_chat.side_effect = [mock_response, mock_final]

    agent = SearchAgent()
    response = agent.search("test query", verbose=False)

    assert response == "Error handled"
