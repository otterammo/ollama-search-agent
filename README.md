# Ollama Search Agent

A search agent using Ollama's web search API for reading and understanding online documentation.

## Installation

```bash
pip3 install -r requirements.txt
```

## Usage

Run interactively:
```bash
make run
```

Or directly:
```bash
cd src && python3 main.py --interactive
```

Single query:
```bash
cd src && python3 main.py "what is ollama's new engine"
```

Or import as a module:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from search_agent import SearchAgent

agent = SearchAgent(model="mistral:7b-instruct")
response = agent.search("what is ollama's new engine")
print(response)
```

## MCP Server

The MCP server runs in stdio mode, waiting for MCP client connections. It won't show output when run directly - it's designed to be launched by MCP clients.

To verify installation:

```bash
pip3 install -e .
ollama-mcp-server --help
```

To run (will wait for MCP client to connect via stdin):

```bash
ollama-mcp-server
# or
python3 src/mcp_server.py
```

### MCP Client Configuration

#### Claude Desktop

Add to your MCP client configuration (e.g., Claude Desktop's config):

```json
{
  "mcpServers": {
    "ollama-search": {
      "command": "python3",
      "args": ["/absolute/path/to/ollama-search/src/mcp_server.py"]
    }
  }
}
```

#### VS Code

See [VSCODE_SETUP.md](VSCODE_SETUP.md) for detailed VS Code integration.

Quick setup - add to VS Code settings.json:
```json
{
  "mcp.servers": {
    "ollama-search": {
      "command": "python3",
      "args": ["${workspaceFolder}/src/mcp_server.py"]
    }
  }
}
```

### Available MCP Tools

1. `ollama_web_search` - Search the web using Ollama
2. `ollama_web_fetch` - Fetch content from a specific URL
3. `ollama_intelligent_search` - Intelligent search that combines search and fetch automatically

### Testing the MCP Server

The MCP Inspector is an interactive debugging tool that helps you test MCP servers without needing a full client application. It provides a web-based UI where you can:

- View all available tools and their schemas
- Make test calls to tools with custom parameters
- See real-time request/response JSON
- Debug server behavior and responses

To use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python3 src/mcp_server.py
```

This will start the inspector (usually at `http://localhost:6274`) where you can interactively test all three tools. No installation required - `npx` runs it directly from the npm registry.

## Development

Install development dependencies:

```bash
pip3 install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run type checking:

```bash
mypy src/
```

Run linting:

```bash
ruff check src/
```
