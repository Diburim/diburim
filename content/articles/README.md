# Article content (Layer 3)

Only Rabbi Goldberg's approved material belongs here. Coding agents must not author these files.

## Recommended format (Markdown + frontmatter)

```markdown
---
id: the-years-of-sarah
title: The Years of Sarah
parsha: Chayei Sara
hebrewTitle: null
date: 2026-11-07
status: published
audio: null
---

[Approved HTML or Markdown body — supplied by author workflow]
```

## Current loader

The site loads optional companion JSON at `content/articles/{id}.json`:

```json
{
  "body": null,
  "bodyFormat": "html"
}
```

When `body` is null, the piece page shows `[CONTENT PENDING]`.

Register the piece in `data/catalog.json` with metadata only (no invented `excerpt`).

## Bulk import from `.docx`

Author `.docx` files can be staged under `_import/Diburim-writings/Diburim/` (not committed; see `.gitignore`), then:

```bash
python scripts/import_docx.py
```

This writes `content/articles/{id}.json` (HTML body, unchanged prose) and rebuilds `data/catalog.json`. Duplicate filenames are deduplicated by preferring `_Full_Diburim`, `_Diburim`, and longer editions. See `scripts/import_report.json` for what was kept vs skipped.

Then apply short URLs, Hebcal Shabbat dates, and refresh the gap report:

```bash
python scripts/fetch_parsha_calendar.py
python scripts/migrate_catalog.py
```

Shabbat dates come from `data/parsha-calendar.json` (Hebcal; default NYC Diaspora). Change `geonameid` in `fetch_parsha_calendar.py` and re-run if you adopt another city. Coverage gaps are listed in `scripts/PARSHA_GAPS.md`.

## Parsha print PDF

The **Print / save PDF** button opens the file named in `content/articles/{id}.json`, not a reformatted HTML page:

```json
{
  "pdf": "assets/parsha/toldot.pdf",
  "body": "…",
  "bodyFormat": "html"
}
```

Stage a file from your machine:

```bash
python scripts/import_parsha_pdf.py toldot /path/to/Toldot.pdf --apply
```

Commit `assets/parsha/toldot.pdf` and the updated JSON so GitHub Pages can serve it.

## Halacha study guides (PDF)

```bash
python scripts/import_study_guides.py path/to/guide1.pdf path/to/guide2.pdf
```

Copies PDFs to `assets/study-guides/`, registers `kind: "study-guide"` pieces in `data/catalog.json`, and sets `content/articles/{id}.json` with a `pdf` path (no HTML body unless added later). Titles come from PDF metadata.
