"""kwaro providers: factory from config."""
from __future__ import annotations

from ..config import Config
from .base import Provider
from .openai_compat import OpenAICompat


def from_config(cfg: Config) -> Provider:
    """Build a Provider from a Config. Ollama and any OpenAI-compatible host use
    the same adapter; Anthropic is selected by provider name."""
    if cfg.provider == "anthropic":
        # imported lazily so Anthropic users are not forced to pull anything extra
        from .anthropic import Anthropic
        return Anthropic(api_key=cfg.api_key, model=cfg.model)
    # default: Ollama, Groq, OpenAI, OpenRouter, Together, DeepSeek, llama.cpp
    return OpenAICompat(base_url=cfg.base_url, api_key=cfg.api_key, model=cfg.model)
