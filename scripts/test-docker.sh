#!/usr/bin/env bash
set -e

echo "Testing Ollama Search MCP Server Docker Setup"
echo "=============================================="
echo

echo "1. Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi
echo "   Docker version: $(docker --version)"
echo

echo "2. Checking if Ollama is running on host..."
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "   Ollama is running"
    OLLAMA_VERSION=$(curl -s http://localhost:11434/api/version)
    echo "   Version: $OLLAMA_VERSION"
else
    echo "   Warning: Cannot connect to Ollama at http://localhost:11434"
    echo "   Make sure Ollama is running for full functionality"
fi
echo

echo "3. Building Docker image..."
docker build -t ollama-mcp-server . || {
    echo "Error: Failed to build Docker image"
    exit 1
}
echo "   Build successful"
echo

echo "4. Testing Docker container startup..."
timeout 5s docker run --rm \
    -e OLLAMA_HOST=http://host.docker.internal:11434 \
    --add-host=host.docker.internal:host-gateway \
    ollama-mcp-server ollama-mcp-server --help > /tmp/docker-test-output.txt 2>&1 || true

if grep -q "Ollama Search MCP Server" /tmp/docker-test-output.txt; then
    echo "   Container startup successful"
    echo "   Help output:"
    cat /tmp/docker-test-output.txt | head -20
else
    echo "   Warning: Container startup may have issues"
    cat /tmp/docker-test-output.txt
fi
echo

echo "5. Verifying installed packages in container..."
docker run --rm ollama-mcp-server pip3 list | grep -E "(ollama|mcp)" || true
echo

echo "=============================================="
echo "Docker setup test complete!"
echo
echo "To run the MCP server:"
echo "  make docker-run"
echo
echo "To use with Docker Compose:"
echo "  make docker-up"
echo "  make docker-logs"
echo
echo "For more information, see DOCKER.md"
