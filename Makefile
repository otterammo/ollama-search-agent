.PHONY: help install test lint type-check format clean run run-mcp

help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run ruff linter"
	@echo "  type-check   - Run mypy type checker"
	@echo "  format       - Format code with ruff"
	@echo "  clean        - Remove build artifacts and cache"
	@echo "  run          - Run the search agent interactively"
	@echo "  run-mcp      - Run the MCP server"

install:
	pip3 install -r requirements.txt

install-dev:
	pip3 install -e ".[dev]"

test:
	pytest

lint:
	ruff check src/ tests/

type-check:
	MYPYPATH=. mypy src/

format:
	ruff format src/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete

run:
	cd src && python3 main.py --interactive

run-mcp:
	python3 src/mcp_server.py
