# Playbook — Lead Pipeline (fetch → clean → dedup → enrich → verify → import)

> SOP for the lead pipeline. Runs as **direct Python scripts** (not agent tool calls):
> the `moonshotai/kimi-k2.6` runtime produced malformed JSON for complex tool calls, so
> the agent **orchestrates** and the **scripts do the work**. Do not "fix" this by making
> the agent fetch — keep the scripts. Full script reference: `../09_canonical_scripts.md`.

## Preconditions
- `.env` has `PLACES_API`, `TWENTY_TOKEN`, `SNOV_USER_ID`, `SNOV_USER_SECRET`.
- Local stack up + DB initialised (`scripts/setup_db.py`). See `deploy_and_sync.md`.
- Single source of truth dataset: `leads_enriched.csv` (gitignored — PII). All later
  stages read/write it.

## Steps (run in order)
```bash
.venv/Scripts/python.exe scripts/fetch_leads.py                    # 1. Google Places → leads.csv (Riyadh, 5 verticals). Keeps place_id.
.venv/Scripts/python.exe scripts/step1_clean.py                   # 2. address/phone/domain clean
.venv/Scripts/python.exe scripts/enrich_emails.py                 # 3a. website crawl + web search
.venv/Scripts/python.exe scripts/fetch_emails_snov.py             # 3b. Snov.io v2 email fetch (async)
.venv/Scripts/python.exe scripts/verify_all_emails.py             # 4. Snov.io v2 verify (.sa → "likely valid")
.venv/Scripts/python.exe scripts/import_all_leads.py              # 5. import to Twenty CRM (store place_id). NO dedup — CRM backend handles it. Count ACTUAL-added; top up until N new.
.venv/Scripts/python.exe scripts/verify_import.py                 # 6. confirm the ACTUAL added count (= what you were asked for)
.venv/Scripts/python.exe scripts/enrich_reviews.py --in leads_enriched.csv  # 7. TRUST-LOCKED review pain (place_id + phone verified) → leads_reviews.csv + CRM → feeds {trigger_line}
```
> **No dedup step (2026-07-08):** the **Twenty CRM backend measures/handles duplicates**, so
> the agent does NOT check for dups — that step is removed (it cost tokens for nothing). Add
> all leads; the CRM dumps duplicates; **count only what was ACTUALLY added.** When asked for
> **N** leads, if the added count is below N (CRM dumped some), **fetch + add more until N NEW
> records exist** — the number you report equals the number actually in the CRM.
> `graphql_dedup.py` / `crosslang_dedup.py` are kept only as **manual one-off** reconciliation
> tools, NOT part of the flow.
>
> **Review enrichment (step 7) is TRUST-LOCKED:** it reads a lead's Google reviews **only** via
> the exact `place_id` (never a name search) and **only** when the Places phone matches the
> lead's phone — so it can never pull a similarly-named different company. It then reasons the
> lead's specific pain from *those* reviews and appends it to the **exact** CRM lead.

## Hard rules
- **Real data only** — record only what a real source (Google Places / Overpass / Snov)
  returns. Never invent a field; leave unknowns empty.
- Every lead needs at least a phone or email. Riyadh region only.
- Twenty CRM link-object fields (`domainName`, `linkedinLink`, `annualRevenue`) are
  `{"primaryLinkUrl": …}`, not strings. `createdBy` is required. Use the 5 exact sector
  names. See `../agents/tariq_sdr_lead_fetcher.md` for schema + CRM quirks.

## Orchestration
Ahmed (GM) delegates "find leads" to **Tariq**. Tariq runs this pipeline, reports counts
back. Scoring/prioritisation model: `../05_lead_scoring_model.md`.
