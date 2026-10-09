"""
Shared logic for every AI provider.

A provider only has to say HOW to create its API client. The tool-calling
loop (web search), retries and friendly error messages live here so
they are written once and work for Hugging Face, Groq and Gemini alike.
"""

import json
import logging
import time
from typing import Any

from tools.web_search import SEARCH_WEB_TOOL, search_web


logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 6
MAX_RESPONSE_TOKENS = 2048
MAX_CALL_RETRIES = 4
RETRY_BACKOFF_BASE = 1.8


class ProviderError(Exception):
    """An error whose message is safe and helpful to show to the user."""


def _status_code(error: Exception) -> int | None:
    """Try to find an HTTP status code on an exception."""
    code = getattr(error, "status_code", None)

    if code is None:
        response = getattr(error, "response", None)
        code = getattr(response, "status_code", None)

    return code if isinstance(code, int) else None


def friendly_error(error: Exception, provider_label: str, model: str) -> str:
    """Turn a raw API exception into a clear one-line explanation."""
    status = _status_code(error)
    text = str(error)
    if status == 402 or "payment required" in text.lower() or "no remaining credits" in text.lower():
        return (
            f"{provider_label} credits have run out. "
            "Please choose another provider (Groq or Gemini) from the sidebar."
        )
    if status in (401, 403) or "invalid api key" in text.lower():
        return (
            f"{provider_label} rejected the API key. Check that the key in "
            "your .env file is correct and still active."
        )
    if status == 404 or "model_not_found" in text or "does not exist" in text:
        return (
            f"The model '{model}' was not found on {provider_label}. "
            "Update the model name in your .env file."
        )
    if status == 429:
        return (
            f"{provider_label} rate limit reached. Wait a moment and try "
            "again, or switch provider in the sidebar."
        )
    if status is not None and status >= 500:
        return f"{provider_label} is temporarily unavailable. Please retry."

    return f"{provider_label} request failed: {text}"


def _is_transient(error: Exception) -> bool:
    status = _status_code(error)
    text = str(error).lower()

    return (
        status in (429, 500, 502, 503, 504)
        or "model busy" in text
        or "overloaded" in text
        or "rate limit" in text
    )


def _message_to_dict(message: Any) -> Any:
    """Convert an SDK message object to a plain dict for the next request."""
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    return message


class BaseProvider:
    """Subclasses set `name`, `label`, `model` and implement `_create`."""

    name = "base"
    label = "Base"
    model = ""

    def _create(self, **kwargs: Any):
        """Send one chat-completion request. Implemented by subclasses."""
        raise NotImplementedError

    # -----------------------------------------------------------
    # Requests with retry
    # -----------------------------------------------------------
    def _create_completion(self, **kwargs: Any):
        attempt = 0

        while True:
            try:
                return self._create(**kwargs)
            except Exception as error:
                attempt += 1

                if not _is_transient(error) or attempt >= MAX_CALL_RETRIES:
                    raise ProviderError(
                        friendly_error(error, self.label, self.model)
                    ) from error

                wait = RETRY_BACKOFF_BASE ** (attempt - 1)
                logger.warning(
                    "%s transient error (attempt %d), retrying in %.1fs: %s",
                    self.label, attempt, wait, error,
                )
                time.sleep(wait)

    # -----------------------------------------------------------
    # Tools
    # -----------------------------------------------------------
    def execute_tool(self, function_name: str, arguments: dict) -> dict:
        if function_name == "search_web":
            query = str(arguments.get("query", ""))
            logger.info("Web search: %s", query)

            return search_web(
                query=query,
                max_results=arguments.get("max_results", 5),
            )

        return {"error": f"Unknown tool requested: {function_name}"}

    def _run_tool_call(self, tool_call: Any) -> dict:
        """Parse the model's arguments and run the requested tool."""
        raw = tool_call.function.arguments

        try:
            arguments = json.loads(raw) if isinstance(raw, str) else raw

            if not isinstance(arguments, dict):
                raise TypeError("Tool arguments must be a dictionary.")
        except (json.JSONDecodeError, TypeError) as error:
            return {"error": f"Invalid tool arguments: {error}"}

        return self.execute_tool(tool_call.function.name, arguments)

    @staticmethod
    def _text_of(message: Any) -> str:
        return (
            getattr(message, "content", None)
            or getattr(message, "text", None)
            or ""
        )

    # -----------------------------------------------------------
    # Main entry point
    # -----------------------------------------------------------
    def chat(self, messages: list[dict]) -> str:
        """Answer the conversation, letting the model use web search."""

        # Tool messages live only in this copy, not in the visible history.
        working = list(messages)

        for round_number in range(1, MAX_TOOL_ROUNDS + 1):
            logger.info(
                "%s | model request, round %d", self.label, round_number
            )

            response = self._create_completion(
                model=self.model,
                messages=working,
                tools=[SEARCH_WEB_TOOL],
                tool_choice="auto",
                max_tokens=MAX_RESPONSE_TOKENS,
            )

            choice = response.choices[0]
            message = getattr(choice, "message", None) or choice
            tool_calls = getattr(message, "tool_calls", None)

            if not tool_calls:
                answer = self._text_of(message)

                if answer:
                    return answer

                raise ProviderError(
                    f"{self.label} returned an empty answer "
                    f"(finish reason: {getattr(choice, 'finish_reason', None)})."
                )

            working.append(_message_to_dict(message))

            for tool_call in tool_calls:
                result = self._run_tool_call(tool_call)

                working.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        # Too many tool rounds: force a final answer without tools.
        final = self._create_completion(
            model=self.model,
            messages=working,
            tools=[SEARCH_WEB_TOOL],
            tool_choice="none",
            max_tokens=MAX_RESPONSE_TOKENS,
        )

        final_choice = final.choices[0]
        answer = self._text_of(getattr(final_choice, "message", None) or final_choice)

        if not answer:
            raise ProviderError(
                f"{self.label} did not produce a final answer. Try rephrasing."
            )

        return answer
