# Ollama Search Agent

A search agent using Ollama's web search API for reading and understanding online documentation.

## Prerequisites

### Ollama API Key (Required)

The web search and web fetch features require an Ollama API key. Follow these steps:

1. **Get an API Key:**
   - Visit [https://ollama.com](https://ollama.com)
   - Sign up or log in to your account
   - Generate an API key from your account settings

2. **Configure the API Key:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API key
   # OLLAMA_API_KEY=your-api-key-here
   ```

3. **Verify Setup:**
   ```bash
   # The API key will be automatically loaded from .env
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key configured!' if os.getenv('OLLAMA_API_KEY') else 'API Key missing!')"
   ```

**Important:** The `.env` file is git-ignored to protect your API key. Never commit it to version control.

## Installation

### Local Installation

```bash
pip3 install -r requirements.txt
```

### Docker Installation

See [docs/DOCKER.md](docs/DOCKER.md) for comprehensive Docker setup instructions.

Quick start with Docker:
```bash
make docker-build
make docker-run
```

Or using Docker Compose:
```bash
make docker-up
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

#### VS Code

See [VSCODE_SETUP.md](VSCODE_SETUP.md) for detailed VS Code integration.

**Local Installation:**

Quick setup - add to VS Code .vscode/mcp.json:
```json
{
  "servers": {
    "ollama-search": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "OLLAMA_HOST=http://host.docker.internal:11434",
        "--add-host=host.docker.internal:host-gateway",
        "ollama-mcp-server"
      ]
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

## Troubleshooting

### Authorization Error

**Error:** `Authorization header with Bearer token is required for web search`

**Solution:** 
1. Ensure you have set up your `.env` file with your Ollama API key:
   ```bash
   cp .env.example .env
   # Edit .env and add: OLLAMA_API_KEY=your-api-key-here
   ```

2. Verify the API key is loaded:
   ```bash
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ API Key configured' if os.getenv('OLLAMA_API_KEY') else '✗ API Key missing')"
   ```

3. For Docker/MCP integration, ensure the `-e OLLAMA_API_KEY=your-api-key-here` environment variable is passed to the container.

### API Key Not Working

**Problem:** You have the API key set but still get errors.

**Solution:**
1. Check if the API key is valid by visiting [https://ollama.com](https://ollama.com)
2. Ensure there are no extra spaces or quotes in your `.env` file
3. Restart any running processes to reload the environment variables

### Connection Issues

**Problem:** Cannot connect to Ollama server.

**Solution:**
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check the `OLLAMA_HOST` variable in your `.env` file
3. For Docker, ensure host networking is properly configured

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
