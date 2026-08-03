"""kwaro core: profile loader (TOML, zero-dep).

A profile pairs static rule ids with an optional triage prompt to tailor kwaro to
a domain. Built-in profiles live in this package; user profiles can override via
~/.kwaro/profiles/<name>.toml. See docs/profiles.md for the format.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Profile:
    name: str = "generic"
    description: str = "Generic scanning across all languages."
    cwe_focus: List[str] = field(default_factory=list)
    enable: List[str] = field(default_factory=list)  # empty = all analyzers
    rules: List[dict] = field(default_factory=list)
    system: str = ""

    @classmethod
    def load(cls, name: str, builtin_dir: Optional[str] = None) -> "Profile":
        if builtin_dir is None:
            builtin_dir = os.path.join(os.path.dirname(__file__), "profiles")
        candidates = [
            os.path.join(os.path.expanduser("~"), ".kwaro", "profiles", f"{name}.toml"),
            os.path.join(builtin_dir, f"{name}.toml"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return cls._from_toml(path, name)
        return cls(name=name)  # unknown name -> generic defaults

    @classmethod
    def _from_toml(cls, path: str, name: str) -> "Profile":
        data: dict = {}
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
                    data[f"{section}.{key.strip()}" if section else key.strip()] = val.strip()
        # minimal: we only need name/description/enable for Phase 3 wiring
        return cls(
            name=name,
            description=data.get("description", ""),
            enable=_split_list(data.get("enable", "")),
        )


def _split_list(s: str) -> List[str]:
    s = s.strip().strip("[]")
    if not s:
        return []
    return [x.strip().strip('"').strip("'") for x in s.split(",") if x.strip()]
