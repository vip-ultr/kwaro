"""kwaro providers: Anthropic adapter (thin second adapter, different format).

Anthropic uses a distinct request/response shape (system is a top-level field,
tool_use blocks instead of tool_calls, stop_reason drives the loop). Same
complete(messages, tools) interface as the OpenAI-compatible adapter. Stdlib only.
"""
from __future__ import annotations

import json
import urllib.request
from typing import List, Optional

from .base import Message, Provider, Response, ToolCall, ToolSpec


def _msg_to_dict(m: Message) -> dict:
    return {"role": m.role, "content": m.content}


class Anthropic(Provider):
    API = "https://api.anthropic.com/v1/messages"
    VERSION = "2023-06-01"

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest") -> None:
        self.api_key = api_key
        self.model = model

    @property
    def label(self) -> str:
        return f"anthropic:{self.model}"

    def complete(self, messages: List[Message], tools: Optional[List[ToolSpec]] = None) -> Response:
        system = ""
        convo = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                convo.append(_msg_to_dict(m))
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "system": system,
            "messages": convo,
        }
        if tools:
            payload["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.parameters}
                for t in tools
            ]
        req = urllib.request.Request(
            self.API,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": self.VERSION,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        content = ""
        tool_calls = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append(ToolCall(name=block.get("name", ""), arguments=block.get("input", {})))
        return Response(message=Message(role="assistant", content=content, tool_calls=tool_calls), raw=data)
