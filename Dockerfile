FROM python:3.11-slim

LABEL maintainer="ollama-search"
LABEL description="Ollama Search MCP Server"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

RUN pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://host.docker.internal:11434

CMD ["ollama-mcp-server"]
