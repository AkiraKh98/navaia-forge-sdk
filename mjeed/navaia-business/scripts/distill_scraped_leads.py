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
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
csv.field_size_limit(10_000_000)  # review columns can be huge

# ACTIVE verticals — locked to three by operator decision 2026-07-19.
SECTOR_KEYWORDS = {
    "Real Estate": ["عقار", "أملاك", "real estate", "property"],
    "Contracting & Facilities": ["مقاولات", "صيانة", "مرافق", "contracting", "maintenance", "facilit"],
    "Training Institutes": ["تدريب", "معهد", "training", "institute"],
}

# RETIRED verticals — matched only so they can be DROPPED and counted, never emitted.
RETIRED_KEYWORDS = {
    "Private Clinics": ["أسنان", "جلدية", "تجميل", "علاج طبيعي", "dental", "derma", "cosmetic", "physio"],
    "Finance & Debt Collection": ["تحصيل", "تمويل", "تقسيط", "debt", "finance", "installment"],
}


def guess_sector(name: str, category: str) -> str:
    """Active vertical name, '' if unclassified, or 'RETIRED:<name>' to be dropped."""
    hay = f"{name} {category}".lower()
    for sector, kws in RETIRED_KEYWORDS.items():
        if any(k in hay for k in kws):
            return f"RETIRED:{sector}"
    for sector, kws in SECTOR_KEYWORDS.items():
        if any(k in hay for k in kws):
            return sector
    return ""


# Text that carries no describable pain no matter what star rating it was filed under.
# A 1-star review reading only "Nice" is real — people mis-click, or are sarcastic — and it
# reached outreach as شركة البرج اللامع's sole pain hint on 2026-07-20, guaranteeing a
# generic message. A low rating means the reviewer was unhappy; it does NOT mean the TEXT
# explains why, and only the text is usable downstream.
_PRAISE_ONLY = re.compile(
    r"^\W*(nice|good|great|ok+|fine|excellent|perfect|best|thanks?|thank you|"
    r"ممتاز|جيد|رائع|جميل|زين|تمام|شكرا|شكراً|جزاك الله خير|طيب|حلو|كويس|"
    r"[\U0001F300-\U0001FAFF☀-➿])\W*$", re.I)

# Complaints that map to something NAVAIA actually fixes: nobody answers, slow reply, no
# follow-up, missed calls, unreachable. Hints matching these are ranked FIRST, because only
# two survive and lina_compose can only match a pain that is present in the text it gets.
_RELEVANT = re.compile(
    r"(ما ?رد|ما ?يرد|لا ?يرد|لا ?يردون|ماردوا|ما ?ردوا|يرد علي|"
    r"ما ?يجاوب|لا ?يجيب|ما ?جاوب|"
    r"تأخر|تاخر|متأخر|بطيء|بطي|طولوا|ينتظر|انتظرت|"
    r"ما ?تواصل|لا ?تواصل|التواصل|يتواصل|متابعة|ما ?تابع|"
    r"مغلق|ما ?يفتح|الهاتف|الاتصال|اتصلت|مكالمة|واتس|"
    r"no reply|never answer|no answer|no response|didn'?t reply|didn'?t answer|"
    r"unreachable|slow response|no follow.?up|call(ed)? (them )?many times)", re.I)

# Below this a snippet is too short to describe anything ("سيء", "bad", "🙁").
_MIN_LEN = 25


def pain_hints(row: dict, limit: int = 2, max_len: int = 200) -> list[str]:
    """Usable negative-review snippets from the same listing (trust-locked pain).

    A hint is only worth carrying if a human could read it and name the problem. Filters
    out praise-only and too-short text even at 1 star, then puts complaints that match a
    pain we actually solve ahead of generic anger, since only `limit` survive.
    """
    candidates = []
    try:
        for rv in json.loads(row.get("user_reviews") or "[]"):
            if (rv.get("Rating") or 5) > 2 or not rv.get("Description"):
                continue
            text = " ".join(rv["Description"].split())
            if len(text) < _MIN_LEN or _PRAISE_ONLY.match(text):
                continue
            candidates.append(text[:max_len])
    except (json.JSONDecodeError, TypeError):
        return []

    # Stable sort: relevant complaints first, original review order preserved within groups.
    candidates.sort(key=lambda t: 0 if _RELEVANT.search(t) else 1)
    return candidates[:limit]


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: distill_scraped_leads.py <scraped.csv> [out.json]")
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "leads_scraped_compact.json"

    leads, seen = [], set()
    dropped_retired: dict[str, int] = {}
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
            sector = guess_sector(name, row.get("category") or "")
            if sector.startswith("RETIRED:"):
                v = sector.split(":", 1)[1]
                dropped_retired[v] = dropped_retired.get(v, 0) + 1
                continue
            leads.append({
                "name": name,
                "sector_guess": sector,
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
    if dropped_retired:
        print("dropped (RETIRED verticals, locked out 2026-07-19):")
        for s, n in sorted(dropped_retired.items(), key=lambda x: -x[1]):
            print(f"  {s}: {n}")


if __name__ == "__main__":
    main()
