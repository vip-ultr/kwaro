"""kwaro providers: factory from config."""
from __future__ import annotations

import os

from ..config import Config
from .base import Provider
from .openai_compat import OpenAICompat

# Well-known OpenAI-compatible hosts (base URL used when provider name matches).
_HOST_BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "together": "https://api.together.xyz/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "ollama": "http://localhost:11434/v1",
}

# Default model per known host (Groq/OpenAI ids differ from Ollama's).
_MODEL_DEFAULTS = {
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o-mini",
    "openrouter": "openai/gpt-4o-mini",
    "ollama": "qwen2.5-coder:14b",
}


def _resolve(provider: str, base_url: str, api_key: str, model: str) -> Provider:
    """Pick base_url/model/key for known hosts; fall back to what config says."""
    p = (provider or "ollama").lower()
    # Config seeds the Ollama localhost default, so only override when the user did
    # not set a real base_url (empty or still the Ollama default).
    if p in _HOST_BASE_URLS and (not base_url or base_url == _HOST_BASE_URLS["ollama"]):
        base_url = _HOST_BASE_URLS[p]
    if not model:
        model = _MODEL_DEFAULTS.get(p, "qwen2.5-coder:14b")
    # Groq/OpenAI/etc read their key from the environment when not in config.
    if not api_key:
        env_map = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "together": "TOGETHER_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env = env_map.get(p)
        if env:
            api_key = os.environ.get(env, "")
    if not base_url:
        base_url = _HOST_BASE_URLS["ollama"]
    return OpenAICompat(base_url=base_url, api_key=api_key, model=model)


def from_config(cfg: Config) -> Provider:
    """Build a Provider from a Config. Ollama and any OpenAI-compatible host use
    the same adapter; Anthropic is selected by provider name. Known hosts
    (groq, openai, openrouter, together, deepseek) get their base URL + API key
    from the environment automatically, so BYOK is one env var, no pull needed."""
    if cfg.provider == "anthropic":
        from .anthropic import Anthropic
        return Anthropic(api_key=cfg.api_key, model=cfg.model)
    return _resolve(cfg.provider, cfg.base_url, cfg.api_key, cfg.model)
