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

## Parsha print PDF (original Word layout)

The **on-screen essay** is HTML converted from `.docx` for reading and search. **Print / save PDF** opens a PDF exported from the same source Word file so typography matches what you authored—not the browser’s HTML print view.

```json
{
  "pdf": "assets/parsha/toldot.pdf",
  "printSource": "Dvar Torah for Parshas Toldos.docx",
  "body": "…",
  "bodyFormat": "html"
}
```

Regenerate PDFs from `_import/Diburim-writings/Diburim` (requires Microsoft Word on Windows, `pip install docx2pdf`):

```bash
python scripts/stage_parsha_print_pdfs.py              # dry run
python scripts/stage_parsha_print_pdfs.py --apply      # all catalog pieces
python scripts/stage_parsha_print_pdfs.py --apply --id toldot
```

Commit `assets/parsha/*.pdf` and the updated article JSON. To register one PDF manually: `scripts/import_parsha_pdf.py`.

## Halacha study guides (PDF)

```bash
python scripts/import_study_guides.py path/to/guide1.pdf path/to/guide2.pdf
```

Copies PDFs to `assets/study-guides/`, registers `kind: "study-guide"` pieces in `data/catalog.json`, and sets `content/articles/{id}.json` with a `pdf` path (no HTML body unless added later). Titles come from PDF metadata.
