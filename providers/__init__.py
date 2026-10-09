from config import PROVIDERS, get_api_key
from providers.base import BaseProvider, ProviderError


def create_provider(name: str) -> BaseProvider:
    """Build the provider object for `name` ('huggingface', 'groq', 'gemini')."""
    if name not in PROVIDERS:
        raise ProviderError(f"Unknown provider: {name}")

    if not get_api_key(name):
        env_name = PROVIDERS[name]["api_key_env"]
        raise ProviderError(f"{env_name} is missing. Add it to your .env file.")

    if name == "huggingface":
        from providers.huggingface_provider import HuggingFaceProvider

        return HuggingFaceProvider()

    from providers.openai_compatible import OpenAICompatibleProvider

    return OpenAICompatibleProvider(name)


__all__ = ["create_provider", "BaseProvider", "ProviderError"]
