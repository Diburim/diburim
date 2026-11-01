#!/usr/bin/env python3
"""Download Diaspora Shabbat parsha dates from Hebcal into data/parsha-calendar.json."""
from __future__ import annotations

import json
import re
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "parsha-calendar.json"

# NYC — common Diaspora default; edit geonameid in site config if you adopt Israel.
HEBCAL_URL = (
    "https://www.hebcal.com/hebcal/?v=1&cfg=json&s=on"
    "&start=2025-10-01&end=2026-11-15&geo=geoname&geonameid=5128581"
)
HOLIDAY_URL = (
    "https://www.hebcal.com/hebcal/?v=1&cfg=json&maj=on&min=on"
    "&start=2025-10-01&end=2026-11-15&geo=geoname&geonameid=5128581"
)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


# Hebcal title (after "Parashat ") → catalog `parsha` field
TITLE_TO_PARSHA: dict[str, str] = {
    "bereshit": "Bereishis",
    "noach": "Noach",
    "lech-lecha": "Lech Lecha",
    "vayera": "Vayera",
    "chayei-sara": "Chayei Sara",
    "toldot": "Toldot",
    "vayetzei": "Vayetzei",
    "vayishlach": "Vayishlach",
    "vayeshev": "Vayeshev",
    "miketz": "Miketz",
    "vayigash": "Vayigash",
    "vayechi": "Vayechi",
    "shemot": "Shemos",
    "vaera": "Vaera",
    "bo": "Bo",
    "beshalach": "Beshalach",
    "yitro": "Yitro",
    "mishpatim": "Mishpatim",
    "terumah": "Terumah",
    "tetzaveh": "Tetzaveh",
    "ki-tisa": "Ki Sisa",
    "vayakhel-pekudei": "Vayakhel-Pekudei",
    "vayikra": "Vayikra",
    "tzav": "Tzav",
    "shmini": "Shmini",
    "tazria-metzora": "Tazria-Metzora",
    "achrei-mot-kedoshim": "Acharei Mot-Kedoshim",
    "emor": "Emor",
    "behar-bechukotai": "Behar-Bechukotai",
    "bamidbar": "Bamidbar",
    "nasso": "Nasso",
    "behaalotcha": "Behaaloscha",
    "shlach": "Shlach",
    "korach": "Korach",
    "chukat-balak": "Chukat-Balak",
    "chukat": "Chukat",
    "balak": "Balak",
    "pinchas": "Pinchas",
    "matot-masei": "Matot-Masei",
    "devarim": "Devarim",
    "vaetchanan": "Vaetchanan",
    "eikev": "Eikev",
    "reeh": "Re'eh",
    "shoftim": "Shoftim",
    "ki-teitzei": "Ki Teitzei",
    "ki-tavo": "Ki Tavo",
    "nitzavim-vayeilech": "Nitzavim-Vayelech",
    "nitzavim": "Nitzavim",
    "vayeilech": "Vayelech",
    "haazinu": "Haazinu",
    "vezot-haberachah": "VeZot Haberachah",
}


def hebcal_title_to_parshas(title: str) -> list[str]:
    raw = title.replace("Parashat ", "").strip()
    key = norm(raw)
    if key in TITLE_TO_PARSHA:
        mapped = TITLE_TO_PARSHA[key]
        if mapped == "Chukat-Balak":
            return ["Chukat", "Balak"]
        if mapped == "Nitzavim-Vayelech":
            return ["Nitzavim", "Vayelech"]
        return [mapped]
    return []


def fetch(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=90) as resp:
        return json.load(resp)


def main() -> None:
    parsha_data = fetch(HEBCAL_URL)
    holiday_data = fetch(HOLIDAY_URL)

    readings: list[dict] = []
    for item in parsha_data.get("items", []):
        if item.get("category") != "parashat":
            continue
        parshas = hebcal_title_to_parshas(item.get("title", ""))
        readings.append(
            {
                "date": item["date"],
                "hebcalTitle": item.get("title"),
                "parshas": parshas,
            }
        )

    holidays: list[dict] = []
    for item in holiday_data.get("items", []):
        cat = item.get("category", "")
        if cat not in ("holiday", "yomtov", "roshchodesh"):
            continue
        title = item.get("title", "")
        if not any(
            k in title.lower()
            for k in ("pesach", "passover", "shavuot", "shavuos", "sukkot", "rosh hashana")
        ):
            continue
        holidays.append({"date": item["date"], "title": title, "category": cat})

    doc = {
        "approvedForMetadata": True,
        "source": "Hebcal",
        "sourceUrl": "https://www.hebcal.com/",
        "fetchedFrom": HEBCAL_URL,
        "locationLabel": "New York, NY (Diaspora)",
        "geonameid": 5128581,
        "notes": "Shabbat parsha dates for catalog `date` fields. Edit geonameid and re-run fetch_parsha_calendar.py for Israel or another city.",
        "readings": readings,
        "holidays": holidays,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(readings)} Shabbat readings to {OUT}")


if __name__ == "__main__":
    main()
