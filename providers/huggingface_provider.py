from typing import Any

from config import PROVIDERS, get_api_key
from providers.base import BaseProvider, ProviderError


class HuggingFaceProvider(BaseProvider):
    name = "huggingface"
    label = PROVIDERS["huggingface"]["label"]

    def __init__(self) -> None:
        try:
            from huggingface_hub import InferenceClient
        except ImportError as error:
            raise ProviderError(
                "The 'huggingface_hub' package is missing. "
                "Run: pip install -r requirements.txt"
            ) from error

        self.model = PROVIDERS["huggingface"]["model"]
        self.client = InferenceClient(
            provider="auto",
            api_key=get_api_key("huggingface"),
        )

    def _create(self, **kwargs: Any):
        return self.client.chat.completions.create(**kwargs)
