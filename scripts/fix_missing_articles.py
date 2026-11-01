#!/usr/bin/env python3
"""Restore article JSON files that catalog ids expect."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "content" / "articles"
IMPORT = ROOT / "_import" / "Diburim-writings" / "Diburim"

sys.path.insert(0, str(ROOT / "scripts"))
from import_docx import body_after_title, extract_doc, pick_title  # noqa: E402


def write_from_docx(piece_id: str, docx: Path) -> None:
    plain, html, _ = extract_doc(docx)
    title, header = pick_title(plain, docx.name)
    html = body_after_title(html, plain, title, header)
    path = ARTICLES / f"{piece_id}.json"
    path.write_text(
        json.dumps({"body": html, "bodyFormat": "html"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {path.name} from {docx.name} ({title[:50]})")


def main() -> None:
    ki_main = ARTICLES / "ki-teitzei.json"
    ki_elul = ARTICLES / "ki-teitzei-elul.json"
    if ki_main.is_file() and not ki_elul.is_file():
        shutil.copy2(ki_main, ki_elul)
        print("Copied ki-teitzei.json -> ki-teitzei-elul.json (checklist essay)")

    write_from_docx("ki-teitzei", IMPORT / "Parshas Ki Seitzei 2026.docx")

    elul_shoftim = next(IMPORT.glob("*Elul*Parshat Shoftim*.docx"), None)
    if elul_shoftim:
        write_from_docx("shoftim-elul", elul_shoftim)
    write_from_docx("shoftim", IMPORT / "Parshas Shoftim Rosh Chodesh Elul 2026.docx")

    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    ids = {p["id"] for p in catalog["pieces"]}
    missing = [i for i in ids if not (ARTICLES / f"{i}.json").is_file() and i]
    if missing:
        print("Still missing article JSON:", ", ".join(sorted(missing)))
    else:
        print("All catalog ids have article JSON (or no body file needed).")


if __name__ == "__main__":
    main()
