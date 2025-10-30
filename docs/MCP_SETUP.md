# MCP Server Setup Guide

## What is MCP?

Model Context Protocol (MCP) is a protocol that allows AI assistants (like VS Code with GitHub Copilot) to use external tools and data sources. This project implements an MCP server that exposes Ollama's web search and fetch capabilities.

## Prerequisites

- Docker and Docker Compose installed
- Ollama running on your host machine (accessible at `http://localhost:11434`)
- VS Code with GitHub Copilot extension (for VS Code integration)

## Quick Start

### Build the Docker Image

```bash
make docker-build
```

### Run the MCP Server with Docker

```bash
make docker-up
```

This starts the MCP server in a Docker container, configured to connect to Ollama on your host machine.

## Detailed Setup

For comprehensive Docker setup instructions, see [DOCKER.md](./DOCKER.md).

For VS Code integration instructions, see [VSCODE_SETUP.md](./VSCODE_SETUP.md).

## VS Code Integration

### Configure MCP Server in VS Code

1. Open VS Code settings (JSON):
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Preferences: Open User Settings (JSON)"
   - Press Enter

2. Add the MCP server configuration to use Docker:

```json
{
  "mcp.servers": {
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
      ],
      "description": "Ollama web search and fetch capabilities"
    }
  }
}
```

3. Reload VS Code window or restart VS Code

4. The tools should now be available in GitHub Copilot/MCP clients:
   - `ollama_web_search` - Search the web
   - `ollama_web_fetch` - Fetch webpage content
   - `ollama_intelligent_search` - AI-powered search with automatic tool use

For detailed VS Code configuration options, see [VSCODE_SETUP.md](./VSCODE_SETUP.md).

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
│   VS Code +     │
│ GitHub Copilot  │
└────────┬────────┘
         │ stdio
         │ (JSON-RPC)
┌────────▼────────┐
│ Docker Container│
│   MCP Server    │
│  (mcp_server.py)│
├─────────────────┤
│  Tool Handlers  │
├─────────────────┤
│ Search Agent    │
├─────────────────┤
│ Ollama API      │
│ (host machine)  │
│ web_search      │
│ web_fetch       │
└─────────────────┘
```

## Troubleshooting

### Server won't start
- Check that Docker image is built: `make docker-build`
- Verify Ollama is running: `curl http://localhost:11434/api/version`
- Check Docker logs: `make docker-logs`

### Tools not appearing in VS Code
- Verify Docker image name is correct: `docker images | grep ollama-mcp-server`
- Check that VS Code MCP settings use `"mcp.servers"` (not `"servers"`)
- Restart VS Code after config changes
- Check VS Code Output panel for MCP/Copilot errors

### Search/fetch not working
- Ensure Ollama server is running on host: `ollama list`
- Test Docker connectivity to host: 
  ```bash
  docker run --rm --add-host=host.docker.internal:host-gateway \
    curlimages/curl http://host.docker.internal:11434/api/version
  ```
- Check that the specified model is available: `ollama list`
- Check container logs: `make docker-logs`

For more troubleshooting help, see [DOCKER.md](./DOCKER.md).

## Development

### Run tests:
```bash
pytest tests/test_mcp_server.py
```

### Test Docker setup:
```bash
./scripts/test-docker.sh
```

### Development mode with live code updates:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This mounts your source code into the container for live development.

## Next Steps

- Configure additional Ollama models in your environment
- Explore advanced VS Code MCP configurations in [VSCODE_SETUP.md](./VSCODE_SETUP.md)
- Set up production deployment options in [DOCKER.md](./DOCKER.md)
- Add custom search configurations
- Implement result caching
