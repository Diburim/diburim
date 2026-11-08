#!/usr/bin/env python3
"""Copy an approved parsha PDF into assets/parsha/ and wire content/articles/{id}.json.

Usage:
  python scripts/import_parsha_pdf.py toldot "C:\\path\\to\\Toldot.pdf"
  python scripts/import_parsha_pdf.py toldot "C:\\path\\to\\Toldot.pdf" --apply

Dry-run by default (prints planned paths). --apply copies the file and updates JSON.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "content" / "articles"
PDF_DIR = ROOT / "assets" / "parsha"


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage a parsha PDF for print/download on diburim.org")
    parser.add_argument("catalog_id", help="Catalog piece id, e.g. toldot")
    parser.add_argument("source_pdf", type=Path, help="Path to the source PDF file")
    parser.add_argument("--apply", action="store_true", help="Copy file and update article JSON")
    args = parser.parse_args()

    catalog_id = args.catalog_id.strip()
    source = args.source_pdf.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Source PDF not found: {source}")

    dest = PDF_DIR / f"{catalog_id}.pdf"
    rel = f"assets/parsha/{catalog_id}.pdf"
    article_path = ARTICLES_DIR / f"{catalog_id}.json"

    print(f"Source:  {source}")
    print(f"Dest:    {dest}")
    print(f"Article: {article_path}  (pdf: {rel})")

    if not args.apply:
        print("Dry run only. Re-run with --apply to copy and update JSON.")
        return

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)

    article: dict = {}
    if article_path.is_file():
        article = json.loads(article_path.read_text(encoding="utf-8"))
    article["pdf"] = rel
    article.setdefault("bodyFormat", "html")
    article_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Done.")


if __name__ == "__main__":
    main()
