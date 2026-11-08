#!/usr/bin/env python3
"""
Stage parsha (and holiday) recordings into assets/audio/parsha/{catalog-id}.m4a
and set content/articles/{id}.json "audio" paths.

Source default: Desktop Recordings folder (override with DIBURIM_AUDIO_SOURCE).

Excludes filenames that look non-public or incomplete (case-insensitive):
  not public, not for publication, not complete, incomplete, internal, etc.

When several files map to the same parsha, picks one using:
  1) excluded names dropped
  2) optional --prefer-year (e.g. 2026) — filename year hint, else recording mtime year
  3) highest filesystem mtime (not creation time — copies from device reset ctime)

Dry run (default): writes scripts/audio_inventory.json only.
  python scripts/import_audio.py
Apply copies + updates article JSON:
  python scripts/import_audio.py --apply
"""
from __future__ import annotations

import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path.home() / "Desktop" / "Recordings" / "Diburim"
ARTICLES_DIR = ROOT / "content" / "articles"
AUDIO_OUT_DIR = ROOT / "assets" / "audio" / "parsha"
AUDIO_HOLIDAY_DIR = ROOT / "assets" / "audio" / "holidays"
CATALOG_PATH = ROOT / "data" / "catalog.json"
CALENDAR_PATH = ROOT / "data" / "parsha-calendar.json"
REPORT_PATH = ROOT / "scripts" / "audio_inventory.json"

EXCLUDE_RE = re.compile(
    r"(not\s*for\s*public(?:ation)?|not\s*public|not\s*complete|incomplete|"
    r"\binternal\b|try\s*\d|share\s+with\s+respect)",
    re.I,
)

YEAR_IN_NAME_RE = re.compile(r"\b(20\d{2}|578[0-9])\b")

# Filename fragment → catalog `parsha` field (must match data/catalog.json)
FILENAME_TO_PARSHA: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ber(?:e|i)sh(?:it|is)", re.I), "Bereishis"),
    (re.compile(r"berishit", re.I), "Bereishis"),
    (re.compile(r"erev\s+shabbos\s+ber(?:e)?i?shit\b", re.I), "Bereishis"),
    (re.compile(r"chayei\s*sar[ah]?", re.I), "Chayei Sara"),
    (re.compile(r"\bnoach\b", re.I), "Noach"),
    (re.compile(r"lech\s*lecha|levh\s*levha", re.I), "Lech Lecha"),
    (re.compile(r"vaye?ir", re.I), "Vayera"),
    (re.compile(r"vaye?re\b", re.I), "Vayera"),
    (re.compile(r"shavuos.*naa?so|naa?so.*shavuos", re.I), "Nasso"),
    (re.compile(r"mik[eei]+tz", re.I), "Miketz"),
    (re.compile(r"\btoldos\b", re.I), "Toldot"),
    (re.compile(r"vaye?itze|vaye?tzei", re.I), "Vayetzei"),
    (re.compile(r"vayishlach", re.I), "Vayishlach"),
    (re.compile(r"vaye?shev", re.I), "Vayeshev"),
    (re.compile(r"vayigash", re.I), "Vayigash"),
    (re.compile(r"vayechi", re.I), "Vayechi"),
    (re.compile(r"shemot", re.I), "Shemos"),
    (re.compile(r"va\s*eira|vaeira", re.I), "Vaera"),
    (re.compile(r"beshalach", re.I), "Beshalach"),
    (re.compile(r"parshat\s+bo\b|parshas\s+bo\b|\bbo\.m4a", re.I), "Bo"),
    (re.compile(r"yisro|yitro", re.I), "Yitro"),
    (re.compile(r"mishpatim", re.I), "Mishpatim"),
    (re.compile(r"terumah", re.I), "Terumah"),
    (re.compile(r"tez?taveh", re.I), "Tetzaveh"),
    (re.compile(r"ki\s*tisa", re.I), "Ki Sisa"),
    (re.compile(r"vayakhe?il|pekudei", re.I), "Vayakhel-Pekudei"),
    (re.compile(r"vayikra", re.I), "Vayikra"),
    (re.compile(r"\btzav\b", re.I), "Tzav"),
    (re.compile(r"shmini", re.I), "Shmini"),
    (re.compile(r"tazria|metzor", re.I), "Tazria-Metzora"),
    (re.compile(r"acharei|kedoshim", re.I), "Acharei Mot-Kedoshim"),
    (re.compile(r"\bemor\b", re.I), "Emor"),
    (re.compile(r"behar|bechuk", re.I), "Behar-Bechukotai"),
    (re.compile(r"bamidbar|bamidvar", re.I), "Bamidbar"),
    (re.compile(r"\bnasso\b", re.I), "Nasso"),
    (re.compile(r"bahaaloscha|behaaloscha", re.I), "Behaaloscha"),
    (re.compile(r"\bshlach\b", re.I), "Shlach"),
    (re.compile(r"korach", re.I), "Korach"),
    (re.compile(r"chukas|chukat", re.I), "Chukat"),
    (re.compile(r"\bbalak\b", re.I), "Balak"),
    (re.compile(r"pinchas", re.I), "Pinchas"),
    (re.compile(r"matos|masei", re.I), "Matot-Masei"),
    (re.compile(r"\bdevarim\b", re.I), "Devarim"),
    (re.compile(r"vaes?chanan|vaetchanan", re.I), "Vaetchanan"),
    (re.compile(r"\beikev\b", re.I), "Eikev"),
    (re.compile(r"re\s*['\u2019]?e?h", re.I), "Re'eh"),
    (re.compile(r"parshas\s+re", re.I), "Re'eh"),
    (re.compile(r"shoftim", re.I), "Shoftim"),
    (re.compile(r"ki\s*teitze|ki\s*tetze", re.I), "Ki Teitzei"),
    (re.compile(r"ki\s*tavo", re.I), "Ki Tavo"),
    (re.compile(r"nitzavim", re.I), "Nitzavim"),
    (re.compile(r"vayelech|vayeleich", re.I), "Vayelech"),
    (re.compile(r"haazinu", re.I), "Haazinu"),
]

HOLIDAY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sukkot\s+story", re.I), "Sukkot Story"),
    (re.compile(r"chol\s*hamoed\s*sukkot", re.I), "Shabbos Chol Hamoed Sukkot"),
    (re.compile(r"erev\s+rosh\s*hash", re.I), "Erev Rosh Hashana"),
    (re.compile(r"erev\s+yom\s+kippur", re.I), "Erev Yom Kippur"),
    (re.compile(r"erev\s+simchas?\s*torah", re.I), "Simchat Torah"),
    (re.compile(r"simchas?\s*torah", re.I), "Simchat Torah"),
    (re.compile(r"erev\s+sukkot", re.I), "Erev Sukkot"),
    (re.compile(r"erev\s+pesach", re.I), "Erev Pesach"),
    (re.compile(r"shevi.?i.*pesach|shvii.*pesach", re.I), "Shvi'i shel Pesach"),
]

# Catalog `holiday` field → (id, page title)
HOLIDAY_CATALOG_META: dict[str, tuple[str, str]] = {
    "Erev Pesach": ("erev-pesach", "From Mitzrayim to Closeness"),
    "Shvi'i shel Pesach": ("shvi-i-shel-pesach", "Shvi’i Shel Pesach"),
    "Erev Rosh Hashana": ("erev-rosh-hashanah", "Erev Rosh Hashanah"),
    "Erev Yom Kippur": ("erev-yom-kippur", "Erev Yom Kippur"),
    "Erev Sukkot": ("erev-sukkot", "Erev Sukkot"),
    "Shabbos Chol Hamoed Sukkot": ("shabbos-chol-hamoed-sukkot", "Shabbos Chol Hamoed Sukkot"),
    "Simchat Torah": ("erev-simchat-torah", "Erev Simchat Torah"),
    "Sukkot Story": ("sukkot-story", "Sukkot Story"),
}

# Filename → forced catalog id when parsha alone is ambiguous
FILENAME_FORCE_ID: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"dvar\s*torah.*vaye?re", re.I), "vayera-mesirat-nefesh"),
    # Prior-year editions (separate catalog ids; not deduped with current cycle)
    (re.compile(r"erev\s+shabbos\s+ber(?:e)?i?shit\.m4a$", re.I), "bereishis-2025"),
    (re.compile(r"erev\s+shabbos\s+chayei\s+sora\.m4a$", re.I), "chayei-sara-2025"),
    (re.compile(r"^erev\s+simchat\s+torah\.m4a$", re.I), "erev-simchat-torah-2025"),
]

# Metadata for archive editions (created in catalog when missing)
ARCHIVE_CATALOG_PIECES: dict[str, dict] = {
    "bereishis-2025": {
        "id": "bereishis-2025",
        "title": "Parshas Bereishis",
        "kind": "parsha",
        "series": "Weekly Torah",
        "parsha": "Bereishis",
        "sefer": "Bereishis",
        "categories": ["torah"],
        "date": "2025-10-17",
        "dateDisplay": "October 17, 2025",
    },
    "chayei-sara-2025": {
        "id": "chayei-sara-2025",
        "title": "Parshas Chayei Sara",
        "kind": "parsha",
        "series": "Weekly Torah",
        "parsha": "Chayei Sara",
        "sefer": "Bereishis",
        "categories": ["torah"],
        "date": "2025-11-14",
        "dateDisplay": "November 14, 2025",
    },
    "erev-simchat-torah-2025": {
        "id": "erev-simchat-torah-2025",
        "title": "Erev Simchat Torah",
        "kind": "holiday",
        "series": "Yamim Tovim",
        "holiday": "Simchat Torah",
        "categories": ["torah"],
        "date": "2025-10-10",
        "dateDisplay": "October 10, 2025",
    },
}


def norm(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def parse_parsha(name: str) -> str | None:
    base = norm(name)
    for pat, holiday in HOLIDAY_PATTERNS:
        if pat.search(base):
            return None  # holidays handled separately
    for pat, piece_id in FILENAME_FORCE_ID:
        if pat.search(base):
            return None  # resolved directly to catalog id
    for pat, parsha in FILENAME_TO_PARSHA:
        if pat.search(base):
            return parsha
    return None


def parse_holiday(name: str) -> str | None:
    base = norm(name)
    for pat, holiday in HOLIDAY_PATTERNS:
        if pat.search(base):
            return holiday
    return None


def year_hints(name: str, mtime: datetime) -> set[int]:
    hints: set[int] = set()
    for m in YEAR_IN_NAME_RE.findall(name):
        if m.startswith("578"):
            continue
        hints.add(int(m))
    hints.add(mtime.year)
    return hints


@dataclass
class Recording:
    path: Path
    mtime: float
    mtime_iso: str
    parsha: str | None
    holiday: str | None
    force_id: str | None
    excluded: bool
    exclude_reason: str | None
    years: list[int]


def scan_file(path: Path) -> Recording:
    st = path.stat()
    mtime = st.st_mtime
    mtime_dt = datetime.fromtimestamp(mtime)
    excluded = bool(EXCLUDE_RE.search(path.name))
    reason = "filename marker (not public / incomplete / internal)" if excluded else None
    parsha = None if excluded else parse_parsha(path.name)
    holiday = None if excluded else parse_holiday(path.name)
    force_id = None if excluded else forced_catalog_id(path.name)
    if holiday:
        parsha = None
        force_id = None
    if force_id:
        parsha = None
    return Recording(
        path=path,
        mtime=mtime,
        mtime_iso=mtime_dt.isoformat(timespec="seconds"),
        parsha=parsha,
        holiday=holiday,
        force_id=force_id,
        excluded=excluded,
        exclude_reason=reason,
        years=sorted(year_hints(path.name, mtime_dt)),
    )


def load_catalog_index() -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_parsha: dict[str, list[dict]] = {}
    by_holiday: dict[str, list[dict]] = {}
    for piece in catalog.get("pieces", []):
        if piece.get("parsha"):
            by_parsha.setdefault(piece["parsha"], []).append(piece)
        if piece.get("holiday"):
            by_holiday.setdefault(piece["holiday"], []).append(piece)
    return by_parsha, by_holiday


PRIMARY_PARSHA_ID: dict[str, str] = {
    "Bereishis": "bereishis",
    "Noach": "noach",
    "Chayei Sara": "chayei-sara",
    "Ki Teitzei": "ki-teitzei",
    "Shoftim": "shoftim",
    "Ki Sisa": "ki-sisa",
    "Vayera": "vayera-rule-of-three",
    "Miketz": "miketz",
    "Nasso": "nasso",
}


def forced_catalog_id(filename: str) -> str | None:
    base = norm(filename)
    for pat, piece_id in FILENAME_FORCE_ID:
        if pat.search(base):
            return piece_id
    return None


def find_holiday_date(cal: dict, holiday_key: str) -> tuple[str | None, str | None]:
    """Map internal holiday key to a Hebcal title fragment and return ISO date + display."""
    fragments = {
        "Erev Rosh Hashana": "Erev Rosh Hashana",
        "Erev Yom Kippur": "Erev Yom Kippur",
        "Erev Sukkot": "Erev Sukkot",
        "Simchat Torah": "Simchat",
        "Erev Pesach": "Erev Pesach",
        "Shvi'i shel Pesach": "Pesach VIII",
    }
    frag = fragments.get(holiday_key)
    if not frag:
        return None, None
    dates: list[str] = []
    for row in cal.get("holidays", []):
        title = row.get("title") or ""
        if frag in title:
            dates.append(row["date"])
    if not dates:
        return None, None
    dates.sort()
    y2026 = [d for d in dates if d.startswith("2026")]
    pick = y2026[-1] if y2026 else dates[-1]
    dt = datetime.strptime(pick, "%Y-%m-%d")
    return pick, dt.strftime("%B %d, %Y").replace(" 0", " ")


def ensure_archive_catalog() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    ids = {p["id"] for p in pieces}
    changed = False
    for pid, piece in ARCHIVE_CATALOG_PIECES.items():
        if pid in ids:
            continue
        pieces.append(dict(piece))
        changed = True
        article_path = ARTICLES_DIR / f"{pid}.json"
        if not article_path.is_file():
            article_path.write_text(
                json.dumps({"body": None, "bodyFormat": "html"}, indent=2) + "\n",
                encoding="utf-8",
            )
    if changed:
        catalog["pieces"] = pieces
        CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_holiday_catalog() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pieces = catalog.get("pieces", [])
    ids = {p["id"] for p in pieces}
    cal = json.loads(CALENDAR_PATH.read_text(encoding="utf-8")) if CALENDAR_PATH.is_file() else {"holidays": []}
    changed = False
    for holiday_key, (pid, title) in HOLIDAY_CATALOG_META.items():
        if pid in ids:
            continue
        d, disp = find_holiday_date(cal, holiday_key)
        piece: dict = {
            "id": pid,
            "title": title,
            "kind": "holiday",
            "series": "Yamim Tovim",
            "holiday": holiday_key,
            "categories": ["torah"],
        }
        if d:
            piece["date"] = d
            piece["dateDisplay"] = disp
        pieces.append(piece)
        changed = True
        article_path = ARTICLES_DIR / f"{pid}.json"
        if not article_path.is_file():
            article_path.write_text(
                json.dumps({"body": None, "bodyFormat": "html"}, indent=2) + "\n",
                encoding="utf-8",
            )
    for piece in pieces:
        h = piece.get("holiday")
        if h in HOLIDAY_CATALOG_META and piece.get("series") != "Yamim Tovim":
            piece["series"] = "Yamim Tovim"
            changed = True
    if changed:
        catalog["pieces"] = pieces
        CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pick_catalog_id(
    rec: Recording,
    by_parsha: dict[str, list[dict]],
    by_holiday: dict[str, list[dict]],
) -> str | None:
    if rec.force_id:
        return rec.force_id
    forced = forced_catalog_id(rec.path.name)
    if forced:
        return forced
    if rec.holiday:
        meta = HOLIDAY_CATALOG_META.get(rec.holiday)
        if meta:
            return meta[0]
        rows = by_holiday.get(rec.holiday, [])
        return rows[0]["id"] if len(rows) == 1 else (rows[0]["id"] if rows else None)
    if rec.parsha:
        rows = by_parsha.get(rec.parsha, [])
        if not rows:
            return None
        if len(rows) == 1:
            return rows[0]["id"]
        prefer = PRIMARY_PARSHA_ID.get(rec.parsha)
        if prefer and any(p["id"] == prefer for p in rows):
            return prefer
        weekly = [p for p in rows if p.get("series") == "Weekly Torah"]
        primary = [p for p in weekly if not re.search(r"-(elul|teshuvah)(?:-|$)", p["id"])]
        pool = primary or weekly or rows
        if len(pool) == 1:
            return pool[0]["id"]
        pool = sorted(pool, key=lambda p: (len(p["id"]), p["id"]))
        return pool[0]["id"]
    return None


def score_candidate(rec: Recording, prefer_year: int | None) -> tuple:
    """Higher sort key = better."""
    year_match = 0
    if prefer_year and prefer_year in rec.years:
        year_match = 1
    name_has_year = 1 if YEAR_IN_NAME_RE.search(rec.path.name) else 0
    return (year_match, name_has_year, rec.mtime, rec.path.stat().st_size)


def group_and_pick(
    recordings: list[Recording],
    prefer_year: int | None,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    buckets: dict[str, list[Recording]] = {}
    unmapped: list[dict] = []
    excluded: list[dict] = []

    for rec in recordings:
        if rec.excluded:
            excluded.append(
                {
                    "file": rec.path.name,
                    "reason": rec.exclude_reason,
                    "mtime": rec.mtime_iso,
                }
            )
            continue
        key = None
        if rec.force_id:
            key = f"id:{rec.force_id}"
        elif rec.parsha:
            key = f"parsha:{rec.parsha}"
        elif rec.holiday:
            key = f"holiday:{rec.holiday}"
        else:
            unmapped.append(
                {
                    "file": rec.path.name,
                    "mtime": rec.mtime_iso,
                    "note": "no parsha/holiday match",
                }
            )
            continue
        buckets.setdefault(key, []).append(rec)

    selected: list[dict] = []
    skipped: list[dict] = []

    for key, items in sorted(buckets.items()):
        ranked = sorted(items, key=lambda r: score_candidate(r, prefer_year), reverse=True)
        winner = ranked[0]
        for loser in ranked[1:]:
            skipped.append(
                {
                    "file": loser.path.name,
                    "mtime": loser.mtime_iso,
                    "years": loser.years,
                    "reason": f"superseded by {winner.path.name}",
                    "group": key,
                }
            )
        selected.append(
            {
                "file": winner.path.name,
                "source": str(winner.path),
                "mtime": winner.mtime_iso,
                "years": winner.years,
                "group": key,
                "parsha": winner.parsha,
                "holiday": winner.holiday,
                "forceId": winner.force_id,
            }
        )

    return selected, excluded, skipped, unmapped


def apply_import(selected: list[dict], by_parsha, by_holiday) -> list[dict]:
    AUDIO_OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_HOLIDAY_DIR.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in catalog.get("pieces", [])}
    applied: list[dict] = []

    for row in selected:
        rec_path = Path(row["source"])
        rec = Recording(
            path=rec_path,
            mtime=rec_path.stat().st_mtime,
            mtime_iso=row["mtime"],
            parsha=row.get("parsha"),
            holiday=row.get("holiday"),
            force_id=row.get("forceId"),
            excluded=False,
            exclude_reason=None,
            years=row.get("years", []),
        )
        piece_id = pick_catalog_id(rec, by_parsha, by_holiday)
        if not piece_id:
            row["applyError"] = "no catalog id"
            applied.append(row)
            continue

        ext = rec_path.suffix.lower()
        if ext not in {".m4a", ".mp3", ".aac", ".wav"}:
            ext = ".m4a"
        dest_name = f"{piece_id}{ext}"
        piece = by_id.get(piece_id, {})
        is_holiday = piece.get("kind") == "holiday"
        dest_dir = AUDIO_HOLIDAY_DIR if is_holiday else AUDIO_OUT_DIR
        dest = dest_dir / dest_name
        shutil.copy2(rec_path, dest)
        folder = "holidays" if is_holiday else "parsha"
        rel = f"assets/audio/{folder}/{dest_name}"

        article_path = ARTICLES_DIR / f"{piece_id}.json"
        article: dict = {}
        if article_path.is_file():
            article = json.loads(article_path.read_text(encoding="utf-8"))
        article["audio"] = rel
        article.setdefault("bodyFormat", "html")
        article_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        row["catalogId"] = piece_id
        row["dest"] = rel
        applied.append(row)

    return applied


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__import__("os").environ.get("DIBURIM_AUDIO_SOURCE", str(DEFAULT_SOURCE))),
    )
    parser.add_argument("--prefer-year", type=int, default=2026, help="Prefer files whose name or mtime year matches")
    parser.add_argument("--apply", action="store_true", help="Copy files and update content/articles/*.json")
    args = parser.parse_args()

    if not args.source.is_dir():
        raise SystemExit(f"Source folder missing: {args.source}")

    recordings = [scan_file(p) for p in sorted(args.source.iterdir()) if p.is_file()]
    by_parsha, by_holiday = load_catalog_index()
    selected, excluded, skipped, unmapped = group_and_pick(recordings, args.prefer_year)

    for row in selected:
        fake = Recording(
            path=Path(row["source"]),
            mtime=0,
            mtime_iso=row["mtime"],
            parsha=row.get("parsha"),
            holiday=row.get("holiday"),
            force_id=row.get("forceId"),
            excluded=False,
            exclude_reason=None,
            years=row.get("years", []),
        )
        row["suggestedCatalogId"] = pick_catalog_id(fake, by_parsha, by_holiday)

    report = {
        "source": str(args.source),
        "preferYear": args.prefer_year,
        "excludedCount": len(excluded),
        "selectedCount": len(selected),
        "excluded": excluded,
        "selected": selected,
        "skippedDuplicates": skipped,
        "unmapped": unmapped,
    }

    if args.apply:
        ensure_archive_catalog()
        ensure_holiday_catalog()
        by_parsha, by_holiday = load_catalog_index()
        report["applied"] = apply_import(selected, by_parsha, by_holiday)

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    print(f"  excluded: {len(excluded)}  selected: {len(selected)}  skipped duplicates: {len(skipped)}  unmapped: {len(unmapped)}")
    if args.apply:
        print(f"  applied: {len(report.get('applied', []))}")


if __name__ == "__main__":
    main()
