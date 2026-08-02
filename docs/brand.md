# kwaro Brand Palette

Locked brand colors for kwaro. Sharp edges, deep dark canvas, one confident accent.
Use these exact values across the logo, web UI, docs, and marketing.

## Core

| Token      | Hex       | Use                                  |
|------------|-----------|--------------------------------------|
| ink        | `#0B0D10` | Primary mark, headings, near-black    |
| surface    | `#0E1116` | App background (deep charcoal)        |
| surface-2  | `#161B22` | Raised panels, cards                 |
| border     | `#232A33` | Subtle separators, input borders     |
| muted      | `#8B98A5` | Secondary text, info severity        |

## Accent

| Token      | Hex       | Use                                  |
|------------|-----------|--------------------------------------|
| signal     | `#C6F432` | Primary accent, CTAs, active states  |

> Accent = Electric Lime. Pops on dark, reads as "scanning / active."

## Severity scale (findings)

| Severity   | Hex       |
|------------|-----------|
| critical   | `#FF4D4D` |
| high       | `#FF9F1C` |
| medium     | `#FFD60A` |
| low        | `#4CC9F0` |
| info       | `#8B98A5` |

## Logo

- `assets/logo.svg` — K with sharp bug antenna, single fill `ink #0B0D10`, no curves.
- All edges hard/angular (90deg and 45deg). No round caps, no gradients.
- Recolor by changing the single `fill` on the `<g>`.
