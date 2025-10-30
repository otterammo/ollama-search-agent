# VS Code MCP Integration

## Overview

VS Code can connect to MCP servers through the GitHub Copilot extension (with MCP support) or other MCP-compatible VS Code extensions. This guide shows how to integrate the Ollama Search MCP server running in Docker with VS Code.

## Prerequisites

- Docker and Docker Compose installed
- Ollama running on your host machine
- VS Code with GitHub Copilot extension (or other MCP-compatible extension)
- MCP server Docker image built (`make docker-build`)

## Setup for VS Code

### Option 1: Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   make docker-build
   ```

2. Open VS Code settings (JSON):
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Preferences: Open User Settings (JSON)"
   - Press Enter

3. Add the MCP server configuration:

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

### Option 2: Using Python Directly (Development)

For local development without Docker:

```json
{
  "mcp.servers": {
    "ollama-search": {
      "command": "python3",
      "args": [
        "/absolute/path/to/ollama-search/src/mcp_server.py"
      ],
      "env": {},
      "description": "Ollama web search and fetch capabilities (local dev)"
    }
  }
}
```
### Option 3: Workspace Settings (Docker)

For project-specific configuration, create `.vscode/settings.json` in your workspace:

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
      "description": "Ollama search agent (Docker)"
    }
  }
}
```

## Testing the Integration

1. **Verify the Docker image exists:**
   ```bash
   docker images | grep ollama-mcp-server
   ```
   If not found, build it: `make docker-build`

2. **Test the server manually:**
   ```bash
   make docker-run
   ```
   Press `Ctrl+C` to stop.

3. **Check VS Code output:**
   - Open Output panel: `View > Output`
   - Select "MCP" or "Copilot" from the dropdown
   - Look for connection messages

4. **Test tool availability:**
   - Open Copilot chat
   - The MCP tools should be available automatically
   - Try: "Use the ollama search to find information about Python async"

## Available Tools in VS Code

Once connected, these tools are available to Copilot/MCP clients:

### 1. ollama_web_search
Search the web for information.

**Example usage in Copilot:**
```
@ollama-search search for "Python 3.12 new features"
```

### 2. ollama_web_fetch
Fetch content from a specific URL.

**Example usage in Copilot:**
```
@ollama-search fetch https://docs.python.org/3/whatsnew/3.12.html
```

### 3. ollama_intelligent_search
AI-powered search that combines search and fetch.

**Example usage in Copilot:**
```
@ollama-search What are the breaking changes in Python 3.12?
```

## Troubleshooting

### Server not connecting

1. **Check Docker image:**
   ```bash
   docker images | grep ollama-mcp-server
   ```
   If missing, build it: `make docker-build`

2. **Verify Docker is running:**
   ```bash
   docker ps
   ```

3. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/version
   ```

4. **Test Docker connectivity to Ollama:**
   ```bash
   docker run --rm --add-host=host.docker.internal:host-gateway \
     curlimages/curl http://host.docker.internal:11434/api/version
   ```

5. **For Python direct mode, check dependencies:**
   ```bash
   cd /path/to/ollama-search
   pip3 list | grep -E "ollama|mcp"
   ```

### Tools not appearing

1. Restart VS Code after configuration changes
2. Verify MCP settings key is `"mcp.servers"` (not `"servers"`)
3. Check Docker image name matches: `ollama-mcp-server`
4. Check VS Code Developer Tools:
   - `Help > Toggle Developer Tools`
   - Look for MCP-related errors in Console
5. Verify MCP extension is installed and enabled:
   - `Extensions: Show Installed Extensions`
   - Look for MCP or Copilot extensions

### Docker-specific issues

1. **Container exits immediately:**
   - Check logs: `docker logs <container-id>`
   - Test manually: `make docker-run`

2. **Cannot connect to host Ollama:**
   - Verify `host.docker.internal` is accessible
   - On Linux, ensure `--add-host=host.docker.internal:host-gateway` is set
   - Try using your host IP directly instead of `host.docker.internal`

For more troubleshooting, see [DOCKER.md](./DOCKER.md).

## Advanced Configuration

### Environment Variables (Docker)

Add environment variables to the Docker MCP server:

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
        "-e",
        "LOG_LEVEL=DEBUG",
        "--add-host=host.docker.internal:host-gateway",
        "ollama-mcp-server"
      ]
    }
  }
}
```

### Environment Variables (Python Direct)

For local development without Docker:

```json
{
  "mcp.servers": {
    "ollama-search": {
      "command": "python3",
      "args": ["/absolute/path/to/ollama-search/src/mcp_server.py"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Custom Model Selection

To use a different Ollama model, you can modify the intelligent search calls to specify the model parameter when calling the tools.

### Multiple Instances

Run different instances with different models using Docker:

```json
{
  "mcp.servers": {
    "ollama-search-mistral": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "OLLAMA_HOST=http://host.docker.internal:11434",
        "--add-host=host.docker.internal:host-gateway",
        "ollama-mcp-server"
      ],
      "description": "Ollama Search with Mistral"
    },
    "ollama-search-codellama": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "OLLAMA_HOST=http://host.docker.internal:11434",
        "-e", "DEFAULT_MODEL=codellama:34b",
        "--add-host=host.docker.internal:host-gateway",
        "ollama-mcp-server"
      ],
      "description": "Ollama Search with CodeLlama"
    }
  }
}
```

## VS Code Tasks Integration

### Using Docker Compose (Recommended)

Create or update `.vscode/tasks.json` to run the MCP server with Docker:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Ollama MCP Server (Docker)",
      "type": "shell",
      "command": "make",
      "args": ["docker-up"],
      "isBackground": true,
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Stop Ollama MCP Server (Docker)",
      "type": "shell",
      "command": "make",
      "args": ["docker-down"],
      "problemMatcher": []
    }
  ]
}
```

### Using Python Directly (Development)

For local development:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Ollama MCP Server (Python)",
      "type": "shell",
      "command": "python3",
      "args": [
        "${workspaceFolder}/src/mcp_server.py"
      ],
      "isBackground": true,
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    }
  ]
}
```

Run with: `Terminal > Run Task... > Start Ollama MCP Server`

## VS Code Extension Development

If you want to create a dedicated VS Code extension for this MCP server:
   ```
   ollama-search-vscode/
   ├── package.json
   ├── src/
   │   └── extension.ts
   └── mcp-server/  (symlink or copy of your MCP server)
   ```

2. **Package.json example:**
   ```json
   {
     "name": "ollama-search-mcp",
     "displayName": "Ollama Search MCP",
     "description": "Ollama web search MCP server for VS Code",
     "version": "0.1.0",
     "engines": {
       "vscode": "^1.80.0"
     },
     "contributes": {
       "configuration": {
         "title": "Ollama Search MCP",
         "properties": {
           "ollama-search.defaultModel": {
             "type": "string",
             "default": "mistral:7b-instruct",
             "description": "Default Ollama model to use"
           }
         }
       }
     }
   }
   ```

## Best Practices

1. **Keep server running:** The MCP server should auto-start when VS Code needs it
2. **Log errors:** Check VS Code output for MCP server logs
3. **Resource usage:** Monitor if the server impacts VS Code performance
4. **Model selection:** Use appropriate models for your use case (smaller models for speed, larger for accuracy)
5. **Rate limiting:** Be mindful of API call frequency

## Example Workflows

### Documentation Research
```
1. Ask Copilot: "Search for Spring Boot 3.0 migration guide"
2. Copilot uses ollama_intelligent_search
3. Results appear in chat
4. Continue conversation to dive deeper
```

### Code Analysis
```
1. Ask: "Fetch the official Python asyncio documentation"
2. Use ollama_web_fetch with the URL
3. Ask follow-up questions about the content
```

### Quick Lookups
```
1. Highlight code in editor
2. Ask Copilot: "Search for best practices for this pattern"
3. Get context-aware search results
```

## Resources

- [VS Code MCP Documentation](https://code.visualstudio.com/docs/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Ollama Documentation](https://ollama.ai/docs)
- [GitHub Copilot Documentation](https://docs.github.com/copilot)
