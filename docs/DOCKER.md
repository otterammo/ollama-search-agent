# Docker Setup for Ollama Search MCP Server

This guide explains how to run the Ollama Search MCP Server in a Docker container.

## Prerequisites

- Docker and Docker Compose installed
- Ollama running on your host machine (accessible at `http://localhost:11434`)

## Quick Reference

### Build Commands

```bash
make docker-build          # Build Docker image
docker build -t ollama-mcp-server .
```

### Run Commands

```bash
make docker-run            # Run interactively
make docker-up             # Start with docker compose
make docker-down           # Stop docker compose services
make docker-logs           # View logs
```

### Test

```bash
./scripts/test-docker.sh   # Run comprehensive tests
```

### Development Mode

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Files Created

- `Dockerfile` - Main Docker image definition
- `docker-compose.yml` - Production compose config
- `docker-compose.dev.yml` - Development compose override
- `.dockerignore` - Files to exclude from build
- `.env.example` - Environment variable template
- `scripts/test-docker.sh` - Docker setup test script

## Quick Start

### Build and Run with Docker Compose

```bash
docker compose up -d
```

### Build and Run with Docker

```bash
docker build -t ollama-mcp-server .
docker run -it --rm \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --add-host=host.docker.internal:host-gateway \
  ollama-mcp-server
```

## Detailed Setup

### Environment Variables

- `OLLAMA_HOST`: URL to your Ollama instance (default: `http://host.docker.internal:11434`)
- `PYTHONUNBUFFERED`: Set to `1` for immediate log output

### Accessing Host Ollama Instance

The Docker setup is configured to access Ollama running on the host machine:

#### Linux
Use `host.docker.internal:host-gateway` mapping (included in docker-compose.yml)

#### macOS/Windows
Docker Desktop automatically provides `host.docker.internal`

#### Custom Network Setup
If Ollama is on a different host:
```bash
docker run -it --rm \
  -e OLLAMA_HOST=http://your-ollama-host:11434 \
  ollama-mcp-server
```

## Using with MCP Clients

### Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
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

### VS Code Configuration

Add to your VS Code settings.json:

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
      ]
    }
  }
}
```

## Development

### Mount Source Code for Development

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Or manually:
```bash
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --add-host=host.docker.internal:host-gateway \
  ollama-mcp-server
```

### Testing the Server

Using MCP Inspector:
```bash
docker run -it --rm \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --add-host=host.docker.internal:host-gateway \
  ollama-mcp-server \
  ollama-mcp-server --help
```

## Troubleshooting

### Cannot Connect to Ollama

1. Verify Ollama is running on host:
   ```bash
   curl http://localhost:11434/api/version
   ```

2. Check Docker network connectivity:
   ```bash
   docker run --rm --add-host=host.docker.internal:host-gateway \
     curlimages/curl http://host.docker.internal:11434/api/version
   ```

3. Try explicit host IP instead of `host.docker.internal`

### Logs

View container logs:
```bash
docker compose logs -f ollama-mcp-server
```

Or for standalone container:
```bash
docker logs <container-id>
```

### Rebuild After Changes

```bash
docker compose build --no-cache
docker compose up -d
```

## Production Deployment

For production deployments, consider:

1. Using a specific Python version tag instead of `slim`
2. Setting resource limits in docker-compose.yml
3. Using Docker secrets for sensitive configuration
4. Running Ollama in a separate container and using Docker networks
5. Setting up health checks

Example production docker-compose.yml snippet:
```yaml
services:
  ollama-mcp-server:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "python3", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```
