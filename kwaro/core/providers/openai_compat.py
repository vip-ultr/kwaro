"""kwaro providers: OpenAI-compatible adapter (Ollama, Groq, OpenAI, OpenRouter...).

Speaks the OpenAI Chat Completions shape over stdlib http.client, so there is no
requests/urllib3 dependency. One class covers every OpenAI-compatible endpoint;
only base_url + api_key differ. Local Ollama needs no key.
"""
from __future__ import annotations

import json
import urllib.request
from typing import List, Optional

from .base import Message, Provider, Response, ToolCall, ToolSpec, ProviderError


def _msg_to_dict(m: Message) -> dict:
    d = {"role": m.role, "content": m.content}
    if m.role == "assistant" and m.tool_calls:
        d["tool_calls"] = [
            {
                "id": f"call_{i}",
                "type": "function",
                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
            }
            for i, tc in enumerate(m.tool_calls)
        ]
    if m.role == "tool":
        d["tool_call_id"] = m.tool_call_id
    return d


def _resp_from_dict(data: dict) -> Response:
    choice = data["choices"][0]["message"]
    content = choice.get("content", "") or ""
    tool_calls = []
    for tc in choice.get("tool_calls", []) or []:
        fn = tc.get("function", {})
        args = fn.get("arguments", "{}")
        try:
            arguments = json.loads(args) if isinstance(args, str) else args
        except json.JSONDecodeError:
            arguments = {}
        tool_calls.append(ToolCall(name=fn.get("name", ""), arguments=arguments))
    return Response(message=Message(role="assistant", content=content, tool_calls=tool_calls), raw=data)


class OpenAICompat(Provider):
    def __init__(self, base_url: str, api_key: str = "", model: str = "qwen2.5-coder:14b") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    @property
    def label(self) -> str:
        return f"openai-compat:{self.model}@{self.base_url}"

    def complete(self, messages: List[Message], tools: Optional[List[ToolSpec]] = None) -> Response:
        payload = {
            "model": self.model,
            "messages": [_msg_to_dict(m) for m in messages],
            "stream": False,
        }
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]
            payload["tool_choice"] = "auto"
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return _resp_from_dict(json.loads(resp.read().decode()))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode(errors="ignore")
            except Exception:
                pass
            hint = ""
            if e.code == 404 and "not found" in body.lower():
                hint = (f" Model '{self.model}' is not available at this endpoint. "
                        f"If this is Ollama, run: ollama pull {self.model}")
            elif e.code == 404:
                hint = (" Endpoint not found. For Ollama, the base URL must end in '/v1' "
                        "(e.g. http://localhost:11434/v1).")
            raise ProviderError(
                f"provider {self.label} returned HTTP {e.code}.{hint}",
                status=e.code, body=body,
            ) from e
        except urllib.error.URLError as e:
            raise ProviderError(
                f"provider {self.label} connection failed: {e.reason}. "
                f"Is the server running at {self.base_url}?"
            ) from e
