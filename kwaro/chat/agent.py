"""kwaro chat: the interactive agent loop (terminal + tool use).

This is the harness from the agent-harness discussion: it assembles context,
calls the model, dispatches tool calls against a governed registry, and repeats
until the model returns no tool calls (stop condition) or an iteration cap hits.
Tools are anonymous, provider-attached steps (no named personas, per L14).

Tools available to the model:
  read_file    - read a file in the workspace
  run_analyzer - run the static analyzer on a path
  request_poc  - mark a finding for PoC generation (offline placeholder)
  done         - finish the session

Pure stdlib. Provider-agnostic: inject any Provider.
"""
from __future__ import annotations

import json
from typing import Callable, Dict, List, Optional

from ..core.providers.base import Message, Provider, ToolCall, ToolSpec
from ..core import verify


SYSTEM_PROMPT = (
    "You are kwaro, a local security scanner. You help the user find, prove, fix, "
    "and verify vulnerabilities in their code. Use tools to inspect the workspace. "
    "When you have enough to report, call the done tool with a short summary. "
    "Be precise. Do not claim a finding is proven unless you have evidence."
)


class ChatAgent:
    def __init__(self, provider: Provider, workspace_root: str, cap: int = 16) -> None:
        self.provider = provider
        self.workspace_root = workspace_root
        self.cap = cap
        self.tools: Dict[str, ToolSpec] = {}
        self.handlers: Dict[str, Callable[[dict], str]] = {}
        self.history: List[Message] = [Message(role="system", content=SYSTEM_PROMPT)]

    def register(self, spec: ToolSpec, handler: Callable[[dict], str]) -> None:
        self.tools[spec.name] = spec
        self.handlers[spec.name] = handler

    def _tool_specs(self) -> List[ToolSpec]:
        return list(self.tools.values())

    def run(self, user_input: str) -> str:
        """Run one user turn through the bounded loop. Returns the final summary."""
        self.history.append(Message(role="user", content=user_input))
        trace: List[str] = []
        for _ in range(self.cap):
            resp = self.provider.complete(self.history, self._tool_specs())
            assistant = resp.message
            self.history.append(assistant)
            if not assistant.tool_calls:
                # stop condition: model produced a final answer, no tool calls
                return assistant.content or "(no response)"
            for tc in assistant.tool_calls:
                result = self._dispatch(tc)
                trace.append(f"{tc.name}({tc.arguments}) -> {result[:80]}")
                self.history.append(Message(
                    role="tool", content=result, tool_call_id=f"call_{tc.name}"))
        return "Reached iteration cap without a final answer. Last actions:\n" + "\n".join(trace)

    def _dispatch(self, tc: ToolCall) -> str:
        handler = self.handlers.get(tc.name)
        if not handler:
            return f"error: unknown tool {tc.name}"
        try:
            return handler(tc.arguments)
        except Exception as e:  # governed: never let a tool crash the loop
            return f"error: {type(e).__name__}: {e}"
