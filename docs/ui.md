# kwaro - UI

kwaro ships two interfaces on one engine. Both read the same SQLite store.

## Brand

Locked palette and logo in `docs/brand.md`. Sharp edges, dark canvas, single
electric-lime (`#C6F432`) accent. Logo: `assets/logo.svg` (aperture chevron).

## Terminal (primary)

- `kwaro chat` - interactive Hermes-style loop. Type requests, the engine runs
  steps and streams results. Works with no model configured (rule-based
  explanations) and upgrades to model-driven when a provider is set.
- `kwaro scan <path|url>` - one-shot scan, prints ranked findings.

## Browser (optional extra: `pip install kwaro[serve]`)

- `kwaro serve` - FastAPI app serving a single static bundle (HTML/CSS/JS) at
  `127.0.0.1`. No React/Node build step in v1. WebSocket streams agent activity.
- Layout: dashboard-first shell (projects/scans/findings) with chat as the main
  working panel. Finding cards: severity pill, file + line, vulnerable snippet,
  plain-language "why," suggested fix, PoC/test link.

## UI principles

- Not a generic 2025 chat clone. App shell, not a bare chatbot.
- Findings as cards, not text dumps.
- Live agent activity (clone, analyze N files, prove candidate) for trust.
- Typography: grotesk for UI, monospace for code. Hard edges, micro-transitions.
- Localhost-only by design (no auth needed); user runs it on their own machine.

## Build approach (v1)

Single static bundle, hand-written CSS (or Tailwind via CDN), vanilla JS or a
tiny reactivity helper. Served by the Python app. No separate frontend framework
required for v1.
