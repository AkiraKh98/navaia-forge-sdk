# 07 — Open Items & Status (Done / Blocked / Pending)

> **Snapshot of what's done, what's blocked, and what's pending** as of
> 2026-07-10. This is the authoritative status reference for the workforce.

---

## Done

| Item | Note |
|------|------|
| **Twenty CRM** | Configured locally with token from `.env`. Base URL: `https://crm.navaia.sa`. REST + GraphQL both reachable. |
| **Twenty CRM dedup (English-name match)** | `scripts/graphql_dedup.py` — 48 raw leads → 36 clean. 12 dups removed by name + domain. **Historical (one-off)** — CRM backend now handles dedup automatically. |
| **Twenty CRM cross-language dedup (Arabic ↔ English)** | `scripts/crosslang_dedup.py` — transliteration + domain/phone/address overlap. 0 dups found across all 645 companies. **Historical (one-off)** — CRM backend now handles dedup automatically. |
| **Bulk import to Twenty CRM** | `scripts/import_all_leads.py` — 35 companies + 35 people created (شركة اتقان العقارية imported separately as test). 0.5s rate limit. |
| **Email verification pipeline (Snov.io v2)** | `scripts/verify_all_emails.py`. All 15 verified `.sa` emails return `smtp_status: unknown` — Saudi mail servers don't respond to SMTP probes. Treat as "likely valid, unverified at SMTP layer." |
| **Email enrichment (website crawl + web search)** | `scripts/enrich_emails.py` — homepage + 10 contact paths + DuckDuckGo. Found 4 new emails. |
| **Outreach templates (5 verticals × 3 touches)** | `04_outreach_templates.md` — formal Arabic, field vocab, per-vertical compliance, cal.com CTA, 4-line signature. Clean PDF: `NAVAIA_Outreach_Templates.pdf`. |
| **Outreach — impact numbers** | Confirmed across verticals: cost −40%, profit +30%. Placeholders replaced in templates. |
| **Lead scoring model** | Designed in `05_lead_scoring_model.md`. Rules-based 0–100 model. Implementation is scripting-model work. |
| **Runtime setup (claude_max + kimi-k2.6)** | Verified via `scripts/check_runtime.py`. |
| **DB init script** | `scripts/setup_db.py` works cross-platform, includes scheduler tables. |
| **SDK fixes** | JWT auth, DEBUG flag, version sync, doc drift — all resolved. |
| **Scripts pruned** | `scripts/` reduced from 65 → 29 (deleted all `test_*`, `debug_*`, `inspect_*`, and superseded duplicates). |
| **Baian (WhatsApp) — VERIFIED LIVE** | Cloud integration **ACTIVE** (`baian.navaia.sa`). Proven end-to-end 2026-07-07: cloud workforce (in `draft`, no activation needed) → Tariq → Baian → Meta template → owner's WhatsApp delivered. Two real messages sent (`meeting_confirmation`, then approved custom `navaia_connectivity_test_v1`). First-contact requires a Meta-**APPROVED** template via `send_template`; new templates approve in ~minutes. |
| **WhatsApp MJ template set — complete (5/5 verticals)** | 2026-07-10: All 5 option-B Touch-1 templates APPROVED — `navaia_mj_clinics_t1`, `navaia_mj_contracting_t1`, `navaia_mj_realestate_t1`, `navaia_mj_finance_t1_v2`, `navaia_mj_training_t1_v2`. Two hard Meta rules learned: (1) no trailing/leading `{{n}}` — needs fixed text after `{{5}}` + an `example`; (2) 30-day name lock after delete. Script refactored to `cleanup` mode (deletes junk in one shot, no recreate). |

---

## Blocked

| Item | Note | Unblock condition |
|------|------|-------------------|
| **Hunter.io record deletion** | Cloud backend returns HTTP 500 on DELETE/PUT. | Retry later or report to Navaia team. |

---

## Pending (handed to scripting model)

| Item | Note | Spec |
|------|------|------|
| **Outreach — sending / automation** | Lina writes → Tariq sends: merge Lina's copy + CRM leads, apply §11.5 score, send email via **Snov.io campaign → Zoho mailbox**; WhatsApp via **Baian (cloud-only)**. Planning session does NOT do this. | `agents/lina_marketing.md` + `agents/tariq_sdr_lead_fetcher.md` (Outbound Sending) + `04_outreach_templates.md` + `05_lead_scoring_model.md` |
| **Scheduler / pipeline automation** | Design after outreach sending is wired and tested. | TBD |
| **Additional agents** | Explore with user (e.g., inbound-lead-qualifier, meeting-scheduler, analytics). | TBD |

---

## What Still Needs User Input

> All design-blockers for the user are resolved as of 2026-07-07.
> Identity (name, company, cal.com, phone), tone, cadence, channel,
> targeting, impact numbers — all locked.

| Item | Status |
|------|--------|
| User's name | **Resolved** — عبدالمجيد الوردي / Abdulmajeed Alwardi |
| User's company | **Resolved** — نڤايا / NAVAIA |
| User's cal.com | **Resolved** — https://cal.com/abdulmajeed-alwardi |
| User's phone | **Resolved** — {{CONTACT_PHONE}} |
| Tone | **Resolved** — formal فصحى, direct/brief |
| Cadence | **Resolved** — day 0 / +3 / +7 |
| Channel | **Resolved** — email first, WhatsApp later |
| Targeting | **Resolved** — most-responsive contact, not executive-only |
| Impact numbers | **Resolved** — cost −40%, profit +30% (confirmed across verticals) |

**Nothing pending from the user for the planning phase.**

---

## Resume Checklist (for next session)

If you're picking this up cold:

1. **Read `workforce/README.md`** — orientation
2. **Read `workforce/00_setup_and_runtime.md`** — what's running
3. **Read `workforce/06_pipeline_state.md`** — current data state
4. **Read this file** — what's done/blocked/pending
5. If scripting model: start with the sending automation
6. If planning model: hand off to scripting model

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Snov.io credits run out | 805 balance, resets in ~18 days. Watch with `scripts/check_snov_credits.py`. |
| Snov.io `.sa` SMTP returns unknown | Accept "likely valid" — Saudi servers don't respond to probes. |
| Zoho sending domain not warmed | Ramp slowly: 20/day → 50/day over 1 week. |
| Baian token lives only on cloud | Token is in the cloud integration config (redacted locally, no local backup). Baian tasks MUST run on the cloud runtime; never expect a local `BAIAN_TOKEN`. |
| Twenty CRM pagination via REST broken | Always use GraphQL for reads across pages. |
| Container env vars not passed | Only `OPENROUTER_API_KEY` is in container env. Other vars must be embedded in task descriptions or added to `docker-compose.yml`. |
| Agent model produces malformed JSON for complex tool calls | Fall back to direct Python scripts (see `09_canonical_scripts.md`). |