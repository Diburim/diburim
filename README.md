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

## Custom domain (`diburim.org`) via Cloudflare

The repo includes a root **`CNAME`** file (`diburim.org`) so GitHub Pages can serve the site on your domain (not only `diburim.github.io`).

### 1. GitHub

1. Repo **Settings → Pages**.
2. Under **Custom domain**, enter **`diburim.org`**, save, and wait for DNS check (can take minutes to a day).
3. When available, enable **Enforce HTTPS**.

If GitHub reports conflicting DNS, finish Cloudflare step 2 first, then retry.

### 2. Cloudflare DNS

Add records for the zone **diburim.org** (nameservers must be Cloudflare’s).

**Apex (`diburim.org`)** — use either:

| Type | Name | Content | Proxy |
| --- | --- | --- | --- |
| A | `@` | `185.199.108.153` | DNS only (grey cloud) or proxied |
| A | `@` | `185.199.109.153` | same |
| A | `@` | `185.199.110.153` | same |
| A | `@` | `185.199.111.153` | same |

Or a single **CNAME** `@` → **`diburim.github.io`** if Cloudflare CNAME flattening is enabled on your plan.

**`www` (optional but recommended):**

| Type | Name | Content | Proxy |
| --- | --- | --- | --- |
| CNAME | `www` | `diburim.github.io` | same |

Use a **Redirect rule** in Cloudflare so `www.diburim.org` → `https://diburim.org` (301), if you want one canonical host.

### 3. Cloudflare SSL and proxy (important for GitHub)

- **SSL/TLS** → **Overview**: start with **Full**; after GitHub shows a valid certificate, you can use **Full (strict)**.
- Do not use **Flexible** only with GitHub Pages (can cause redirect loops).
- While GitHub reports **DNS check** or **`www` InvalidDNSError**, set every GitHub record to **DNS only** (grey cloud). Proxied records hide the apex **A** answers and the **www** **CNAME** to `diburim.github.io`, so GitHub cannot verify the domain.
- After **Enforce HTTPS** works, you may turn proxy back on for `diburim.org` if you want Cloudflare in front.

### 4. Runtime config

`js/config.js` sets **`siteUrl`** to `https://diburim.org` for future canonical/share use.

After DNS and HTTPS work, the live site should be **https://diburim.org/** (library and pieces at the domain root, not `/diburim/`).

## Assets

- Logo: `assets/logo-diburim.jpg`
- Portrait: `assets/rabbi-binyamin-goldberg.jpg`
- Background: `assets/parchment-background.jpg` (fixed in CSS)
