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
  `127.0.0.1`. No React/Node build step in v1 (locked decision L11). WebSocket
  (via the `serve` extra's `websockets`) streams agent activity + chat.
- Layout: dashboard-first shell (Scans / Chat / Profiles / Settings) with the
  active scan detail as the main panel. Finding cards: severity pill, file + line,
  vulnerable snippet, plain-language "why," suggested fix, PoC/test link, and a
  "proven" badge shown only when a PoC was verified.

### Tech stack (locked, L11)

- **No React, no Node, no build step in v1.** This protects the zero-dependency
  promise; the CLI and UI share one Python process.
- **Server:** FastAPI (the `serve` extra only; not required for the CLI).
- **Markup:** hand-written semantic HTML.
- **Styling:** hand-written CSS using the locked palette: ink `#0B0D10` canvas,
  surface `#0E1116` / `#161B22` panels, border `#232A33`, muted `#8B98A5` text,
  lime `#C6F432` accent. Sharp corners (radius 0-2px), micro-transitions only.
- **Behavior:** vanilla JS with a tiny (~10-line) reactivity helper, or htmx/Alpine
  via CDN. Prefer the self-written helper to stay truly zero-dep. WebSocket for
  live activity + chat.
- **Typography:** grotesk UI stack (system-ui / Inter-like) and monospace for code
  (ui-monospace / SFMono). No external font CDN required.
- **Revisit React only if** the UI outgrows vanilla (chat + cards + live stream).
  Not in v1, and only if justified.

### How it looks (concrete)

- Dark, sharp, technical. A security console, not a chatbot. Not a generic 2025
  chat clone.
- **Shell:** top/left nav (Scans, Chat, Profiles, Settings). Main area switches
  between the scans list and the active scan detail.
- **Finding cards:** severity pill (critical red, high orange, medium yellow, low
  blue, info grey), title, a `proven` / `static` / `model` source tag, `file:line`,
  a one-line plain-language "why" generated from the model reading the code (not a
  CWE paste), and actions (View snippet, Prove, Fix, Ignore).
- **Activity rail:** stage labels only, no named agent personas (option A):
  `cloning repo...`, `analyzing 42 files (static)...`, `proving db.py:88... verified.`
- **Chat panel:** the working surface when open. Input + message stream; the agent
  reads only the opened workspace. Sharp bubbles, monospace code, lime accent on
  agent actions.
- **Empty states** are explicit and privacy-first: "No scans yet. Drop a repo path
  or URL. Your code stays on this machine."

## UI principles

- Not a generic 2025 chat clone. App shell, not a bare chatbot.
- Findings as cards, not text dumps.
- Live activity for trust (clone, analyze N files, prove candidate).
- Typography: grotesk for UI, monospace for code. Hard edges, micro-transitions.
- Localhost-only by design (no auth needed); user runs it on their own machine.

## Build approach (v1)

Single static bundle, hand-written CSS, vanilla JS + tiny helper. Served by the
Python app. No separate frontend framework required for v1.
