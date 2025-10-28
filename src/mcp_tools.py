"""MCP tool schema definitions for Ollama search agent."""

from typing import Any

# Tool schema for web search
WEB_SEARCH_TOOL = {
    "name": "ollama_web_search",
    "description": (
        "Search the web using Ollama's web search capability. "
        "Returns relevant web search results for the given query."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute",
            },
            "verbose": {
                "type": "boolean",
                "description": "Whether to show intermediate search steps",
                "default": False,
            },
        },
        "required": ["query"],
    },
}

# Tool schema for fetching web content
WEB_FETCH_TOOL = {
    "name": "ollama_web_fetch",
    "description": (
        "Fetch and read content from a specific URL using Ollama's web fetch capability. "
        "Returns the text content of the webpage."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch content from",
            },
            "verbose": {
                "type": "boolean",
                "description": "Whether to show intermediate fetch steps",
                "default": False,
            },
        },
        "required": ["url"],
    },
}

# Tool schema for intelligent search with conversation
INTELLIGENT_SEARCH_TOOL = {
    "name": "ollama_intelligent_search",
    "description": (
        "Perform an intelligent web search that can use multiple tools (search and fetch) "
        "to answer complex questions about online documentation and web content. "
        "The agent will automatically decide when to search and when to fetch content."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or search query to answer",
            },
            "model": {
                "type": "string",
                "description": "The Ollama model to use (default: mistral:7b-instruct)",
                "default": "mistral:7b-instruct",
            },
            "verbose": {
                "type": "boolean",
                "description": "Whether to show intermediate processing steps",
                "default": False,
            },
        },
        "required": ["query"],
    },
}


def get_all_tools() -> list[dict[str, Any]]:
    """Get all available MCP tools.

    Returns:
        List of tool schema dictionaries
    """
    return [
        WEB_SEARCH_TOOL,
        WEB_FETCH_TOOL,
        INTELLIGENT_SEARCH_TOOL,
    ]
