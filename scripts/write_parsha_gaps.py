#!/usr/bin/env python3
"""Regenerate scripts/PARSHA_GAPS.md from catalog + calendar (no id migration)."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog.json"
CALENDAR = ROOT / "data" / "parsha-calendar.json"
GAPS = ROOT / "scripts" / "PARSHA_GAPS.md"
CYCLE_START = "2025-10-18"
CYCLE_END = "2026-09-19"


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    cal = json.loads(CALENDAR.read_text(encoding="utf-8"))
    pieces = catalog["pieces"]

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

    lines = [
        "# Parsha coverage (5786–5787, Diaspora)",
        "",
        f"Calendar: `data/parsha-calendar.json` ({cal.get('locationLabel', 'Hebcal')}).",
        f"Shabbat `date` on each piece prefers the **2026** reading when Hebcal lists the sedra twice.",
        "",
        f"**Weekly parsha labels in catalog:** {len(have)}",
        f"**Sedra slots (Oct 2025–Sep 2026):** {len(cycle_parshas)}",
        "",
        "## Missing (no weekly piece for this sedra)",
        "",
    ]
    for m in missing:
        lines.append(f"- {m}")
    lines.extend(["", "## Multiple essays for one parsha", ""])
    counts = Counter(
        p.get("parsha")
        for p in pieces
        if p.get("kind") == "parsha" and p.get("parsha")
    )
    for parsha, n in sorted(counts.items()):
        if n > 1:
            ids = [x["id"] for x in pieces if x.get("parsha") == parsha]
            lines.append(f"- **{parsha}** ({n}): `{ '`, `'.join(ids) }`")
    lines.extend(["", "## Kuntres / holiday (not counted as sedra gaps)", ""])
    for p in pieces:
        if p.get("kind") == "kuntres" or p.get("holiday"):
            lines.append(f"- `{p['id']}` — {p.get('title', '')[:60]}")
    GAPS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {GAPS}")


if __name__ == "__main__":
    main()
