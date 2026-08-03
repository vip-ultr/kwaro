"""Phase 2 tests: config, provider factory, and chat loop (no network needed)."""
import os
import sys

import pytest

from kwaro.core.config import Config
from kwaro.core.providers import from_config
from kwaro.core.providers.base import Message, Provider, Response, ToolCall, ToolSpec
from kwaro.chat.agent import ChatAgent


def test_config_roundtrip(tmp_path):
    p = tmp_path / "config.toml"
    cfg = Config(provider="ollama", base_url="http://localhost:11434/v1",
                 api_key="", model="qwen2.5-coder:14b")
    cfg.save(str(p))
    loaded = Config.load(str(p))
    assert loaded.provider == "ollama"
    assert loaded.base_url == "http://localhost:11434/v1"
    assert loaded.model == "qwen2.5-coder:14b"
    assert loaded.is_local is True


def test_config_load_missing_returns_default():
    cfg = Config.load("/nonexistent/path/config.toml")
    assert cfg.provider == "ollama"
    assert cfg.is_local is True


def test_factory_builds_openai_compat_for_ollama():
    cfg = Config(provider="ollama", base_url="http://localhost:11434/v1", api_key="", model="x")
    prov = from_config(cfg)
    assert prov.label.startswith("openai-compat:")


class FakeProvider(Provider):
    """Returns one tool call then a final answer, deterministically."""
    def __init__(self):
        self.calls = 0

    @property
    def label(self):
        return "fake"

    def complete(self, messages, tools=None):
        self.calls += 1
        if self.calls == 1:
            return Response(message=Message(
                role="assistant", content="", tool_calls=[ToolCall("run_analyzer", {})]))
        return Response(message=Message(role="assistant", content="Found 2 issues."))


def test_chat_loop_dispatches_tool_then_stops():
    agent = ChatAgent(FakeProvider(), "/tmp")
    seen = {}

    def run_analyzer(args):
        seen["ran"] = True
        return "1 high, 1 medium"

    agent.register(ToolSpec(
        name="run_analyzer", description="run", parameters={"type": "object"}), run_analyzer)
    out = agent.run("scan this")
    assert seen.get("ran") is True
    assert "Found 2 issues" in out
    assert len(agent.history) >= 3  # system, user, assistant(tool), tool, assistant(final)


def test_chat_loop_iteration_cap():
    class Chatty(FakeProvider):
        def complete(self, messages, tools=None):
            self.calls += 1
            return Response(message=Message(
                role="assistant", content="", tool_calls=[ToolCall("run_analyzer", {})]))

    agent = ChatAgent(Chatty(), "/tmp", cap=4)
    agent.register(ToolSpec(name="run_analyzer", description="run", parameters={"type": "object"}),
                   lambda a: "ok")
    out = agent.run("go")
    assert "iteration cap" in out
