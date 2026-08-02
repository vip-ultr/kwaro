# kwaro - Providers (model access)

kwaro is free-first. The default model runs locally with no account and no cost.
Paid models are opt-in via a standard API.

## Default: local, free, offline

- **Ollama** at `http://localhost:11434/v1`.
- No API key. No internet. No cyber-safety blocks on security research.
- Recommended model: a code-capable model (e.g. `qwen2.5-coder`, `llama3.1`,
  `deepseek-coder`) pulled locally.

## Universal adapter: OpenAI-compatible API

Most model providers speak the OpenAI Chat Completions shape. One adapter covers:

| Provider     | base_url                          | api_key            |
|--------------|-----------------------------------|--------------------|
| Ollama       | `http://localhost:11434/v1`       | (none)             |
| Groq (free)  | `https://api.groq.com/openai/v1`  | groq key (free)    |
| OpenAI       | `https://api.openai.com/v1`       | openai key (paid)  |
| OpenRouter   | `https://openrouter.ai/api/v1`    | openrouter key     |
| Together     | `https://api.together.xyz/v1`     | together key       |
| DeepSeek     | `https://api.deepseek.com/v1`     | deepseek key       |
| llama.cpp    | `http://localhost:8080/v1`        | (none)             |

Config: `provider`, `base_url`, `api_key`, `model`.

## Secondary adapter: Anthropic

Claude users use a thin Anthropic adapter (different request/response format).
Same `complete(messages, tools)` interface.

## Config

`~/.kwaro/config.toml`, overridable by environment variables.

```toml
[provider]
name = "ollama"
base_url = "http://localhost:11434/v1"
api_key = ""
model = "qwen2.5-coder:7b"
```

Set once with `kwaro init`.

## Honesty note

Paid providers may refuse security-research prompts under their cyber-safety
policies. Local models do not. The free default is therefore both cheaper and
more reliable for vulnerability hunting. We state this plainly to users.
