# Diburim

Torah library site for **Rabbi Binyamin Goldberg** — static GitHub Pages.

**Read `AGENTS.md` before editing content or copy.**

## Three layers

| Layer | Path | Who writes it |
| --- | --- | --- |
| Design | HTML, CSS, `js/site.js` renderers | Coding agent (implementation) |
| Site configuration | `data/site.json`, `data/ui.json`, `data/projects.json`, `js/config.js` | Rabbi / editor, only when instructed |
| Torah content | `data/catalog.json`, `content/articles/*` | Rabbi Goldberg / Rav Comp workflow — **not** the coding agent |

## Adding a published piece

1. Add metadata to `data/catalog.json` (no invented `excerpt` unless approved).
2. Set `"thisWeekId"` when it is the weekly feature.
3. Add `content/articles/{id}.json` with `{ "body": "..." }` or `null` until ready.

See `content/articles/README.md`.

## Approved site copy

`data/site.json` — currently only `mission`, `metaDescription`, `author`.

## Local preview

The server **must** run from this project root (the folder that contains `data/catalog.json`).

**Git Bash / macOS / Linux:**

```bash
cd /path/to/Diburim
python -m http.server 8765
```

**PowerShell (Windows):**

```powershell
.\scripts\serve-local.ps1
```

Open http://127.0.0.1:8765/library.html — the subtitle should show **(64 published pieces)** when the catalog loaded.

Sanity check: http://127.0.0.1:8765/data/catalog.json should list `"pieces": [ ... ]`, not an empty array.

## Assets

- Logo: `assets/logo-diburim.jpg`
- Portrait: `assets/rabbi-binyamin-goldberg.jpg`
- Background: `assets/parchment-background.jpg` (fixed in CSS)
