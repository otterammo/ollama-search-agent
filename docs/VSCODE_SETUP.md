# VS Code MCP Integration

## Overview

VS Code can connect to MCP servers through the GitHub Copilot extension (with MCP support) or other MCP-compatible VS Code extensions.

## Setup for VS Code

### Option 1: Using VS Code Settings (Recommended)

1. Open VS Code settings (JSON):
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Preferences: Open User Settings (JSON)"
   - Press Enter

2. Add the MCP server configuration:

```json
{
  "mcp.servers": {
    "ollama-search": {
      "command": "python3",
      "args": [
        "/absolute/path/to/ollama-search/src/mcp_server.py"
      ],
      "env": {},
      "description": "Ollama web search and fetch capabilities"
    }
  }
}
```

### Option 2: Workspace Settings

For project-specific configuration, create `.vscode/settings.json` in your workspace:

```json
{
  "mcp.servers": {
    "ollama-search": {
      "command": "python3",
      "args": [
        "${workspaceFolder}/../ollama-search/src/mcp_server.py"
      ],
      "description": "Ollama search agent for documentation"
    }
  }
}
```

### Option 3: GitHub Copilot with MCP

If using GitHub Copilot with MCP support:

1. Install GitHub Copilot extension (if not already installed)
2. Check if MCP support is available in your Copilot version
3. Configure in Copilot settings or use the VS Code settings above

## Testing the Integration

1. **Verify the server starts:**
   ```bash
   python3 /absolute/path/to/ollama-search/src/mcp_server.py
   ```
   Press `Ctrl+C` to stop.

2. **Check VS Code output:**
   - Open Output panel: `View > Output`
   - Select "MCP" or "Copilot" from the dropdown
   - Look for connection messages

3. **Test tool availability:**
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

1. **Check Python path:**
   ```bash
   which python3
   ```
   Update the `command` in settings if different.

2. **Verify dependencies:**
   ```bash
   cd /path/to/ollama-search
   pip3 list | grep -E "ollama|mcp"
   ```

3. **Check Ollama is running:**
   ```bash
   ollama list
   ```

4. **Test server manually:**
   ```bash
   cd /path/to/ollama-search
   python3 src/mcp_server.py
   ```

### Tools not appearing

1. Restart VS Code after configuration changes
2. Check VS Code Developer Tools:
   - `Help > Toggle Developer Tools`
   - Look for MCP-related errors in Console

3. Verify MCP extension is installed and enabled:
   - `Extensions: Show Installed Extensions`
   - Look for MCP or Copilot extensions

### Permission issues

If you get permission errors:
```bash
chmod +x /path/to/ollama-search/src/mcp_server.py
```

## Advanced Configuration

### Environment Variables

Add environment variables to the MCP server:

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

To use a different Ollama model, you can modify the intelligent search calls to specify the model parameter.

### Multiple Instances

Run different instances with different models:

```json
{
  "mcp.servers": {
    "ollama-search-mistral": {
      "command": "python3",
      "args": ["/absolute/path/to/ollama-search/src/mcp_server.py"]
    },
    "ollama-search-codellama": {
      "command": "python3",
      "args": ["/absolute/path/to/ollama-search/src/mcp_server.py"],
      "env": {
        "DEFAULT_MODEL": "codellama:34b"
      }
    }
  }
}
```

## VS Code Tasks Integration

Create `.vscode/tasks.json` to run the MCP server as a VS Code task:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Ollama MCP Server",
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

1. **Extension Structure:**
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
