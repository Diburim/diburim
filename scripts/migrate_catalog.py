#!/usr/bin/env python3
"""
Short slugs, Hebcal dates, dedupe, metadata fixes, gap report.
Run after import_docx.py; requires data/parsha-calendar.json (fetch_parsha_calendar.py).
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"
CALENDAR_PATH = ROOT / "data" / "parsha-calendar.json"
ARTICLES_DIR = ROOT / "content" / "articles"
GAPS_PATH = ROOT / "scripts" / "PARSHA_GAPS.md"
REPORT_PATH = ROOT / "scripts" / "migrate_catalog_report.json"

# Canonical short slug per catalog `parsha` name
PARSHA_SLUG: dict[str, str] = {
    "Bereishis": "bereishis",
    "Noach": "noach",
    "Lech Lecha": "lech-lecha",
    "Vayera": "vayera",
    "Chayei Sara": "chayei-sara",
    "Toldot": "toldot",
    "Vayetzei": "vayetzei",
    "Vayishlach": "vayishlach",
    "Vayeshev": "vayeshev",
    "Miketz": "miketz",
    "Vayigash": "vayigash",
    "Vayechi": "vayechi",
    "Shemos": "shemos",
    "Vaera": "vaera",
    "Bo": "bo",
    "Beshalach": "beshalach",
    "Yitro": "yitro",
    "Mishpatim": "mishpatim",
    "Terumah": "terumah",
    "Tetzaveh": "tetzaveh",
    "Ki Sisa": "ki-sisa",
    "Vayakhel-Pekudei": "vayakhel-pekudei",
    "Vayikra": "vayikra",
    "Tzav": "tzav",
    "Shmini": "shmini",
    "Tazria-Metzora": "tazria-metzora",
    "Acharei Mot-Kedoshim": "acharei-mot-kedoshim",
    "Emor": "emor",
    "Behar-Bechukotai": "behar-bechukotai",
    "Bamidbar": "bamidbar",
    "Nasso": "nasso",
    "Behaaloscha": "behaaloscha",
    "Shlach": "shlach",
    "Korach": "korach",
    "Chukat": "chukat",
    "Balak": "balak",
    "Pinchas": "pinchas",
    "Matot-Masei": "matot-masei",
    "Devarim": "devarim",
    "Vaetchanan": "vaetchanan",
    "Eikev": "eikev",
    "Re'eh": "re-eh",
    "Shoftim": "shoftim",
    "Ki Teitzei": "ki-teitzei",
    "Ki Tavo": "ki-tavo",
    "Nitzavim": "nitzavim",
    "Vayelech": "vayelech",
    "Haazinu": "haazinu",
    "VeZot Haberachah": "vezot-haberachah",
}

# 5786 cycle (first occurrence after Oct 2025) — sedra list for gap analysis
CYCLE_START = "2025-10-18"
CYCLE_END = "2026-09-19"

# Manual fixes from source filenames (content integrity: parsha from author file name)
FILENAME_PARSHA_FIX: dict[str, str] = {
    "D_var Torah on Parshas VaEira_ Leadership, Listening, and the Jewish Eye for Detail.docx": "Vaera",
}

# Prefer keeping this id when deduping same parsha (old id → reason)
DROP_IDS = {
    "matot-masei-parshas-matosmasei",
    "ki-tavo-parshas-ki-tavo",
    "re-eh-parshas-re-eh",
    "vaetchanan-parshas-va-etchanan",
    "shlach-dvar-torah-parshas-shlach",
    "bereishis-ascent-from-the-chagim",
    "yitro-this-weeks-parsha-yitro-yisro-is-a-v",
}

SEFER_BY_PARSHA: dict[str, str] = {
    "Vaera": "Shemos",
    "Bo": "Shemos",
    "Beshalach": "Shemos",
    "Yitro": "Shemos",
    "Mishpatim": "Shemos",
    "Terumah": "Shemos",
    "Tetzaveh": "Shemos",
    "Ki Sisa": "Shemos",
    "Vayakhel-Pekudei": "Shemos",
    "Shemos": "Shemos",
}

# Extra slug suffixes when multiple pieces share a parsha (old id → new id)
FORCED_ID: dict[str, str] = {
    "chayei-sara-the-power-of-the-imahot-nature-nurtu": "chayei-sara",
    "vayera-parshas-vayeira-mesirat-nefesh-and-c": "vayera-mesirat-nefesh",
    "vayera-parshas-vayeira-the-rule-of-three": "vayera-rule-of-three",
    "ki-sisa-d-var-torah-on-parshas-ki-sisa-the-s": "ki-sisa",
    "ki-sisa-the-strength-of-being-human-falling-": "ki-sisa-teshuvah",
    "yitro-d-var-torah-on-parshas-yitro-the-blu": "yitro",
    "vayikra-avodah-awareness-and-bringing-what-y": "vayikra",
    "vayikra-d-var-torah-on-parshas-vaeira-leader": "vaera",
    "ki-teitzei-ki-tetzei-a-checklist-for-elul": "ki-teitzei-elul",
    "ki-teitzei-parshas-ki-seitzei": "ki-teitzei",
    "shoftim-elul-connection-ani-ldodi": "shoftim-elul",
    "shoftim-parshas-shoftim": "shoftim",
    "nitzavim-standing-together-hidden-things-reve": "nitzavim",
    "vayelech-parshat-vayeleich-living-beyond-the-": "vayelech",
    "noach-parshas-noach-a-deeper-look-at-tafki": "noach",
    "lech-lecha-lech-lecha-the-beginnings-of-z-chut-": "lech-lecha",
    "toldot-building-toldos-with-awareness-mesor": "toldot",
    "vayetzei-foundational-themes": "vayetzei",
    "vayishlach-d-var-torah-on-parshas-vayishlach-st": "vayishlach",
    "haazinu-the-final-full-parsha": "haazinu",
    "acharei-mot-kedoshim-who-defines-value-living-as-kedoshim": "acharei-mot-kedoshim",
    "shmini-growth-within-structure-reaching-wit": "shmini",
    "balak-parshas-balak": "balak",
    "chukat-parshas-chukas": "chukat",
    "bamidbar-parshas-bamidbar": "bamidbar",
    "behaaloscha-parshas-beha-aloscha": "behaaloscha",
    "korach-parshas-korach": "korach",
    "matot-masei-parshas-matos-masei": "matot-masei",
    "nasso-parshas-nasso": "nasso",
    "pinchas-parshas-pinchas": "pinchas",
    "shlach-parshas-shlach": "shlach",
    "miketz-parshas-miketz": "miketz",
    "vayeshev-parshas-vayeishev": "vayeshev",
    "eikev-parshas-eikev": "eikev",
    "ki-tavo-parshas-ki-savo": "ki-tavo",
    "re-eh-parshas-reeh": "re-eh",
    "vaetchanan-parshas-vaeschanan": "vaetchanan",
    "emor-parshas-emor": "emor",
    "behar-bechukotai-parshas-beharbechukosai": "behar-bechukotai",
    "beshalach-d-var-torah-on-parshas-beshalach-mov": "beshalach",
    "bo-d-var-torah-on-parshas-bo-coming-tog": "bo",
    "mishpatim-d-var-torah-on-parshas-mishpatim-the": "mishpatim",
    "terumah-d-var-torah-on-parshas-terumah-build": "terumah",
    "tetzaveh-becoming-the-mishkan-from-olive-oil-": "tetzaveh",
    "vayakhel-pekudei-the-testimony-of-creation-building-f": "vayakhel-pekudei",
    "tzav-mesorah-time-and-standing-our-ground": "tzav",
    "tazria-metzora-diburim-sefer-vayikra": "tazria-metzora",
    "devarim-parshas-devarim": "devarim",
    "devarim": "kuntres-devarim",
    "bereishit-diburim": "kuntres-bereishit",
    "sefer-bereishis": "kuntres-sefer-bereishis",
    "erev-pesach": "erev-pesach",
    "shvi-i-shel-pesach": "shvi-i-shel-pesach",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:80]


def body_words(piece_id: str) -> int:
    path = ARTICLES_DIR / f"{piece_id}.json"
    if not path.is_file():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    text = re.sub(r"<[^>]+>", " ", data.get("body") or "")
    return len(text.split())


def load_calendar() -> tuple[dict[str, str], dict[str, str]]:
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
        # Prefer 2026 Shabbat when Hebcal lists the sedra twice (matches 2026-titled docx batch).
        parsha_to_date[p] = y2026[-1] if y2026 else in_window[-1]

    parsha_to_display: dict[str, str] = {}
    for p, d in parsha_to_date.items():
        dt = datetime.strptime(d, "%Y-%m-%d")
        parsha_to_display[p] = dt.strftime("%B %d, %Y").replace(" 0", " ")
    return parsha_to_date, parsha_to_display


def fix_holiday_metadata(piece: dict) -> None:
    """Remove false Pesach/Shavuot from weekly parsha essays (body mentioned chagim)."""
    h = piece.get("holiday")
    if piece.get("parsha") and h in ("Pesach", "Shavuot", "Shvi'i shel Pesach"):
        piece.pop("holiday", None)
        if piece.get("kind") == "holiday":
            piece["kind"] = "parsha"
    if piece.get("parsha") == "Tzav" and piece.get("title", "").startswith("Mesorah"):
        piece.pop("holiday", None)
        piece["kind"] = "parsha"
        piece["occasion"] = piece.get("occasion") or "Shabbos HaGadol"
    if piece.get("parsha") == "Nasso" and piece.get("occasion"):
        pass  # keep Shavuot occasion only in `occasion`, not holiday kind


CANONICAL_BY_TITLE: list[tuple[str, str, str]] = [
    ("Vayera", "Mesirat Nefesh", "vayera-mesirat-nefesh"),
    ("Vayera", "Rule of Three", "vayera-rule-of-three"),
    ("Ki Sisa", "Gift of Teshuvah", "ki-sisa-teshuvah"),
    ("Ki Teitzei", "Checklist for Elul", "ki-teitzei-elul"),
    ("Shoftim", "Ani L", "shoftim-elul"),
]


def canonical_id(piece: dict) -> str | None:
    title = piece.get("title") or ""
    parsha = piece.get("parsha")
    for p, frag, cid in CANONICAL_BY_TITLE:
        if parsha == p and frag in title:
            return cid
    if piece.get("kind") == "kuntres" and piece.get("title") == "DIBURIM":
        return "kuntres-devarim"
    if piece.get("kind") == "kuntres" and "בְּרֵאשִׁית" in title:
        return "kuntres-sefer-bereishis"
    if piece.get("kind") == "kuntres" and piece.get("title") == "Ascent from the Chagim":
        return "kuntres-bereishit"
    return None


def assign_short_id(piece: dict, used: set[str]) -> str:
    canon = canonical_id(piece)
    if canon:
        new = canon
    else:
        old = piece["id"]
        if old in FORCED_ID:
            new = FORCED_ID[old]
        elif piece.get("kind") == "kuntres":
            new = slugify(piece.get("title") or old) or "kuntres-piece"
            if not new.startswith("kuntres-"):
                new = f"kuntres-{new}"
        elif piece.get("parsha"):
            base = PARSHA_SLUG.get(piece["parsha"], slugify(piece["parsha"]))
            new = base or slugify(piece["parsha"])
        elif piece.get("holiday"):
            new = slugify(piece["holiday"]) or "holiday"
        else:
            new = slugify(piece.get("title") or old) or old or "piece"

    if new in used:
        if piece.get("parsha") and new == PARSHA_SLUG.get(piece["parsha"]):
            suffix = slugify(piece.get("title", ""))[:24] or "alt"
            new = f"{new}-{suffix}"
        n = 2
        while new in used:
            new = f"{PARSHA_SLUG.get(piece.get('parsha') or '', 'piece')}-{n}"
            n += 1
    return new


def main() -> None:
    if not CALENDAR_PATH.is_file():
        raise SystemExit(f"Missing {CALENDAR_PATH}; run scripts/fetch_parsha_calendar.py first")

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    import_report = json.loads((ROOT / "scripts" / "import_report.json").read_text(encoding="utf-8"))
    source_by_old_id = {p["id"]: p.get("sourceFile") for p in import_report.get("pieces", [])}

    parsha_dates, parsha_display = load_calendar()

    # Apply filename parsha fixes
    for piece in pieces:
        src = source_by_old_id.get(piece["id"])
        if src and src in FILENAME_PARSHA_FIX:
            piece["parsha"] = FILENAME_PARSHA_FIX[src]
            if piece["parsha"] in SEFER_BY_PARSHA:
                piece["sefer"] = SEFER_BY_PARSHA[piece["parsha"]]

    # Drop duplicate catalog rows
    pieces = [p for p in pieces if p["id"] not in DROP_IDS]

    for piece in pieces:
        fix_holiday_metadata(piece)

    # Rename ids
    id_map: dict[str, str] = {}
    used_ids: set[str] = set()
    for piece in pieces:
        old_id = piece["id"]
        new_id = assign_short_id(piece, used_ids)
        while new_id in used_ids:
            new_id = f"{new_id}-alt"
        used_ids.add(new_id)
        id_map[old_id] = new_id
        piece["id"] = new_id

    # Attach calendar dates (5786 cycle)
    for piece in pieces:
        parsha = piece.get("parsha")
        if not parsha or piece.get("kind") == "kuntres":
            continue
        d = parsha_dates.get(parsha)
        if not d and parsha == "Balak":
            d = parsha_dates.get("Chukat")  # combined week
        if not d and parsha == "Chukat":
            d = parsha_dates.get("Chukat") or parsha_dates.get("Balak")
        if not d and parsha == "Vayelech":
            d = parsha_dates.get("Nitzavim")
        if not d and parsha == "Nitzavim":
            d = parsha_dates.get("Nitzavim")
        if d:
            piece["date"] = d
            piece["dateDisplay"] = parsha_display.get(parsha) or parsha_display.get("Nitzavim", d)

    # Holiday dates from calendar holidays list
    cal = json.loads(CALENDAR_PATH.read_text(encoding="utf-8"))
    for piece in pieces:
        if piece.get("holiday") == "Erev Pesach":
            for h in cal.get("holidays", []):
                if "Erev Pesach" in h.get("title", ""):
                    piece["date"] = h["date"]
                    dt = datetime.strptime(h["date"], "%Y-%m-%d")
                    piece["dateDisplay"] = dt.strftime("%B %d, %Y").replace(" 0", " ")
                    break
        if piece.get("holiday") == "Shvi'i shel Pesach":
            for h in cal.get("holidays", []):
                t = h.get("title", "")
                if t in ("Pesach VIII", "Pesach 8") or "8th Day of Pesach" in t:
                    piece["date"] = h["date"]
                    dt = datetime.strptime(h["date"], "%Y-%m-%d")
                    piece["dateDisplay"] = dt.strftime("%B %d, %Y").replace(" 0", " ")
                    break

    # Rename article files
    for old_id, new_id in id_map.items():
        if old_id == new_id:
            continue
        old_path = ARTICLES_DIR / f"{old_id}.json"
        new_path = ARTICLES_DIR / f"{new_id}.json"
        if old_path.is_file():
            if new_path.is_file():
                old_path.unlink()
            else:
                old_path.rename(new_path)

    # Remove orphan article json
    valid = {p["id"] for p in pieces}
    for path in ARTICLES_DIR.glob("*.json"):
        if path.stem not in valid:
            path.unlink()

    this_week = "chayei-sara"
    if not any(p["id"] == this_week for p in pieces):
        this_week = next((p["id"] for p in pieces if p.get("parsha") == "Chayei Sara"), None)

    catalog["pieces"] = pieces
    catalog["thisWeekId"] = this_week
    catalog["calendarSource"] = "data/parsha-calendar.json"
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Gap report
    cycle_parshas: list[str] = []
    for row in cal.get("readings", []):
        d = row["date"]
        if d < CYCLE_START or d > CYCLE_END:
            continue
        for p in row.get("parshas", []):
            if p not in cycle_parshas:
                cycle_parshas.append(p)

    have: set[str] = set()
    for p in pieces:
        parsha = p.get("parsha")
        if not parsha or p.get("kind") == "kuntres":
            continue
        if p.get("holiday") in ("Erev Pesach", "Shvi'i shel Pesach"):
            continue
        have.add(parsha)
    missing = [p for p in cycle_parshas if p not in have]
    # Combined sedra: satisfied if any constituent present
    for combined, parts in [("Chukat-Balak", ["Chukat", "Balak"]), ("Nitzavim-Vayelech", ["Nitzavim", "Vayelech"])]:
        if combined in missing and any(x in have for x in parts):
            missing.remove(combined)

    extras = sorted(have - set(cycle_parshas))

    lines = [
        "# Parsha coverage (5786 cycle, Diaspora)",
        "",
        f"Calendar: `{CALENDAR_PATH.relative_to(ROOT)}` (Hebcal, NYC).",
        f"Cycle window: **{CYCLE_START}** through **{CYCLE_END}**.",
        "",
        f"**Published weekly parsha pieces:** {len(have)} distinct parsha labels in catalog.",
        f"**Sedra slots in cycle:** {len(cycle_parshas)} (includes combined readings).",
        "",
        "## Missing sedra (no `kind: parsha` piece with this parsha)",
        "",
    ]
    if missing:
        for m in missing:
            lines.append(f"- {m}")
    else:
        lines.append("- _(none)_")
    lines.extend(["", "## Extra parsha labels (not a separate sedra this cycle)", ""])
    for e in extras:
        lines.append(f"- {e}")
    lines.extend(["", "## Duplicate parsha (multiple essays)", ""])
    from collections import Counter

    counts = Counter(p.get("parsha") for p in pieces if p.get("kind") == "parsha" and p.get("parsha"))
    for parsha, n in sorted(counts.items()):
        if n > 1:
            ids = [p["id"] for p in pieces if p.get("parsha") == parsha]
            lines.append(f"- **{parsha}** ({n}): {', '.join(ids)}")
    lines.extend(["", "## Catalog IDs renamed", ""])
    for old, new in sorted(id_map.items()):
        if old != new:
            lines.append(f"- `{old}` → `{new}`")
    GAPS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    REPORT_PATH.write_text(
        json.dumps({"idMap": id_map, "thisWeekId": this_week, "missingSedra": missing}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Migrated {len(pieces)} pieces; thisWeekId={this_week}")
    print(f"Gaps: {GAPS_PATH}")


if __name__ == "__main__":
    main()
