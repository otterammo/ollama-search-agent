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
