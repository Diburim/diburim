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
CATALOG_PATH = ROOT / "data" / "catalog.json"
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
    (re.compile(r"\bnoach\b", re.I), "Noach"),
    (re.compile(r"lech\s*lecha|levh\s*levha", re.I), "Lech Lecha"),
    (re.compile(r"vaye?ir", re.I), "Vayera"),
    (re.compile(r"chayei\s*sar", re.I), "Chayei Sara"),
    (re.compile(r"\btoldos\b", re.I), "Toldot"),
    (re.compile(r"vaye?itze|vaye?tzei", re.I), "Vayetzei"),
    (re.compile(r"vayishlach", re.I), "Vayishlach"),
    (re.compile(r"vaye?shev", re.I), "Vayeshev"),
    (re.compile(r"mike?tz", re.I), "Miketz"),
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
    (re.compile(r"re\s*['\u2019]?eh", re.I), "Re'eh"),
    (re.compile(r"shoftim", re.I), "Shoftim"),
    (re.compile(r"ki\s*teitze|ki\s*tetze", re.I), "Ki Teitzei"),
    (re.compile(r"ki\s*tavo", re.I), "Ki Tavo"),
    (re.compile(r"nitzavim", re.I), "Nitzavim"),
    (re.compile(r"vayelech|vayeleich", re.I), "Vayelech"),
    (re.compile(r"haazinu", re.I), "Haazinu"),
]

HOLIDAY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"erev\s+pesach", re.I), "Erev Pesach"),
    (re.compile(r"shevi.?i.*pesach|shvii.*pesach", re.I), "Shvi'i shel Pesach"),
]


def norm(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def parse_parsha(name: str) -> str | None:
    base = norm(name)
    for pat, parsha in HOLIDAY_PATTERNS:
        if pat.search(base):
            return None  # holidays handled separately
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
    if holiday:
        parsha = None
    return Recording(
        path=path,
        mtime=mtime,
        mtime_iso=mtime_dt.isoformat(timespec="seconds"),
        parsha=parsha,
        holiday=holiday,
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
}


def pick_catalog_id(
    rec: Recording,
    by_parsha: dict[str, list[dict]],
    by_holiday: dict[str, list[dict]],
) -> str | None:
    if rec.holiday:
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
        if rec.parsha:
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
            }
        )

    return selected, excluded, skipped, unmapped


def apply_import(selected: list[dict], by_parsha, by_holiday) -> list[dict]:
    AUDIO_OUT_DIR.mkdir(parents=True, exist_ok=True)
    applied: list[dict] = []

    for row in selected:
        rec_path = Path(row["source"])
        rec = Recording(
            path=rec_path,
            mtime=rec_path.stat().st_mtime,
            mtime_iso=row["mtime"],
            parsha=row.get("parsha"),
            holiday=row.get("holiday"),
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
        dest = AUDIO_OUT_DIR / dest_name
        shutil.copy2(rec_path, dest)
        rel = f"assets/audio/parsha/{dest_name}"

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
        report["applied"] = apply_import(selected, by_parsha, by_holiday)

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    print(f"  excluded: {len(excluded)}  selected: {len(selected)}  skipped duplicates: {len(skipped)}  unmapped: {len(unmapped)}")
    if args.apply:
        print(f"  applied: {len(report.get('applied', []))}")


if __name__ == "__main__":
    main()
