#!/usr/bin/env python3
"""One-time repair: canonical multi-parsha slugs and kuntres ids."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog.json"
ARTICLES = ROOT / "content" / "articles"

# current_id -> new_id
RENAME = {
    "vayera": "vayera-mesirat-nefesh",
    "vayera-2": "vayera-rule-of-three",
    "ki-teitzei": "ki-teitzei-elul",
    "ki-teitzei-2": "ki-teitzei",
    "shoftim": "shoftim-elul",
    "shoftim-2": "shoftim",
    "ki-sisa-2": "ki-sisa-teshuvah",
    "": "kuntres-sefer-bereishis",
    "kuntres-devarim": "devarim",
    "kuntres-diburim": "kuntres-devarim",
    "kuntres-ascent-from-the-chagim": "kuntres-bereishit",
}


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    for piece in catalog["pieces"]:
        old = piece["id"]
        if old in RENAME:
            piece["id"] = RENAME[old]

    for old, new in RENAME.items():
        if not old:
            # empty id file may be missing; try kuntres-sefer-bereishis from import
            candidates = list(ARTICLES.glob("*.json"))
            for c in candidates:
                if c.stem in ("kuntres-sefer-bereishis", "sefer-bereishis"):
                    old_path = c
                    break
            else:
                continue
        else:
            old_path = ARTICLES / f"{old}.json"
        new_path = ARTICLES / f"{new}.json"
        if old_path.is_file() and old != new:
            if new_path.is_file():
                old_path.unlink()
            else:
                old_path.rename(new_path)

    valid = {p["id"] for p in catalog["pieces"]}
    for path in list(ARTICLES.glob("*.json")):
        if path.stem not in valid:
            path.unlink()

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Fixed ids:", ", ".join(f"{a}→{b}" for a, b in RENAME.items() if a != b))


if __name__ == "__main__":
    main()
