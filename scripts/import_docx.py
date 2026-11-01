#!/usr/bin/env python3
"""
Import Rabbi Goldberg's .docx writings into content/articles/*.json and data/catalog.json.
Preserves body text; does not paraphrase. Metadata derived from filenames and document lines only.
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
IMPORT_DIR = ROOT / "_import" / "Diburim-writings" / "Diburim"
ARTICLES_DIR = ROOT / "content" / "articles"
CATALOG_PATH = ROOT / "data" / "catalog.json"
REPORT_PATH = ROOT / "scripts" / "import_report.json"

THIS_WEEK_PARSHA_SLUGS = {"chayei-sara", "chayei-sarah"}

PARSHA_ALIASES: dict[str, str] = {
    "bereishis": "Bereishis",
    "bereishit": "Bereishis",
    "noach": "Noach",
    "lech lecha": "Lech Lecha",
    "vayera": "Vayera",
    "vayeira": "Vayera",
    "vayeishev": "Vayeshev",
    "chayei sarah": "Chayei Sara",
    "chayei sara": "Chayei Sara",
    "toldos": "Toldot",
    "toldot": "Toldot",
    "vayetzei": "Vayetzei",
    "vayishlach": "Vayishlach",
    "vayeshev": "Vayeshev",
    "miketz": "Miketz",
    "vayigash": "Vayigash",
    "vayechi": "Vayechi",
    "shemos": "Shemos",
    "vaera": "Vaera",
    "va'eira": "Vaera",
    "bo": "Bo",
    "beshalach": "Beshalach",
    "yitro": "Yitro",
    "yisro": "Yitro",
    "mishpatim": "Mishpatim",
    "terumah": "Terumah",
    "tetzaveh": "Tetzaveh",
    "ki sisa": "Ki Sisa",
    "ki tisa": "Ki Sisa",
    "vayakhel": "Vayakhel-Pekudei",
    "pekudei": "Vayakhel-Pekudei",
    "vayakhel-pekudei": "Vayakhel-Pekudei",
    "vayikra": "Vayikra",
    "tzav": "Tzav",
    "shmini": "Shmini",
    "shmini": "Shmini",
    "tazria": "Tazria-Metzora",
    "metzora": "Tazria-Metzora",
    "tazria-metzora": "Tazria-Metzora",
    "acharei mot": "Acharei Mot-Kedoshim",
    "kedoshim": "Acharei Mot-Kedoshim",
    "emor": "Emor",
    "behar": "Behar-Bechukotai",
    "bechukosai": "Behar-Bechukotai",
    "bechukotai": "Behar-Bechukotai",
    "bamidbar": "Bamidbar",
    "nasso": "Nasso",
    "behaaloscha": "Behaaloscha",
    "beha'aloscha": "Behaaloscha",
    "shlach": "Shlach",
    "korach": "Korach",
    "chukas": "Chukat",
    "chukat": "Chukat",
    "balak": "Balak",
    "pinchas": "Pinchas",
    "matos": "Matot-Masei",
    "masei": "Matot-Masei",
    "matot-masei": "Matot-Masei",
    "devarim": "Devarim",
    "vaetchanan": "Vaetchanan",
    "vaeschanan": "Vaetchanan",
    "eikev": "Eikev",
    "reeh": "Re'eh",
    "shoftim": "Shoftim",
    "ki tetzei": "Ki Teitzei",
    "ki teitzei": "Ki Teitzei",
    "ki seitzei": "Ki Teitzei",
    "ki tavo": "Ki Tavo",
    "kitavo": "Ki Tavo",
    "ki savo": "Ki Tavo",
    "nitzavim": "Nitzavim",
    "vayelech": "Vayelech",
    "vayeleich": "Vayelech",
    "haazinu": "Haazinu",
    "vezot haberachah": "VeZot Haberachah",
}

SEFER_BY_PARSHA: dict[str, str] = {
    "Bereishis": "Bereishis",
    "Noach": "Bereishis",
    "Lech Lecha": "Bereishis",
    "Vayera": "Bereishis",
    "Chayei Sara": "Bereishis",
    "Toldot": "Bereishis",
    "Vayetzei": "Bereishis",
    "Vayishlach": "Bereishis",
    "Vayeshev": "Bereishis",
    "Miketz": "Bereishis",
    "Vayigash": "Bereishis",
    "Vayechi": "Bereishis",
    "Shemos": "Shemos",
    "Vaera": "Shemos",
    "Bo": "Shemos",
    "Beshalach": "Shemos",
    "Yitro": "Shemos",
    "Mishpatim": "Shemos",
    "Terumah": "Shemos",
    "Tetzaveh": "Shemos",
    "Ki Sisa": "Shemos",
    "Vayakhel-Pekudei": "Shemos",
    "Vayikra": "Vayikra",
    "Tzav": "Vayikra",
    "Shmini": "Vayikra",
    "Tazria-Metzora": "Vayikra",
    "Acharei Mot-Kedoshim": "Vayikra",
    "Emor": "Vayikra",
    "Behar-Bechukotai": "Vayikra",
    "Bamidbar": "Bamidbar",
    "Nasso": "Bamidbar",
    "Behaaloscha": "Bamidbar",
    "Shlach": "Bamidbar",
    "Korach": "Bamidbar",
    "Chukat": "Bamidbar",
    "Balak": "Bamidbar",
    "Pinchas": "Bamidbar",
    "Matot-Masei": "Bamidbar",
    "Devarim": "Devarim",
    "Vaetchanan": "Devarim",
    "Eikev": "Devarim",
    "Re'eh": "Devarim",
    "Shoftim": "Devarim",
    "Ki Teitzei": "Devarim",
    "Ki Tavo": "Devarim",
    "Nitzavim": "Devarim",
    "Vayelech": "Devarim",
    "Haazinu": "Devarim",
    "VeZot Haberachah": "Devarim",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80] or "piece"


def normalize_lookup(s: str) -> str:
    s = s.lower().replace("_", " ").replace("-", " ")
    s = re.sub(r"[^\w\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _match_parsha_in(hay: str) -> str | None:
    for alias in sorted(PARSHA_ALIASES.keys(), key=len, reverse=True):
        if re.search(r"\b" + re.escape(alias) + r"\b", hay):
            return PARSHA_ALIASES[alias]
    return None


def detect_parsha(name: str, doc_lines: list[str]) -> str | None:
    """Filename and opening lines only — avoid false matches from later pesukim or cross-references."""
    from_filename = _match_parsha_in(normalize_lookup(name))
    if from_filename:
        return from_filename
    header = normalize_lookup(" ".join(doc_lines[:4]))
    return _match_parsha_in(header)


def detect_holiday(name: str, doc_lines: list[str]) -> str | None:
    """Filename / title line only — weekly essays often mention Pesach in the body."""
    hay = normalize_lookup(name)
    header = normalize_lookup(" ".join(doc_lines[:2]))
    combined = hay + " " + header
    if "erev pesach" in combined:
        return "Erev Pesach"
    if "shvii shel pesach" in combined or "shvi i shel pesach" in combined:
        return "Shvi'i shel Pesach"
    if re.search(r"\bpesach\b", combined) and re.search(r"parsh", combined) is None:
        if "erev" not in combined:
            return "Pesach"
    if "shavuos" in combined or "shavuot" in combined:
        return "Shavuot"
    if "shabbos hagadol" in combined or "shabbos ha gadol" in combined:
        return "Shabbos HaGadol"
    return None


def detect_occasion(name: str, doc_lines: list[str]) -> str | None:
    hay = (name + " " + " ".join(doc_lines[:10])).lower()
    if "rosh chodesh elul" in hay or ("elul" in hay and "shoftim" in hay):
        return "Elul · Parshas Shoftim"
    if "nachamu" in hay:
        return "Shabbos Nachamu"
    if "chazon" in hay:
        return "Shabbos Chazon"
    return None


def file_score(path: Path) -> int:
    name = path.name.lower()
    score = path.stat().st_size
    if "internal" in name:
        score -= 10_000_000
    if name.startswith("copy of"):
        score -= 10_000_000
    if "_full_diburim" in name or "full_diburim" in name:
        score += 500_000
    if "_diburim" in name or " diburim" in name:
        score += 250_000
    if "final" in name:
        score += 100_000
    if re.search(r"\b2026\b", name):
        score += 10_000
    if "version 1" in name:
        score -= 50_000
    if "(1)" in name:
        score -= 5_000
    if name.endswith(" v2.docx") or "_v2" in name:
        score += 20_000
    if "long" in name:
        score += 15_000
    return score


def para_to_html(para: Paragraph) -> str:
    chunks: list[str] = []
    for run in para.runs:
        t = html.escape(run.text)
        if not t:
            continue
        if run.bold:
            t = f"<strong>{t}</strong>"
        if run.italic:
            t = f"<em>{t}</em>"
        chunks.append(t)
    inner = "".join(chunks).strip()
    if not inner:
        return ""
    style = (para.style.name or "").lower() if para.style else ""
    if style.startswith("heading 1"):
        return f"<h2>{inner}</h2>"
    if style.startswith("heading 2"):
        return f"<h3>{inner}</h3>"
    if style.startswith("heading 3"):
        return f"<h4>{inner}</h4>"
    return f"<p>{inner}</p>"


def extract_doc(path: Path) -> tuple[list[str], str, int]:
    doc = Document(path)
    plain_lines: list[str] = []
    html_parts: list[str] = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            plain_lines.append(text)
        block = para_to_html(para)
        if block:
            html_parts.append(block)
    body = "\n".join(html_parts)
    word_count = len(re.sub(r"<[^>]+>", " ", body).split())
    return plain_lines, body, word_count


def pick_title(plain_lines: list[str], filename: str) -> tuple[str, str | None]:
    """Returns (title, header_line). header_line is the d'var Torah line if present."""
    lines = [ln for ln in plain_lines if ln.strip()]
    header = None
    idx = 0
    if not lines:
        base = Path(filename).stem
        return re.sub(r"[_]+", " ", base), None
    first = lines[0]
    if re.search(r"d[''']?var|dvar\s+torah|parshat|parshas|parashat", first, re.I):
        header = first.lstrip("zZ").strip()
        idx = 1
    while idx < len(lines) and len(lines[idx]) < 120:
        candidate = lines[idx].strip()
        idx += 1
        if candidate.lower().startswith("introduction"):
            continue
        if header and re.search(r"parshas?\s", candidate, re.I) and len(candidate) < 48:
            continue
        if len(candidate) < 120:
            return candidate, header
    if header:
        return header, header
    return lines[0], None


def body_after_title(html_body: str, plain_lines: list[str], title: str, header: str | None) -> str:
    """Drop leading paragraphs that duplicate title/header in the HTML."""
    skip_texts = {title.strip()}
    if header:
        skip_texts.add(header.strip())
        skip_texts.add("z" + header.strip())
    parts = re.split(r"(?=<h[234]>|<p>)", html_body)
    out: list[str] = []
    started = False
    for part in parts:
        if not part.strip():
            continue
        inner = re.sub(r"<[^>]+>", "", part).strip()
        if not started and inner in skip_texts:
            continue
        if not started and inner.lower().startswith("introduction:"):
            started = True
        if inner:
            started = True
        if started:
            out.append(part)
    return "".join(out) if out else html_body


def dedup_key(path: Path, parsha: str | None, holiday: str | None, title: str) -> str:
    name = path.stem.lower()
    if "diburim_bereishit" in name or "kuntres bereishit" in name:
        return "kuntres:bereishit-diburim"
    if "kuntres" in name or "sefer devarim" in name:
        if "bereish" in name:
            return "kuntres:bereishis"
        return "kuntres:devarim"
    if "sefer_bereishis" in name:
        return "kuntres:sefer-bereishis"
    if holiday and not parsha:
        return f"holiday:{slugify(holiday)}"
    if parsha:
        title_slug = slugify(title)[:40]
        # Same parsha, clearly different titles → separate pieces
        if title_slug and title_slug not in slugify(parsha):
            return f"parsha:{slugify(parsha)}:{title_slug}"
        return f"parsha:{slugify(parsha)}"
    return f"file:{slugify(path.stem)}"


def kind_for(
    parsha: str | None, holiday: str | None, path: Path
) -> str:
    name = path.name.lower()
    if "kuntres" in name or "sefer_bereishis" in name:
        return "kuntres"
    if holiday:
        return "holiday"
    return "parsha"


@dataclass
class Candidate:
    path: Path
    score: int
    key: str
    piece: dict


SKIP_TITLE_PATTERNS = (
    re.compile(r"thank you for calling", re.I),
)


def should_skip(path: Path, title: str, words: int) -> str | None:
    if words < 80:
        return "too short"
    for pat in SKIP_TITLE_PATTERNS:
        if pat.search(title) or pat.search(path.name):
            return "excluded placeholder"
    return None


def build_piece(path: Path) -> Candidate:
    plain, html_body, words = extract_doc(path)
    title, header = pick_title(plain, path.name)
    skip = should_skip(path, title, words)
    if skip:
        raise ValueError(skip)
    parsha = detect_parsha(path.name, plain)
    holiday = detect_holiday(path.name, plain)
    occasion = detect_occasion(path.name, plain)
    html_body = body_after_title(html_body, plain, title, header)

    key = dedup_key(path, parsha, holiday, title)
    if key.startswith("kuntres:"):
        piece_id = slugify(key.split(":", 1)[1])
    elif key.startswith("holiday:"):
        piece_id = slugify(holiday or key.split(":", 1)[1])
    elif key.count(":") >= 2:
        base = slugify(parsha or "torah")
        suffix = slugify(title)[:36]
        piece_id = f"{base}-{suffix}" if suffix and suffix != base else base
    elif parsha:
        piece_id = slugify(parsha)
    else:
        piece_id = slugify(title) or slugify(path.stem)

    is_kuntres = key.startswith("kuntres:")
    if is_kuntres:
        parsha = None
    sefer = SEFER_BY_PARSHA.get(parsha) if parsha else None
    if is_kuntres and "bereish" in path.name.lower():
        sefer = "Bereishis"
    if not sefer and "devarim" in path.name.lower() and "kuntres" in path.name.lower():
        sefer = "Devarim"

    series = None
    lower = path.name.lower()
    if "kuntres" in lower or "sefer_bereishis" in lower:
        series = "Kuntres"
    elif "_diburim" in lower or " diburim" in lower or "full_diburim" in lower:
        series = "Diburim"
    else:
        series = "Weekly Torah"

    piece: dict = {
        "id": piece_id,
        "title": title,
        "kind": "kuntres" if is_kuntres else kind_for(parsha, holiday, path),
        "series": series,
        "sourceFile": path.name,
    }
    if parsha:
        piece["parsha"] = parsha
    if holiday:
        piece["holiday"] = holiday
    if occasion:
        piece["occasion"] = occasion
    if sefer:
        piece["sefer"] = sefer
    piece["categories"] = ["torah"]
    if piece["kind"] == "kuntres":
        piece["categories"].append("series")

    return Candidate(
        path=path,
        score=file_score(path) + words,
        key=key,
        piece=piece,
    )


def main() -> None:
    if not IMPORT_DIR.is_dir():
        raise SystemExit(f"Import folder missing: {IMPORT_DIR}")

    paths = sorted(IMPORT_DIR.glob("*.docx"))
    by_key: dict[str, Candidate] = {}
    skipped: list[dict] = []

    excluded: list[dict] = []

    for path in paths:
        try:
            cand = build_piece(path)
        except ValueError as e:
            excluded.append({"file": path.name, "reason": str(e)})
            continue
        prev = by_key.get(cand.key)
        if prev is None or cand.score > prev.score:
            if prev is not None:
                skipped.append(
                    {
                        "kept": cand.path.name,
                        "dropped": prev.path.name,
                        "key": cand.key,
                        "reason": "lower score",
                    }
                )
            by_key[cand.key] = cand
        else:
            skipped.append(
                {
                    "kept": prev.path.name,
                    "dropped": path.name,
                    "key": cand.key,
                    "reason": "lower score",
                }
            )

    chosen = sorted(by_key.values(), key=lambda c: (c.piece.get("sefer") or "ZZZ", c.piece.get("parsha") or c.piece["title"]))

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    catalog_pieces: list[dict] = []
    used_ids: set[str] = set()
    this_week_id = None

    for cand in chosen:
        plain, html_body, _ = extract_doc(cand.path)
        title, header = pick_title(plain, cand.path.name)
        html_body = body_after_title(html_body, plain, title, header)

        meta = {k: v for k, v in cand.piece.items() if k != "sourceFile"}
        pid = meta["id"]
        if pid in used_ids:
            n = 2
            while f"{pid}-{n}" in used_ids:
                n += 1
            pid = f"{pid}-{n}"
            meta["id"] = pid
        used_ids.add(meta["id"])
        catalog_pieces.append(meta)

        article_path = ARTICLES_DIR / f"{meta['id']}.json"
        article_path.write_text(
            json.dumps({"body": html_body, "bodyFormat": "html"}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        pid = meta["id"]
        if pid in THIS_WEEK_PARSHA_SLUGS or slugify(meta.get("parsha") or "") in THIS_WEEK_PARSHA_SLUGS:
            this_week_id = pid
        if meta.get("parsha") == "Chayei Sara" and this_week_id is None:
            this_week_id = meta["id"]

    catalog = {"thisWeekId": this_week_id, "pieces": catalog_pieces}
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for old in ARTICLES_DIR.glob("*.json"):
        if old.name == "README.md":
            continue
        if old.stem not in used_ids:
            old.unlink()

    report = {
        "imported": len(catalog_pieces),
        "sourceFiles": len(paths),
        "excluded": excluded,
        "skippedDuplicates": skipped,
        "thisWeekId": this_week_id,
        "pieces": [{"id": p["id"], "title": p["title"], "parsha": p.get("parsha"), "sourceFile": c.path.name} for c, p in zip(chosen, catalog_pieces)],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(catalog_pieces)} pieces from {len(paths)} docx files.")
    print(f"thisWeekId={this_week_id}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
