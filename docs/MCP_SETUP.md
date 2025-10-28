# MCP Server Setup Guide

## What is MCP?

Model Context Protocol (MCP) is a protocol that allows AI assistants (like Claude Desktop) to use external tools and data sources. This project implements an MCP server that exposes Ollama's web search and fetch capabilities.

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Verify installation:
```bash
python3 tests/test_mcp_manual.py
```

## Running the MCP Server

### Standalone Mode
```bash
make run-mcp
# or
python3 src/mcp_server.py
```

The server will run in stdio mode, waiting for MCP client connections.

## MCP Client Integration

### Claude Desktop

1. Find your Claude Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the ollama-search server:
```json
{
  "mcpServers": {
    "ollama-search": {
      "command": "python3",
      "args": [
        "/absolute/path/to/ollama-search/src/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

3. Restart Claude Desktop

4. The tools should now appear in Claude Desktop:
   - `ollama_web_search` - Search the web
   - `ollama_web_fetch` - Fetch webpage content
   - `ollama_intelligent_search` - AI-powered search with automatic tool use

### Other MCP Clients

Any MCP-compatible client can connect using stdio transport:
```bash
python3 src/mcp_server.py
```

## Available Tools

### ollama_web_search
Search the web using Ollama's search capability.

**Parameters:**
- `query` (required): The search query
- `verbose` (optional): Show intermediate steps

**Example:**
```json
{
  "query": "latest Python best practices",
  "verbose": false
}
```

### ollama_web_fetch
Fetch content from a specific URL.

**Parameters:**
- `url` (required): The URL to fetch
- `verbose` (optional): Show intermediate steps

**Example:**
```json
{
  "url": "https://docs.python.org/3/",
  "verbose": false
}
```

### ollama_intelligent_search
Intelligent search that can automatically search and fetch content.

**Parameters:**
- `query` (required): The question to answer
- `model` (optional): Ollama model to use (default: mistral:7b-instruct)
- `verbose` (optional): Show intermediate steps

**Example:**
```json
{
  "query": "What are the new features in Python 3.12?",
  "model": "mistral:7b-instruct",
  "verbose": false
}
```

## Architecture

```
┌─────────────────┐
│   MCP Client    │
│ (Claude, etc.)  │
└────────┬────────┘
         │ stdio
         │ (JSON-RPC)
┌────────▼────────┐
│   MCP Server    │
│  (mcp_server.py)│
├─────────────────┤
│  Tool Handlers  │
├─────────────────┤
│ Search Agent    │
├─────────────────┤
│ Ollama API      │
│ web_search      │
│ web_fetch       │
└─────────────────┘
```

## Troubleshooting

### Server won't start
- Check that `mcp` package is installed: `pip3 list | grep mcp`
- Verify Ollama is running: `ollama list`
- Check logs for errors

### Tools not appearing in client
- Verify config file path is correct
- Check that absolute paths are used in config
- Restart the MCP client after config changes
- Check client logs for connection errors

### Search/fetch not working
- Ensure Ollama server is running: `ollama serve`
- Check that the specified model is available: `ollama list`
- Test the search agent directly: `make run`

## Development

Run tests:
```bash
pytest tests/test_mcp_server.py
```

Test manually:
```bash
python3 tests/test_mcp_manual.py
```

## Next Steps

- Add more search configuration options
- Implement result caching
- Add support for different search engines
- Create resources for documentation sources
- Add prompts for common search patterns
