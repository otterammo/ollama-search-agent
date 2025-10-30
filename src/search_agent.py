"""Search agent using Ollama's web search and fetch capabilities."""

import logging
from collections.abc import Callable
from typing import Any

from ollama import chat, web_fetch, web_search
from ollama._types import Message

logger = logging.getLogger(__name__)

# Context window sizes to try in descending order
CONTEXT_FALLBACK_SIZES = [32768, 16384, 8192, 4096]


def detect_working_context(model: str, preferred_ctx: int | None = None) -> int:
    """Detect the maximum working context window size for a model.
    
    Tries context sizes in descending order until one works.
    Caches successful results to avoid repeated testing.
    
    Args:
        model: The Ollama model name
        preferred_ctx: Preferred context size to try first
        
    Returns:
        Working context window size in tokens
    """
    # Check if we've already detected this model's limit
    cache_key = f"_ctx_limit_{model}"
    if hasattr(detect_working_context, cache_key):
        cached_limit = getattr(detect_working_context, cache_key)
        logger.info("Using cached context limit for %s: %d", model, cached_limit)
        return cached_limit
    
    # Build list of sizes to try
    sizes_to_try = list(CONTEXT_FALLBACK_SIZES)
    if preferred_ctx and preferred_ctx not in sizes_to_try:
        sizes_to_try.insert(0, preferred_ctx)
        sizes_to_try.sort(reverse=True)
    
    logger.info("Auto-detecting context window limit for model: %s", model)
    
    for ctx_size in sizes_to_try:
        logger.debug("Testing %s with context size: %d", model, ctx_size)
        try:
            # Simple test to see if the model accepts this context size
            response = chat(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                options={"num_ctx": ctx_size}
            )
            
            if response and response.message:
                logger.info(
                    "Model %s successfully tested with context size: %d",
                    model,
                    ctx_size
                )
                # Cache the successful size
                setattr(detect_working_context, cache_key, ctx_size)
                return ctx_size
                
        except Exception as e:
            error_msg = str(e)
            logger.debug(
                "Model %s failed at context size %d: %s",
                model,
                ctx_size,
                error_msg[:100]
            )
            
            # If it's a termination error, try smaller context
            if "terminated" in error_msg.lower() or "exit status" in error_msg.lower():
                continue
            else:
                # For other errors, re-raise
                raise
    
    # Fallback to minimum safe size
    logger.warning(
        "Could not find working context for %s, using minimum: 2048",
        model
    )
    return 2048


class SearchAgent:
    """Agent that uses Ollama to search and fetch web content."""

    def __init__(
        self,
        model: str = "mistral:7b-instruct",
        max_result_length: int = 8000,
        enable_thinking: bool = False,
        num_ctx: int | None = None,
        auto_detect_context: bool = True,
    ) -> None:
        """Initialize the search agent.

        Args:
            model: The Ollama model to use for chat completions
            max_result_length: Maximum length of tool results to include in context
            enable_thinking: Whether to enable the thinking feature
                (only works with compatible models)
            num_ctx: Context window size in tokens. If None and auto_detect_context=True,
                automatically detects the maximum working context size.
            auto_detect_context: Whether to automatically detect and use the maximum
                working context size for the model (default: True)
        """
        self.model = model
        self.max_result_length = max_result_length
        self.enable_thinking = enable_thinking
        
        # Determine context window size
        if num_ctx is not None:
            # User explicitly specified context size
            self.num_ctx = num_ctx
            logger.info(
                "Initialized SearchAgent: model=%s, num_ctx=%d (user-specified)",
                self.model,
                self.num_ctx,
            )
        elif auto_detect_context:
            # Auto-detect maximum working context
            self.num_ctx = detect_working_context(model, preferred_ctx=32768)
            logger.info(
                "Initialized SearchAgent: model=%s, num_ctx=%d (auto-detected)",
                self.model,
                self.num_ctx,
            )
        else:
            # Use conservative default
            self.num_ctx = 8192
            logger.info(
                "Initialized SearchAgent: model=%s, num_ctx=%d (default)",
                self.model,
                self.num_ctx,
            )
        
        self.available_tools: dict[str, Callable[..., Any]] = {
            "web_search": web_search,
            "web_fetch": web_fetch,
        }

    def _filter_tool_arguments(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Filter tool arguments to only include valid parameters.
        
        Args:
            tool_name: Name of the tool being called
            args: Raw arguments from the model
            
        Returns:
            Filtered arguments dict with only valid parameters
        """
        if tool_name == "web_search":
            # web_search only accepts: query, max_results
            return {k: v for k, v in args.items() if k in ["query", "max_results"]}
        elif tool_name == "web_fetch":
            # web_fetch only accepts: url
            return {k: v for k, v in args.items() if k in ["url"]}
        else:
            # Unknown tool, pass all args
            return args

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
            try:
                response = chat(
                    model=self.model,
                    messages=messages,
                    tools=[web_search, web_fetch],
                    think=self.enable_thinking,
                    options={"num_ctx": self.num_ctx},
                )
            except Exception as e:
                error_msg = str(e)
                # If context is too large, try to reduce it
                if ("terminated" in error_msg.lower() or "exit status" in error_msg.lower()) and self.num_ctx > 2048:
                    old_ctx = self.num_ctx
                    self.num_ctx = self.num_ctx // 2
                    logger.warning(
                        "Context size %d failed, reducing to %d and retrying",
                        old_ctx,
                        self.num_ctx
                    )
                    continue
                else:
                    # For other errors or if already at minimum, re-raise
                    raise

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
                        # Filter arguments to only valid ones
                        raw_args = tool_call.function.arguments
                        valid_args = self._filter_tool_arguments(
                            tool_call.function.name, raw_args
                        )
                        
                        try:
                            result = function_to_call(**valid_args)
                        except Exception as e:
                            error_message = f"Tool {tool_call.function.name} error: {str(e)}"
                            logger.error(error_message)
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": error_message,
                                    "tool_name": tool_call.function.name,
                                }
                            )
                            continue

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
            try:
                response = chat(
                    model=self.model,
                    messages=messages,
                    tools=[web_search, web_fetch],
                    think=self.enable_thinking,
                    options={"num_ctx": self.num_ctx},
                )
            except Exception as e:
                error_msg = str(e)
                # If context is too large, try to reduce it
                if ("terminated" in error_msg.lower() or "exit status" in error_msg.lower()) and self.num_ctx > 2048:
                    old_ctx = self.num_ctx
                    self.num_ctx = self.num_ctx // 2
                    logger.warning(
                        "Context size %d failed, reducing to %d and retrying",
                        old_ctx,
                        self.num_ctx
                    )
                    continue
                else:
                    # For other errors or if already at minimum, re-raise
                    raise

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
                        # Filter arguments to only valid ones
                        raw_args = tool_call.function.arguments
                        valid_args = self._filter_tool_arguments(
                            tool_call.function.name, raw_args
                        )
                        
                        try:
                            result = function_to_call(**valid_args)
                        except Exception as e:
                            error_message = f"Tool {tool_call.function.name} error: {str(e)}"
                            logger.error(error_message)
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": error_message,
                                    "tool_name": tool_call.function.name,
                                }
                            )
                            continue

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
