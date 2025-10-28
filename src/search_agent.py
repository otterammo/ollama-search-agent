"""Search agent using Ollama's web search and fetch capabilities."""

import logging
from collections.abc import Callable
from typing import Any

from ollama import chat, web_fetch, web_search
from ollama._types import Message

logger = logging.getLogger(__name__)


class SearchAgent:
    """Agent that uses Ollama to search and fetch web content."""

    def __init__(
        self,
        model: str = "mistral:7b-instruct",
        max_result_length: int = 8000,
        enable_thinking: bool = False,
    ) -> None:
        """Initialize the search agent.

        Args:
            model: The Ollama model to use for chat completions
            max_result_length: Maximum length of tool results to include in context
            enable_thinking: Whether to enable the thinking feature
                (only works with compatible models)
        """
        self.model = model
        self.max_result_length = max_result_length
        self.enable_thinking = enable_thinking
        self.available_tools: dict[str, Callable[..., Any]] = {
            "web_search": web_search,
            "web_fetch": web_fetch,
        }

    def search(self, query: str, verbose: bool = True) -> str:
        """Execute a search query using the agent.

        Args:
            query: The search query or question to ask
            verbose: Whether to print intermediate steps

        Returns:
            The final response from the agent
        """
        messages: list[dict[str, Any] | Message] = [
            {"role": "user", "content": query}
        ]

        while True:
            response = chat(
                model=self.model,
                messages=messages,
                tools=[web_search, web_fetch],
                think=self.enable_thinking,
            )

            if response.message.thinking and verbose:
                logger.info("Thinking: %s", response.message.thinking)
                print(f"Thinking: {response.message.thinking}")

            if response.message.content and verbose:
                logger.info("Content: %s", response.message.content)
                print(f"Content: {response.message.content}")

            messages.append(response.message)

            if response.message.tool_calls:
                if verbose:
                    logger.info("Tool calls: %s", response.message.tool_calls)
                    print(f"Tool calls: {response.message.tool_calls}")

                for tool_call in response.message.tool_calls:
                    function_to_call = self.available_tools.get(
                        tool_call.function.name
                    )

                    if function_to_call:
                        args = tool_call.function.arguments
                        result = function_to_call(**args)

                        if verbose:
                            result_preview = str(result)[:200]
                            logger.info("Result: %s...", result_preview)
                            print(f"Result: {result_preview}...")

                        truncated_result = str(result)[: self.max_result_length]
                        messages.append(
                            {
                                "role": "tool",
                                "content": truncated_result,
                                "tool_name": tool_call.function.name,
                            }
                        )
                    else:
                        error_message = f"Tool {tool_call.function.name} not found"
                        logger.error(error_message)
                        messages.append(
                            {
                                "role": "tool",
                                "content": error_message,
                                "tool_name": tool_call.function.name,
                            }
                        )
            else:
                break

        return response.message.content if response.message.content else ""

    def search_with_history(
        self,
        query: str,
        conversation_history: list[dict[str, Any] | Message],
        verbose: bool = True,
    ) -> tuple[str, list[dict[str, Any] | Message]]:
        """Execute a search query with existing conversation history.

        Args:
            query: The search query or question to ask
            conversation_history: Previous conversation messages
            verbose: Whether to print intermediate steps

        Returns:
            Tuple of (final response, updated conversation history)
        """
        messages: list[dict[str, Any] | Message] = list(
            conversation_history
        ) + [{"role": "user", "content": query}]

        while True:
            response = chat(
                model=self.model,
                messages=messages,
                tools=[web_search, web_fetch],
                think=self.enable_thinking,
            )

            if response.message.thinking and verbose:
                logger.info("Thinking: %s", response.message.thinking)
                print(f"Thinking: {response.message.thinking}")

            if response.message.content and verbose:
                logger.info("Content: %s", response.message.content)
                print(f"Content: {response.message.content}")

            messages.append(response.message)

            if response.message.tool_calls:
                if verbose:
                    logger.info("Tool calls: %s", response.message.tool_calls)
                    print(f"Tool calls: {response.message.tool_calls}")

                for tool_call in response.message.tool_calls:
                    function_to_call = self.available_tools.get(
                        tool_call.function.name
                    )

                    if function_to_call:
                        args = tool_call.function.arguments
                        result = function_to_call(**args)

                        if verbose:
                            result_preview = str(result)[:200]
                            logger.info("Result: %s...", result_preview)
                            print(f"Result: {result_preview}...")

                        truncated_result = str(result)[: self.max_result_length]
                        messages.append(
                            {
                                "role": "tool",
                                "content": truncated_result,
                                "tool_name": tool_call.function.name,
                            }
                        )
                    else:
                        error_message = f"Tool {tool_call.function.name} not found"
                        logger.error(error_message)
                        messages.append(
                            {
                                "role": "tool",
                                "content": error_message,
                                "tool_name": tool_call.function.name,
                            }
                        )
            else:
                break

        return (
            response.message.content if response.message.content else "",
            messages,
        )
