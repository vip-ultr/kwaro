"""kwaro providers: base interface + response types.

A Provider turns a message list + optional tool schemas into a Response. The
loop (chat/agent.py) drives this. Pure stdlib, zero deps. Tool use follows the
OpenAI Chat Completions tool-call shape, which Ollama and most hosts speak.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class Message:
    role: str          # system | user | assistant | tool
    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""


@dataclass
class Response:
    message: Message
    raw: dict = field(default_factory=dict)


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict  # JSON-schema-like dict


class ProviderError(Exception):
    """Raised when a provider call fails (HTTP error, connection error, bad response).

    Carries the provider's raw error body when available, so the CLI can show the
    real cause (e.g. 'model not found') instead of a traceback.
    """
    def __init__(self, message: str, status: Optional[int] = None, body: str = "") -> None:
        self.status = status
        self.body = body
        super().__init__(message)


class Provider(ABC):
    @abstractmethod
    def complete(self, messages: List[Message], tools: Optional[List[ToolSpec]] = None) -> Response:
        ...

    @property
    @abstractmethod
    def label(self) -> str:
        ...
