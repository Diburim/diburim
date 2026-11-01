# Content audit (2026-11-01)

This documents AI-generated or hard-coded substantive content removed or relocated during the content-integrity refactor.

| Location | What was removed / changed | Why it appeared generated | New source of truth |
| --- | --- | --- | --- |
| `js/catalog.js` | Entire fake library (~10 essays, bodies, Hebrew, sources) | Agent-authored “launch drafts” | `data/catalog.json` + `content/articles/*` (user-supplied only) |
| `js/catalog.js` | `DIBURIM_PROJECTS` long bodies | Invented project copy | `data/projects.json` (title/structure only; `summary`/`body` null until supplied) |
| `index.html` | Tagline, hero intro, series lede, project blurbs, keeper lede, values grid | Editorial voice not approved | `data/site.json` (mission only) + render from data |
| `index.html` | Meta / JSON-LD “Words of Torah…” | SEO tagline invented | `data/site.json` → applied by `js/bootstrap.js` |
| `js/site.js` | “The recording will be added here” | Soft invented copy | `data/ui.json` → `audioUnavailable` |
| `js/config.js` | Calendar entries linking to fake pieces | Inferred schedule copy | Removed; calendar when supplied in data |
| `about.html` | Biographical paragraphs | Agent voice | `[CONTENT PENDING]` or user-supplied `content/about.json` later |
| `js/shulchan.js` | Sample OC 1 English (if not sourced) | Marked reference; do not extend without supplied text | External project + future approved translation files |

**Principle applied:** questionable prose was deleted, not replaced with new generated text.
