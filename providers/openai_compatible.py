"""
Groq and Google Gemini both expose an OpenAI-compatible API, so one
class serves both. Only the base URL, key and model differ.
"""

from typing import Any

from config import PROVIDERS, get_api_key
from providers.base import BaseProvider, ProviderError


class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, name: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ProviderError(
                "The 'openai' package is missing. "
                "Run: pip install -r requirements.txt"
            ) from error

        settings = PROVIDERS[name]

        self.name = name
        self.label = settings["label"]
        self.model = settings["model"]

        self.client = OpenAI(
            api_key=get_api_key(name),
            base_url=settings["base_url"],
            timeout=60,
            max_retries=0,  # retries are handled in BaseProvider
        )

    def _create(self, **kwargs: Any):
        return self.client.chat.completions.create(**kwargs)
