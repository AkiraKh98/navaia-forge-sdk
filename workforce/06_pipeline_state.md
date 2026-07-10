# 06 — Pipeline State (Post-Import, as of 2026-07-06)

> **Authoritative reference for the current state of the data and CRM.**
> Read this before re-running dedup/enrichment/import scripts.

---

## CRM — Twenty CRM is live

- **Base URL:** `https://crm.navaia.sa`
- **Auth:** `TWENTY_TOKEN` in `.env` (header: `Authorization: Bearer <token>`)
- **REST endpoint:** `/rest/companies` (POST), `/rest/people` (POST with `companyId`)
- **GraphQL endpoint:** `/graphql` (use for pagination — see below)
- **Current state:** 645 companies, ~491 contacts. Of these, 36 are from the
  Riyadh lead run (35 bulk + 1 test = شركة اتقان العقارية).

---

## Critical CRM Quirks (don't re-discover these)

| Quirk | Detail |
|-------|--------|
| **REST pagination is broken** | `?after=<cursor>` is silently ignored. Always returns page 1. **Do not use REST for reads across pages.** |
| **GraphQL pagination works** | Use `first` + `after` + `cursor` on the `/graphql` endpoint. `scripts/graphql_dedup.py` is the working pattern. |
| **Link-object fields** | `domainName`, `linkedinLink`, `annualRevenue` are link objects: `{"primaryLinkUrl": "https://..."}`. Not strings. |
| **`createdBy` is required** | Format: `{"source": "AGENT", "name": "Mjeed using "}`. The trailing space is intentional (matches the test script's pattern). |
| **`address` is structured** | Use `{"addressStreet1": "..."}`. Not a flat string. |
| **Sector field** | Free-text on Company and Person. Use the 5 vertical names from §5.1 exactly. |
| **Person needs `companyId`** | UUID returned from `createCompany`. Confirmed working as `companyId` in the request body. |

---

## Pipeline Steps (in order — do not skip)

1. **Raw fetch** → `leads.csv` (50, first run) → `leads_to_import.csv` (48, second run)
2. **English-name dedup vs CRM** → `scripts/graphql_dedup.py` → `leads_clean.csv` (36 leads, 12 dups removed)
3. **Email enrichment (website crawl + web search)** → `scripts/enrich_emails.py` → `leads_enriched.csv` (36 leads, +4 new emails)
4. **Email verification (Snov.io v2)** → `scripts/verify_all_emails.py` → status updates in `leads_enriched.csv`
5. **Bulk import to CRM** → `scripts/import_all_leads.py` → 35 companies + 35 people created
6. **Cross-language dedup** → `scripts/crosslang_dedup.py` → confirmed 0 dups across 645 companies
7. **Post-import verify** → `scripts/verify_import.py` → GraphQL `totalCount` check

---

## Snov.io v2 — the Only Working Endpoints

| Purpose | Endpoint | Method | Notes |
|---------|----------|--------|-------|
| Start email verify | `/v2/email-verification/start` | POST | Body: `{"email": "..."}`. Returns `task_hash`. |
| Get email verify result | `/v2/email-verification/result?task_hash=<hash>` | GET | Returns `smtp_status`. |
| Start domain email search | `/v2/domain-search/domain-emails/start` | POST | Body: `{"domain": "..."}`. Returns `task_hash`. |
| Get domain email result | `/v2/domain-search/domain-emails/result/<task_hash>` | GET | Returns list of emails. |

**All other endpoint variants (`/v1/email-verifier`, `/v2/email-verifier`, etc.)
return 404. Do not retry them — they don't exist.**

**`.sa` domain caveat:** SMTP probes for Saudi domains return
`smtp_status: unknown` — the mail servers don't respond. Treat as "likely valid,
unverified at SMTP layer." Don't reject these leads for that reason.

**Snov.io credits:** 805 balance, resets in ~18 days from 2026-07-06.

---

## Cross-Language Dedup Approach (reuse this)

`scripts/crosslang_dedup.py` catches Arabic/English duplicate company names by:

1. Fetching all companies + contacts via GraphQL.
2. Normalizing: lowercase, strip diacritics, remove `شركة` / `مؤسسة` / `Co.` /
   `LLC` / `Ltd` / `Inc`.
3. **Transliteration match:** map Arabic chars to Latin equivalents (ا→a,
   ع→a/aa, ح→h, etc.) and compare.
4. **Domain match:** exact or suffix match (e.g. `saudico.com.sa` matches
   `www.saudico.com.sa`).
5. **Phone match:** normalize to digits only, last 9 digits must match.
6. **Address overlap:** token Jaccard similarity ≥ 0.6 on street/city tokens.

**Result on 2026-07-06:** 0 duplicates found across 645 companies.

---

## Current Data State (single source of truth)

**Junk cleanup done 2026-07-06:** all stale/intermediate/duplicate lead files
were eliminated. **`leads_enriched.csv` is now the one and only lead dataset** —
do not recreate the intermediates.

| File / Source | Rows | Status |
|---------------|------|--------|
| **`leads_enriched.csv`** | 36 | **THE dataset** — clean + enrichment + Snov verification. Columns: company_name, domain_name, address, phone, email, email_status, sector, vertical_tier, created_by, lead_source, place_id. |
| CRM (Twenty) | 645 companies | Includes 35 from this run + 1 test (اتقان) |
| CRM contacts | ~491 | Includes 35 from this run + 1 test |

**Before re-running import:** run `scripts/verify_import.py` and
`scripts/crosslang_dedup.py` to confirm no new collisions. The 35
already-imported companies are in CRM and will create dupes if
`leads_enriched.csv` is re-imported as-is.

---

## Lead CSV Schema (canonical)

```
company_name: Business name from Google Places
domain_name: Cleaned domain (e.g., saudico.com.sa)
address: Full formatted address from Google Places
phone: International phone number (+966...)
email: Email from Snov.io (if found, otherwise empty)
email_status: found_unverified | no_emails_in_snov | no_domain | email_domain_mismatch
sector: Contracting & Facilities | Finance & Debt Collection | Private Clinics | Real Estate | Training Institutes
vertical_tier: Tier 1 | Tier 2
created_by: Mjeed using [Tariq SDR Agent]
lead_source: Google-Places
place_id: Google Places ID (for dedup tracking)
```

---

## Eliminated Junk (deleted 2026-07-06 — do not recreate)

These were stale/intermediate/duplicate and have been **deleted** per the
"useful data upfront, no junk" rule. Listed so nobody re-generates them by
habit:

| File | Why it was junk |
|------|-----------------|
| `leads.csv`, `leads_final.csv`, `leads_verified.csv` | 50-row raw/intermediate first/second-run stages, superseded. |
| `leads_to_import.csv` | 48-row pre-dedup intermediate. |
| `leads_clean.csv` | 36-row subset of `leads_enriched.csv`. |
| `leads_verified_final.csv` | Byte-identical duplicate of `leads_clean.csv`. |
| `scripts/existing_crm_data.json` | Stale cache (claimed 21,500; actual 645). |
| `scripts/dedup_output.txt`, `scripts/test_crm.json` | Throwaway console dump / test artifact. |

---

## Per-Vertical Lead Counts (current dataset)

| Vertical | Tier | Leads |
|----------|------|-------|
| Contracting & Facilities | T1 | (in `leads_enriched.csv`) |
| Finance & Debt Collection | T1 | (in `leads_enriched.csv`) |
| Private Clinics (dental) | T1 | (in `leads_enriched.csv`) |
| Real Estate | T2 | (in `leads_enriched.csv`) |
| Training Institutes | T2 | (in `leads_enriched.csv`) |
| **Total** | | **36** |

Run `python -c "import pandas as pd; df = pd.read_csv('leads_enriched.csv'); print(df['sector'].value_counts())"` to see exact counts.

---

## Google Places API Configuration

- **Endpoint:** `POST https://places.googleapis.com/v1/places:searchText`
- **Location bias:** Riyadh center (24.7136, 46.6753), 50km radius
- **Field mask:** `displayName, formattedAddress, internationalPhoneNumber, websiteUri, id, types`
- **Key:** `PLACES_API` in `.env` (NOT passed to container — must be embedded
  in task descriptions or added to `docker-compose.yml`)

### Filtering rules
- Address must contain "Riyadh" or "الرياض"
- Must have international phone number (no phone = skip)
- Deduplicated by Google Places ID and company name
- No fabricated data — only real Google Places results

---

## Verification Process (how 50 leads became 36)

1. **Phone validation:** Regex for Saudi +966 format — all 50 passed
2. **Address validation:** Must contain "Riyadh" — all 50 passed
3. **Domain extraction:** Parsed from website URL, cleaned (removed protocol,
   www, path)
   - 40 leads have valid domains
   - 10 leads have no website (domain missing)
4. **Snov.io email count check** (v1 `get-domain-emails-count`, free API):
   - 27 domains have emails in Snov database
   - 13 domains have 0 emails
   - 10 leads have no domain
5. **Snov.io email discovery** (v2 `domain-search/domain-emails` +
   `generic-contacts`):
   - 25 leads with real email addresses found
   - 1 lead email cleared (BROS Dental — Instagram URL was treated as domain,
     produced `info@instagram.com`)
   - Email selection priority: info@ > contact@ > sales@ > admin@ > first
     available
6. **CRM dedup** (English name + domain): 12 dups removed → 36 leads
7. **Cross-language dedup:** 0 dups found
8. **Bulk import:** 35 created (1 excluded during final preflight)