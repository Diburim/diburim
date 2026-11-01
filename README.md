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

## Push to GitHub (`Diburim/diburim`)

The repo remote is `https://github.com/Diburim/diburim.git`. Git must authenticate as a **GitHub user that has write access** to that repository (your Diburim org account tied to `rabbigoldbergdiburim@gmail.com`), not a personal account without access.

1. Sign in at [github.com](https://github.com) as the user/org owner for **Diburim**.
2. Create a **Personal Access Token** (Settings → Developer settings → Fine-grained or classic token with **Contents: Read and write** on `diburim`).
3. From this folder, push (Git Credential Manager will ask once):

```powershell
cd C:\Users\binya\Documents\Diburim
git push -u origin main
```

When prompted: username = your GitHub username for the Diburim account; password = **the token** (not your Gmail password).

If Git still uses the wrong account, remove the saved entry: Windows **Credential Manager** → **Windows Credentials** → delete `git:https://github.com`, then push again.

After push, enable **GitHub Pages** → Build and deployment → **GitHub Actions** (workflow already in `.github/workflows/pages.yml`).

## Assets

- Logo: `assets/logo-diburim.jpg`
- Portrait: `assets/rabbi-binyamin-goldberg.jpg`
- Background: `assets/parchment-background.jpg` (fixed in CSS)
