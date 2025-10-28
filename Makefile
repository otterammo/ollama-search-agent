.PHONY: help install test lint type-check format clean run run-mcp docker-build docker-run docker-up docker-down docker-logs

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip3 install -r requirements.txt

install-dev: ## Install development dependencies
	pip3 install -e ".[dev]"

test: ## Run tests with coverage
	pytest

lint: ## Run ruff linter
	ruff check src/ tests/

type-check: ## Run mypy type checker
	MYPYPATH=. mypy src/

format: ## Format code with ruff
	ruff format src/ tests/

clean: ## Remove build artifacts and cache
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete

run: ## Run the search agent interactively
	cd src && python3 main.py --interactive

run-mcp: ## Run the MCP server
	python3 src/mcp_server.py

docker-build: ## Build Docker image
	docker build -t ollama-mcp-server .

docker-run: ## Run Docker container interactively
	docker run -it --rm \
		-e OLLAMA_HOST=http://host.docker.internal:11434 \
		--add-host=host.docker.internal:host-gateway \
		ollama-mcp-server

docker-up: ## Start Docker Compose services
	docker compose up -d

docker-down: ## Stop Docker Compose services
	docker compose down

docker-logs: ## View Docker Compose logs
	docker compose logs -f ollama-mcp-server
