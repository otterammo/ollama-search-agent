"""MCP tool schema definitions for Ollama search agent."""

from typing import Any

# Tool schema for web search
WEB_SEARCH_TOOL = {
    "name": "ollama_web_search",
    "description": (
        "Search the web using Ollama's web search capability. "
        "Returns a list of search results with URLs, titles, and snippets. "
        "Use this to find relevant sources, then analyze the results to answer the user's question. "
        "For automatically synthesized answers, use ollama_intelligent_search instead."
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
        "Perform an AI-powered web search that automatically finds, fetches, and synthesizes "
        "information from the web to answer questions. This tool uses an AI agent that can "
        "search multiple sources, fetch page content, and provide comprehensive answers. "
        "Recommended for questions requiring real-time information, current events, polls, "
        "news, documentation, or any web-based research. Automatically detects the maximum "
        "working context window for each model (typically 16K-32K tokens)."
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
            "num_ctx": {
                "type": "integer",
                "description": (
                    "Context window size in tokens. If omitted, automatically detects the maximum "
                    "working context for the model by testing in descending order: 32K, 16K, 8K, 4K"
                ),
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
