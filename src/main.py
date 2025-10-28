"""Main entry point for the Ollama search agent."""

import argparse
import logging
import sys
from typing import Any

from ollama._types import Message

from .search_agent import SearchAgent


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application.

    Args:
        verbose: Whether to enable debug logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    """Run the search agent CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Ollama Search Agent - Search and fetch web content using Ollama"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query to execute",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="mistral:7b-instruct",
        help="Ollama model to use (default: mistral:7b-instruct)",
    )
    parser.add_argument(
        "--max-result-length",
        type=int,
        default=8000,
        help="Maximum length of tool results (default: 8000)",
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        help=(
            "Enable thinking feature "
            "(only works with compatible models like qwen, deepseek-r1)"
        ),
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress intermediate output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    agent = SearchAgent(
        model=args.model,
        max_result_length=args.max_result_length,
        enable_thinking=args.thinking,
    )

    try:
        if args.interactive:
            print("Ollama Search Agent - Interactive Mode")
            print("Type 'exit' or 'quit' to end the session")
            print("-" * 50)

            conversation_history: list[dict[str, Any] | Message] = []
            while True:
                try:
                    query = input("\nQuery: ").strip()
                    if query.lower() in ("exit", "quit"):
                        print("Goodbye!")
                        break

                    if not query:
                        continue

                    print("-" * 50)
                    response, conversation_history = agent.search_with_history(
                        query, conversation_history, verbose=not args.quiet
                    )
                    print("-" * 50)
                    print(f"\nFinal Answer: {response}")

                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break

        else:
            if not args.query:
                parser.print_help()
                return 1

            response = agent.search(args.query, verbose=not args.quiet)
            print(f"\nFinal Answer: {response}")

        return 0

    except Exception as e:
        logging.error("Error executing search: %s", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
