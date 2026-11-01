#!/usr/bin/env python3
"""
Import Hilchos Shabbos study-guide PDFs into assets/ + catalog + content/articles/*.json.
Titles from PDF metadata only; no invented halacha text.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "study-guides" / "hilchos-shabbos"
ARTICLES = ROOT / "content" / "articles"
CATALOG = ROOT / "data" / "catalog.json"

# Default source folder; pass paths as CLI args to import other PDFs later.
DEFAULT_GLOB = "Hilchos_Shabbos_*_-_Siman_*.pdf"


def siman_from_name(name: str) -> int:
    m = re.search(r"Siman_(\d+)", name, re.I)
    if not m:
        raise ValueError(f"No siman in filename: {name}")
    return int(m.group(1))


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


def main() -> None:
    import sys

    sources: list[Path] = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else []
    if not sources:
        downloads = Path.home() / "Downloads"
        sources = sorted(downloads.glob(DEFAULT_GLOB))
    if not sources:
        raise SystemExit("No PDFs found. Pass paths or place files in Downloads.")

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES.mkdir(parents=True, exist_ok=True)

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    existing_ids = {p["id"] for p in pieces}

    new_pieces: list[dict] = []
    updated: list[str] = []
    for src in sorted(sources, key=lambda p: siman_from_name(p.name)):
        siman = siman_from_name(src.name)
        pid = piece_id(siman)
        dest = ASSET_DIR / f"siman-{siman}.pdf"
        shutil.copy2(src, dest)
        rel_pdf = dest.relative_to(ROOT).as_posix()

        title = title_from_pdf(src)
        he = hebrew_subtitle_from_pdf(src)

        article_path = ARTICLES / f"{pid}.json"
        article_path.write_text(
            json.dumps({"body": None, "pdf": rel_pdf, "bodyFormat": "html"}, indent=2) + "\n",
            encoding="utf-8",
        )

        entry: dict = {
            "id": pid,
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
        if he:
            entry["hebrewTitle"] = he

        if pid in existing_ids:
            pieces = [entry if p["id"] == pid else p for p in pieces]
            updated.append(pid)
        else:
            new_pieces.append(entry)

    pieces.extend(new_pieces)

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

    catalog["pieces"] = pieces
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(sources)} study guides into {ASSET_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
