"""
Central configuration for the assistant.

All secrets are read from the `.env` file (or real environment variables).
Nothing in this file should ever contain an API key.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)


def _env(name: str, default: str = "") -> str:
    """Read an env var; empty values fall back to the default."""
    return (os.getenv(name) or "").strip() or default


# ---------------------------------------------------------------
# Branding  (change APP_NAME here or in .env)
# ---------------------------------------------------------------
APP_NAME = _env("APP_NAME", "Nexora")
APP_TAGLINE = "Intelligent answers, backed by live web search."

# Optional avatar image URL or local path for the assistant.
AVATAR_URL = _env("AVATAR_URL") or None


# ---------------------------------------------------------------
# AI providers
# ---------------------------------------------------------------
# Add ANY ONE (or all) of these keys to `.env`. Providers that have
# a key will automatically appear in the app's sidebar.
PROVIDERS: dict[str, dict[str, str]] = {
    "huggingface": {
        "label": "Hugging Face",
        "api_key_env": "HF_TOKEN",
        "model": _env("HF_MODEL", "openai/gpt-oss-120b:cheapest"),
        "base_url": "",  # handled by the huggingface_hub client
        "key_url": "https://huggingface.co/settings/tokens",
    },
    "groq": {
        "label": "Groq",
        "api_key_env": "GROQ_API_KEY",
        "model": _env("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "base_url": "https://api.groq.com/openai/v1",
        "key_url": "https://console.groq.com/keys",
    },
    "gemini": {
        "label": "Google Gemini",
        "api_key_env": "GEMINI_API_KEY",
        "model": _env("GEMINI_MODEL", "gemini-2.5-flash"),
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_url": "https://aistudio.google.com/apikey",
    },
}


def get_api_key(provider: str) -> str:
    """Return the API key for a provider ('' if missing)."""
    return _env(PROVIDERS[provider]["api_key_env"])


def available_providers() -> list[str]:
    """Providers that currently have an API key configured."""
    return [name for name in PROVIDERS if get_api_key(name)]


def default_provider() -> str | None:
    """Pick DEFAULT_PROVIDER from .env, else the first configured one."""
    available = available_providers()
    preferred = _env("DEFAULT_PROVIDER").lower()

    if preferred in available:
        return preferred

    return available[0] if available else None
