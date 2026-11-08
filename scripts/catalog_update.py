#!/usr/bin/env python3
"""
Sync catalog + article JSON from on-disk assets (study guides, audio, weekly Torah).

Run after uploading files via GitHub or locally:
  python scripts/catalog_update.py

Also triggered manually by the GitHub Action "Catalog Update".

Weekly Torah: new editions can include a ``catalog`` object inside
``content/articles/{id}.json`` with approved metadata (title required).
The agent does not invent titles or Torah text.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"
CALENDAR_PATH = ROOT / "data" / "parsha-calendar.json"
ARTICLES_DIR = ROOT / "content" / "articles"
REPORT_PATH = ROOT / "scripts" / "catalog_update_report.json"

CYCLE_START = "2025-10-01"

sys.path.insert(0, str(ROOT / "scripts"))
from import_audio import sync_audio_from_assets  # noqa: E402
from import_study_guides import ASSET_DIR, sync_from_assets  # noqa: E402

STUDY_GUIDE_PREFIX = "hilchos-shabbos-"


def load_parsha_dates() -> tuple[dict[str, str], dict[str, str]]:
    if not CALENDAR_PATH.is_file():
        return {}, {}
    cal = json.loads(CALENDAR_PATH.read_text(encoding="utf-8"))
    all_dates: dict[str, list[str]] = {}
    for row in cal.get("readings", []):
        d = row["date"]
        for p in row.get("parshas", []):
            all_dates.setdefault(p, []).append(d)

    parsha_to_date: dict[str, str] = {}
    for p, dates in all_dates.items():
        dates = sorted(set(dates))
        in_window = [d for d in dates if CYCLE_START <= d <= "2026-12-31"]
        if not in_window:
            continue
        y2026 = [d for d in in_window if d.startswith("2026")]
        parsha_to_date[p] = y2026[-1] if y2026 else in_window[-1]

    parsha_to_display: dict[str, str] = {}
    for p, d in parsha_to_date.items():
        dt = datetime.strptime(d, "%Y-%m-%d")
        parsha_to_display[p] = dt.strftime("%B %d, %Y").replace(" 0", " ")
    return parsha_to_date, parsha_to_display


def attach_parsha_dates(pieces: list[dict]) -> list[str]:
    parsha_dates, parsha_display = load_parsha_dates()
    if not parsha_dates:
        return []
    touched: list[str] = []
    for piece in pieces:
        if not piece.get("parsha") or piece.get("date"):
            continue
        if piece.get("kind") not in (None, "parsha", "essay"):
            continue
        parsha = piece["parsha"]
        d = parsha_dates.get(parsha)
        if not d and parsha == "Balak":
            d = parsha_dates.get("Chukat")
        if not d and parsha == "Chukat":
            d = parsha_dates.get("Chukat") or parsha_dates.get("Balak")
        if not d and parsha == "Vayelech":
            d = parsha_dates.get("Nitzavim")
        if not d:
            continue
        piece["date"] = d
        piece["dateDisplay"] = parsha_display.get(parsha, d)
        touched.append(piece["id"])
    return touched


def register_weekly_from_articles(pieces: list[dict]) -> tuple[list[dict], list[str], list[str]]:
    """Add catalog rows from article ``catalog`` sidecars; report orphans."""
    by_id = {p["id"]: p for p in pieces}
    created: list[str] = []
    orphans: list[str] = []

    for path in sorted(ARTICLES_DIR.glob("*.json")):
        pid = path.stem
        if pid.startswith(STUDY_GUIDE_PREFIX):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        sidecar = data.get("catalog")
        if pid in by_id:
            continue
        if not isinstance(sidecar, dict):
            if data.get("body") or data.get("pdf"):
                orphans.append(pid)
            continue
        title = sidecar.get("title")
        if not title or not str(title).strip():
            orphans.append(pid)
            print(f"  skip {pid}: catalog sidecar missing title")
            continue
        entry = dict(sidecar)
        entry["id"] = pid
        pieces.append(entry)
        by_id[pid] = entry
        created.append(pid)
        print(f"  new catalog from article sidecar: {pid}")

    catalog_ids = set(by_id)
    missing_articles = sorted(i for i in catalog_ids if not (ARTICLES_DIR / f"{i}.json").is_file())
    return pieces, created, orphans + [f"catalog-missing-article:{i}" for i in missing_articles]


def sync_weekly() -> dict:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    pieces, created, warnings = register_weekly_from_articles(pieces)
    dates = attach_parsha_dates(pieces)
    changed = bool(created or dates)
    if changed:
        catalog["pieces"] = pieces
        CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Weekly sync: {len(created)} new piece(s), {len(dates)} date(s) filled")
    if warnings:
        print(f"  review: {len(warnings)} item(s) (orphan articles or missing JSON)")
    return {"created": created, "datesFilled": dates, "warnings": warnings}


def sync_study_guides() -> dict:
    if not ASSET_DIR.is_dir() or not list(ASSET_DIR.glob("siman-*.pdf")):
        return {"ran": False, "count": 0}
    ran = sync_from_assets(allow_empty=True)
    count = len(list(ASSET_DIR.glob("siman-*.pdf")))
    return {"ran": ran, "count": count}


def main() -> None:
    report = {
        "studyGuides": sync_study_guides(),
        "audio": sync_audio_from_assets(),
        "weekly": sync_weekly(),
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
