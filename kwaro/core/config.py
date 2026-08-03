"""kwaro core: config (load/save ~/.kwaro/config.toml, zero runtime deps).

A minimal TOML reader/writer for the flat [provider] table kwaro uses. Avoids
tomllib (3.11+) so we stay dependency-free on Python 3.10. Only handles the
simple key = "value" / key = 123 forms we write ourselves.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".kwaro", "config.toml")


@dataclass
class Config:
    provider: str = "ollama"
    base_url: str = "http://localhost:11434/v1"
    api_key: str = ""
    model: str = "qwen2.5-coder:14b"
    raw: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str = CONFIG_PATH) -> "Config":
        if not os.path.exists(path):
            return cls()
        data: Dict[str, str] = {}
        section = ""
        with open(path, "r", errors="ignore") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1].strip()
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if section:
                        key = f"{section}.{key}"
                    data[key] = val
        return cls(
            provider=data.get("provider.name", "ollama"),
            base_url=data.get("provider.base_url", "http://localhost:11434/v1"),
            api_key=data.get("provider.api_key", ""),
            model=data.get("provider.model", "qwen2.5-coder:14b"),
            raw=data,
        )

    def save(self, path: str = CONFIG_PATH) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write("[provider]\n")
            fh.write(f'name = "{self.provider}"\n')
            fh.write(f'base_url = "{self.base_url}"\n')
            fh.write(f'api_key = "{self.api_key}"\n')
            fh.write(f'model = "{self.model}"\n')

    @property
    def is_local(self) -> bool:
        return self.provider == "ollama" or "localhost" in self.base_url

    @property
    def needs_key(self) -> bool:
        return bool(self.api_key) or not self.is_local
