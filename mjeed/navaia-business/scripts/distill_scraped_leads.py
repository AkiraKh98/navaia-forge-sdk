#!/usr/bin/env python3
"""
Distill a gosom/google-maps-scraper results CSV into a compact JSON lead list
small enough to embed in a cloud task description (the cloud runtime has no
browser/Docker, so the scrape runs on a laptop and the DATA travels with the
task — see workforce/playbooks/lead_pipeline.md).

Keeps only phone-bearing rows; per lead: name, sector guess (from category +
Arabic/English name keywords; empty = let Tariq qualify), address, phone,
website, rating/review_count, place_id, and up to 2 short negative-review
snippets as pain hints (feeds Lina's pain_line — same-listing = trust-locked).

Usage:
    python scripts/distill_scraped_leads.py <scraped.csv> [out.json]
"""

import csv
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
csv.field_size_limit(10_000_000)  # review columns can be huge

SECTOR_KEYWORDS = {
    "Real Estate": ["عقار", "أملاك", "real estate", "property"],
    "Contracting & Facilities": ["مقاولات", "صيانة", "مرافق", "contracting", "maintenance", "facilit"],
    "Private Clinics": ["أسنان", "جلدية", "تجميل", "علاج طبيعي", "dental", "derma", "cosmetic", "physio"],
    "Finance & Debt Collection": ["تحصيل", "تمويل", "تقسيط", "debt", "finance", "installment"],
    "Training Institutes": ["تدريب", "معهد", "training", "institute"],
}


def guess_sector(name: str, category: str) -> str:
    hay = f"{name} {category}".lower()
    for sector, kws in SECTOR_KEYWORDS.items():
        if any(k in hay for k in kws):
            return sector
    return ""


def pain_hints(row: dict, limit: int = 2, max_len: int = 200) -> list[str]:
    """Short negative-review snippets from the same listing (trust-locked pain)."""
    hints = []
    try:
        for rv in json.loads(row.get("user_reviews") or "[]"):
            if (rv.get("Rating") or 5) <= 2 and rv.get("Description"):
                text = " ".join(rv["Description"].split())
                hints.append(text[:max_len])
                if len(hints) >= limit:
                    break
    except (json.JSONDecodeError, TypeError):
        pass
    return hints


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: distill_scraped_leads.py <scraped.csv> [out.json]")
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "leads_scraped_compact.json"

    leads, seen = [], set()
    with open(src, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("title") or "").strip()
            phone = (row.get("phone") or "").strip()
            if not name or not phone:
                continue
            key = (row.get("place_id") or name.lower(), phone)
            if key in seen:
                continue
            seen.add(key)
            leads.append({
                "name": name,
                "sector_guess": guess_sector(name, row.get("category") or ""),
                "category": (row.get("category") or "").strip(),
                "address": (row.get("address") or "").strip(),
                "phone": phone,
                "website": (row.get("website") or "").strip(),
                "rating": row.get("review_rating") or "",
                "review_count": row.get("review_count") or "",
                "place_id": row.get("place_id") or "",
                "pain_hints": pain_hints(row),
            })

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=1)

    by_sector: dict[str, int] = {}
    for l in leads:
        by_sector[l["sector_guess"] or "(unclassified)"] = by_sector.get(l["sector_guess"] or "(unclassified)", 0) + 1
    print(f"{len(leads)} phone-bearing leads -> {dst} ({sum(len(json.dumps(l, ensure_ascii=False)) for l in leads)} chars)")
    for s, n in sorted(by_sector.items(), key=lambda x: -x[1]):
        print(f"  {s}: {n}")


if __name__ == "__main__":
    main()
