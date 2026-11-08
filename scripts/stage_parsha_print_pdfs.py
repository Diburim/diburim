#!/usr/bin/env python3
"""
Export print PDFs from approved .docx sources (_import/Diburim-writings/Diburim).

Uses the same file-picking rules as import_docx.py, then converts via Word (docx2pdf)
so Print / save PDF matches the original document layout—not the HTML reader view.

  python scripts/stage_parsha_print_pdfs.py              # dry run
  python scripts/stage_parsha_print_pdfs.py --apply
  python scripts/stage_parsha_print_pdfs.py --apply --id toldot
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import import_docx as imp  # noqa: E402

ARTICLES_DIR = ROOT / "content" / "articles"
CATALOG_PATH = ROOT / "data" / "catalog.json"
PDF_DIR = ROOT / "assets" / "parsha"
REPORT_PATH = ROOT / "scripts" / "parsha_pdf_report.json"

# Catalog id → exact filename in _import (when auto-matching misses holidays / dual parshiyot).
DOCX_OVERRIDES: dict[str, str] = {
    "vayera-mesirat-nefesh": "Parshas Vayeira - Mesirat Nefesh and Chazakas.docx",
    "vayera-rule-of-three": "Parshas Vayeira – The Rule of Three.docx",
    "erev-rosh-hashanah": "Rosh_Hashana_Shanah_Tovah_Diburim.docx",
    "erev-yom-kippur": "Erev Yom Kippur 2026.docx",
    "erev-sukkot": "Erev Sukkos 2026 .docx",
    "shabbos-chol-hamoed-sukkot": "The Simplicity of Joy — Shabbos Chol HaMoed Sukkos.docx",
    "erev-simchat-torah-2025": "Simchat Torah — The Joy of Continuity 2025.docx",
    "erev-simchat-torah": "Simchat Torah — The Joy of Continuity 2025.docx",
    "vaera": "D_var Torah on Parshas VaEira_ Leadership, Listening, and the Jewish Eye for Detail.docx",
}


def collect_candidates() -> dict[str, imp.Candidate]:
    by_key: dict[str, imp.Candidate] = {}
    for path in sorted(imp.IMPORT_DIR.glob("*.docx")):
        try:
            cand = imp.build_piece(path)
        except ValueError:
            continue
        prev = by_key.get(cand.key)
        if prev is None or cand.score > prev.score:
            by_key[cand.key] = cand
    return by_key


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def resolve_docx(catalog_piece: dict, candidates: list[imp.Candidate]) -> imp.Candidate | None:
    pid = catalog_piece["id"]

    for c in candidates:
        if c.piece["id"] == pid:
            return c

    parsha = catalog_piece.get("parsha")
    if parsha:
        same_parsha = [c for c in candidates if c.piece.get("parsha") == parsha]
        if not same_parsha:
            return None
        if len(same_parsha) == 1:
            return same_parsha[0]
        title_slug = slug(catalog_piece.get("title") or "")
        for c in sorted(same_parsha, key=lambda x: -x.score):
            if title_slug and title_slug[:24] in c.piece["id"]:
                return c
            if c.piece["id"].startswith(pid):
                return c
        return max(same_parsha, key=lambda x: x.score)

    holiday = catalog_piece.get("holiday")
    if holiday:
        same = [c for c in candidates if c.piece.get("holiday") == holiday]
        if same:
            return max(same, key=lambda x: x.score)

    title_slug = slug(catalog_piece.get("title") or pid)
    for c in sorted(candidates, key=lambda x: -x.score):
        if title_slug and title_slug[:20] in slug(c.path.stem):
            return c
    return None


def docx_path_for_piece(catalog_piece: dict, candidates: list[imp.Candidate]) -> Path | None:
    pid = catalog_piece["id"]
    override = DOCX_OVERRIDES.get(pid)
    if override:
        path = imp.IMPORT_DIR / override
        if path.is_file():
            return path
    cand = resolve_docx(catalog_piece, candidates)
    return cand.path if cand else None


def merge_article_pdf(catalog_id: str, rel_pdf: str, source_docx: str) -> None:
    article_path = ARTICLES_DIR / f"{catalog_id}.json"
    article: dict = {}
    if article_path.is_file():
        article = json.loads(article_path.read_text(encoding="utf-8"))
    article["pdf"] = rel_pdf
    article["printSource"] = source_docx
    article.setdefault("bodyFormat", "html")
    article_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def convert_docx_to_pdf(docx: Path, pdf: Path) -> None:
    from docx2pdf import convert

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    tmp = pdf.with_suffix(".part.pdf")
    if tmp.exists():
        tmp.unlink()
    convert(str(docx.resolve()), str(tmp.resolve()))
    if not tmp.is_file():
        raise RuntimeError(f"Conversion produced no file for {docx.name}")
    tmp.replace(pdf)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--id", help="Only process this catalog piece id")
    args = parser.parse_args()

    if not imp.IMPORT_DIR.is_dir():
        raise SystemExit(f"Import folder missing: {imp.IMPORT_DIR}")

    by_key = collect_candidates()
    candidates = list(by_key.values())
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces") or []

    planned: list[dict] = []
    for piece in pieces:
        if piece.get("kind") == "study-guide":
            continue
        if args.id and piece["id"] != args.id:
            continue
        docx_path = docx_path_for_piece(piece, candidates)
        if not docx_path:
            planned.append({"id": piece["id"], "status": "no_source_docx"})
            continue
        rel_pdf = f"assets/parsha/{piece['id']}.pdf"
        planned.append(
            {
                "id": piece["id"],
                "status": "ready",
                "docx": docx_path.name,
                "pdf": rel_pdf,
            }
        )

    if not args.apply:
        print(json.dumps(planned, indent=2))
        ready = sum(1 for row in planned if row.get("status") == "ready")
        print(f"\nDry run: {ready} PDF(s) would be built. Re-run with --apply.")
        REPORT_PATH.write_text(json.dumps({"planned": planned, "applied": False}, indent=2) + "\n", encoding="utf-8")
        return

    applied: list[dict] = []
    for row in planned:
        if row.get("status") != "ready":
            applied.append(row)
            continue
        piece_id = row["id"]
        catalog_piece = next(p for p in pieces if p["id"] == piece_id)
        docx_path = docx_path_for_piece(catalog_piece, candidates)
        assert docx_path
        dest = PDF_DIR / f"{piece_id}.pdf"
        print(f"Converting {docx_path.name} -> {dest.relative_to(ROOT)}")
        convert_docx_to_pdf(docx_path, dest)
        merge_article_pdf(piece_id, row["pdf"], docx_path.name)
        row["status"] = "applied"
        applied.append(row)

    REPORT_PATH.write_text(json.dumps({"applied": applied}, indent=2) + "\n", encoding="utf-8")
    ok = sum(1 for row in applied if row.get("status") == "applied")
    print(f"Done. {ok} PDF(s) in assets/parsha/; article JSON updated with pdf paths.")


if __name__ == "__main__":
    main()
