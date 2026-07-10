#!/usr/bin/env python3
"""
Fetch 50 real business leads in Riyadh from Google Places API across 5 verticals.
Writes results to CSV file matching Twenty CRM schema for later import.
"""

import csv
import json
import os
import time
import urllib.request
import urllib.error

def _env_secret(name):
    v = os.environ.get(name)
    if v:
        return v
    try:
        env = open(os.path.join(os.path.dirname(__file__), "..", ".env")).read()
    except OSError:
        return None
    import re
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip() if m else None


API_KEY = _env_secret("PLACES_API")
if not API_KEY:
    raise SystemExit("Set PLACES_API (env var or .env)")
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
OUTPUT_CSV = os.environ.get("OUTPUT_CSV", "/app/workspace/leads.csv")

# Riyadh center: 24.7136, 46.6753, radius 50km
LOCATION_BIAS = {
    "circle": {
        "center": {"latitude": 24.7136, "longitude": 46.6753},
        "radius": 50000,
    }
}

FIELD_MASK = "places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.websiteUri,places.id,places.types,nextPageToken"

VERTICALS = [
    {
        "sector": "Contracting & Facilities",
        "tier": "Tier 1",
        "target": 10,
        "terms": [
            "contracting company Riyadh",
            "maintenance company Riyadh",
            "facilities management Riyadh",
        ],
    },
    {
        "sector": "Finance & Debt Collection",
        "tier": "Tier 1",
        "target": 10,
        "terms": [
            "debt collection Riyadh",
            "finance company Riyadh",
            "installment company Riyadh",
        ],
    },
    {
        "sector": "Private Clinics",
        "tier": "Tier 1",
        "target": 10,
        "terms": [
            "dental clinic Riyadh",
            "dermatology clinic Riyadh",
            "cosmetic clinic Riyadh",
            "physiotherapy clinic Riyadh",
        ],
    },
    {
        "sector": "Real Estate",
        "tier": "Tier 2",
        "target": 10,
        "terms": [
            "real estate company Riyadh",
            "property management Riyadh",
        ],
    },
    {
        "sector": "Training Institutes",
        "tier": "Tier 2",
        "target": 10,
        "terms": [
            "training institute Riyadh",
            "training center Riyadh",
        ],
    },
]


def search_places(text_query, page_token=None):
    """Call Google Places Text Search API and return results."""
    body = {"textQuery": text_query, "locationBias": LOCATION_BIAS, "pageSize": 20}
    if page_token:
        body = {"pageToken": page_token}

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": FIELD_MASK,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}")
        return {}
    except Exception as e:
        print(f"  Error: {e}")
        return {}


def extract_place_data(place, sector, tier):
    """Extract and filter a single place result."""
    name = ""
    display = place.get("displayName", {})
    if isinstance(display, dict):
        name = display.get("text", "")
    elif isinstance(display, str):
        name = display

    address = place.get("formattedAddress", "")
    phone = place.get("internationalPhoneNumber", "")
    website = place.get("websiteUri", "")
    place_id = place.get("id", "")

    # Filter: must have name
    if not name:
        return None

    # Filter: must have phone
    if not phone:
        return None

    # Filter: address must contain Riyadh
    if "riyadh" not in address.lower() and "الرياض" not in address:
        return None

    return {
        "company_name": name,
        "domain_name": website or "",
        "address": address,
        "phone": phone,
        "sector": sector,
        "vertical_tier": tier,
        "created_by": "Mjeed using [Tariq SDR Agent]",
        "lead_source": "Google-Places",
        "place_id": place_id,
    }


def main():
    all_leads = []
    seen_place_ids = set()
    seen_names = set()

    for v in VERTICALS:
        sector = v["sector"]
        tier = v["tier"]
        target = v["target"]
        terms = v["terms"]

        print(f"\n=== {sector} ({tier}) — target: {target} leads ===")
        vertical_leads = []

        for term in terms:
            if len(vertical_leads) >= target:
                break

            print(f"  Searching: {term}")
            page_token = None
            pages = 0

            while pages < 3 and len(vertical_leads) < target:
                pages += 1
                result = search_places(term, page_token)

                places = result.get("places", [])
                if not places:
                    print(f"    Page {pages}: no results")
                    break

                print(f"    Page {pages}: {len(places)} results")

                for place in places:
                    lead = extract_place_data(place, sector, tier)
                    if lead is None:
                        continue

                    # Deduplicate by place_id and name
                    pid = lead["place_id"]
                    cname = lead["company_name"].lower().strip()

                    if pid and pid in seen_place_ids:
                        continue
                    if cname and cname in seen_names:
                        continue

                    seen_place_ids.add(pid)
                    seen_names.add(cname)
                    vertical_leads.append(lead)
                    print(f"      + {lead['company_name']} | {lead['phone']}")

                    if len(vertical_leads) >= target:
                        break

                page_token = result.get("nextPageToken")
                if not page_token:
                    break

                # Google requires a short delay before using nextPageToken
                time.sleep(2)

            if len(vertical_leads) >= target:
                break

        print(f"  -> {sector}: {len(vertical_leads)} leads collected")
        all_leads.extend(vertical_leads)

    # Write CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = [
        "company_name",
        "domain_name",
        "address",
        "phone",
        "sector",
        "vertical_tier",
        "created_by",
        "lead_source",
        "place_id",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_leads)

    print(f"\n{'='*60}")
    print(f"TOTAL LEADS: {len(all_leads)}")
    print(f"CSV written to: {OUTPUT_CSV}")
    print(f"\nBreakdown by sector:")
    for v in VERTICALS:
        count = sum(1 for l in all_leads if l["sector"] == v["sector"])
        print(f"  {v['sector']} ({v['tier']}): {count}")
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
