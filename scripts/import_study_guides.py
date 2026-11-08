#!/usr/bin/env python3
"""
Import Hilchos Shabbos study-guide PDFs into assets/ + catalog + content/articles/*.json.
Titles from PDF metadata only; no invented halacha text.

Import new files from disk or Downloads:
  python scripts/import_study_guides.py path/to/Hilchos_Shabbos_*_Siman_252.pdf

Register PDFs you already placed under assets/ (e.g. uploaded via GitHub UI):
  python scripts/import_study_guides.py --sync-assets

The live site only reads data/catalog.json — PDFs in assets/ alone are not auto-detected until
sync or import runs. Accepts siman-NNN.pdf or Hilchos_Shabbos_*_-_Siman_NNN.pdf in assets/.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "study-guides" / "hilchos-shabbos"
ARTICLES = ROOT / "content" / "articles"
CATALOG = ROOT / "data" / "catalog.json"

DEFAULT_GLOB = "Hilchos_Shabbos_*_-_Siman_*.pdf"
ASSET_PDF_RE = re.compile(r"^siman-(\d+)\.pdf$", re.I)


def siman_from_name(name: str) -> int:
    m = re.search(r"Siman_(\d+)", name, re.I)
    if m:
        return int(m.group(1))
    m = ASSET_PDF_RE.match(name)
    if m:
        return int(m.group(1))
    raise ValueError(f"No siman in filename: {name}")


def title_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    if reader.metadata and reader.metadata.get("/Title"):
        return str(reader.metadata["/Title"]).strip()
    return f"Hilchos Shabbos — Siman {siman_from_name(path.name)}"


def hebrew_subtitle_from_pdf(path: Path) -> str | None:
    try:
        reader = PdfReader(str(path))
        text = (reader.pages[0].extract_text() or "") if reader.pages else ""
        for line in text.splitlines():
            if "סימן" in line and "אורח" in line:
                return line.strip()
    except Exception:
        return None
    return None


def piece_id(siman: int) -> str:
    return f"hilchos-shabbos-{siman}"


def make_catalog_entry(siman: int, title: str, hebrew: str | None) -> dict:
    entry: dict = {
        "id": piece_id(siman),
        "title": title,
        "kind": "study-guide",
        "series": "Hilchos Shabbos",
        "project": "halachah",
        "sefer": "Halachah",
        "siman": siman,
        "chelek": "OC",
        "categories": ["halacha", "torah"],
        "topics": ["Hilchos Shabbos", "Shabbos", "Orach Chaim"],
    }
    if hebrew:
        entry["hebrewTitle"] = hebrew
    return entry


def write_article_json(pid: str, rel_pdf: str) -> None:
    article_path = ARTICLES / f"{pid}.json"
    article: dict = {}
    if article_path.is_file():
        article = json.loads(article_path.read_text(encoding="utf-8"))
    article["pdf"] = rel_pdf
    article.setdefault("bodyFormat", "html")
    article.setdefault("body", None)
    article_path.write_text(
        json.dumps(article, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def merge_piece(pieces: list[dict], entry: dict) -> tuple[list[dict], bool]:
    pid = entry["id"]
    for i, p in enumerate(pieces):
        if p.get("id") == pid:
            pieces[i] = entry
            return pieces, False
    pieces.append(entry)
    return pieces, True


def wire_prev_next(pieces: list[dict]) -> None:
    hs = sorted(
        [p for p in pieces if p.get("id", "").startswith("hilchos-shabbos-")],
        key=lambda p: int(p.get("siman") or 0),
    )
    for i, p in enumerate(hs):
        if i:
            p["prevId"] = hs[i - 1]["id"]
        else:
            p.pop("prevId", None)
        if i < len(hs) - 1:
            p["nextId"] = hs[i + 1]["id"]
        else:
            p.pop("nextId", None)


def register_pdf(pdf_path: Path, pieces: list[dict]) -> tuple[list[dict], str, bool]:
    """Ensure catalog + article json exist for an on-disk PDF under assets/."""
    siman = siman_from_name(pdf_path.name)
    pid = piece_id(siman)
    rel_pdf = pdf_path.relative_to(ROOT).as_posix()
    title = title_from_pdf(pdf_path)
    he = hebrew_subtitle_from_pdf(pdf_path)
    entry = make_catalog_entry(siman, title, he)
    write_article_json(pid, rel_pdf)
    pieces, created = merge_piece(pieces, entry)
    return pieces, pid, created


def import_sources(sources: list[Path]) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES.mkdir(parents=True, exist_ok=True)

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    created: list[str] = []
    updated: list[str] = []

    for src in sorted(sources, key=lambda p: siman_from_name(p.name)):
        siman = siman_from_name(src.name)
        dest = ASSET_DIR / f"siman-{siman}.pdf"
        shutil.copy2(src, dest)
        pieces, pid, is_new = register_pdf(dest, pieces)
        (created if is_new else updated).append(pid)

    wire_prev_next(pieces)
    catalog["pieces"] = pieces
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(sources)} PDF(s) into {ASSET_DIR.relative_to(ROOT)}")
    if created:
        print(f"  new catalog: {', '.join(created)}")
    if updated:
        print(f"  updated: {', '.join(updated)}")


def collect_asset_pdfs() -> list[Path]:
    """All study-guide PDFs under assets/, one path per siman (prefer siman-NNN.pdf)."""
    by_siman: dict[int, Path] = {}
    patterns = ("siman-*.pdf", DEFAULT_GLOB)

    def rank(p: Path) -> int:
        return 0 if ASSET_PDF_RE.match(p.name) else 1

    for pattern in patterns:
        for pdf in ASSET_DIR.glob(pattern):
            try:
                siman = siman_from_name(pdf.name)
            except ValueError:
                continue
            cur = by_siman.get(siman)
            if cur is None or rank(pdf) < rank(cur):
                by_siman[siman] = pdf
    return sorted(by_siman.values(), key=lambda p: siman_from_name(p.name))


def sync_from_assets(*, allow_empty: bool = False) -> bool:
    pdfs = collect_asset_pdfs()
    if not pdfs:
        if allow_empty:
            print(f"No Hilchos Shabbos PDFs in {ASSET_DIR.relative_to(ROOT)} (skipped)")
            return False
        raise SystemExit(f"No PDFs in {ASSET_DIR}. Add siman-NNN.pdf files, then re-run.")

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    created: list[str] = []
    updated: list[str] = []

    for pdf in pdfs:
        pieces, pid, is_new = register_pdf(pdf, pieces)
        (created if is_new else updated).append(pid)

    wire_prev_next(pieces)
    catalog["pieces"] = pieces
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(pdfs)} study guide(s) from {ASSET_DIR.relative_to(ROOT)}")
    if created:
        print(f"  new catalog: {', '.join(created)}")
    if updated:
        print(f"  refreshed: {', '.join(updated)}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdfs",
        nargs="*",
        help="Source PDF paths (Hilchos_Shabbos_*_Siman_NNN.pdf). Omit with --sync-assets.",
    )
    parser.add_argument(
        "--sync-assets",
        action="store_true",
        help="Scan assets/study-guides/hilchos-shabbos (*.pdf) and update catalog + articles",
    )
    args = parser.parse_args()

    if args.sync_assets:
        sync_from_assets()
        return

    sources: list[Path] = [Path(p) for p in args.pdfs]
    if not sources:
        downloads = Path.home() / "Downloads"
        sources = sorted(downloads.glob(DEFAULT_GLOB))
    if not sources:
        raise SystemExit(
            "No PDFs found. Pass paths, use --sync-assets after adding files to assets/, "
            "or place Hilchos_Shabbos_*_-_Siman_*.pdf in Downloads."
        )

    import_sources(sources)


if __name__ == "__main__":
    main()
