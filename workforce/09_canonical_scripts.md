# 09 — Canonical Scripts

## Added 2026-07-08 (outreach ops, agent ops, dedup, triggers)

| Script | Purpose |
|--------|---------|
| `enrich_reviews.py` | **Trust-locked** review enrichment: reads a lead's OWN Google reviews via exact `place_id` + phone match (never a name search), reasons the pain, writes to the exact CRM lead + `leads_reviews.csv`. Feeds `{trigger_line}`. |
| `email_send.py` | Single transactional/test email via Zoho (`--via zoho\|snov`, `--html`, `--signature-file`). Bulk outreach = Snov campaigns (dashboard). |
| `baian_send.py` / `check_baian_templates.py` | WhatsApp send via Baian (cloud-only) / list template approval status. |
| `deploy_agents.py` | Push each agent's `system_prompt` from `agents/*.md` to the cloud (in-place). |
| `set_agent_models.py` | Apply the model/escalation/max_turns cost policy to agents (in-place). |

---


> **`scripts/` was pruned 65 → 29** on 2026-07-06 (deleted `test_*`, `debug_*`,
> `inspect_*`, superseded dups), then **cleaned again 2026-07-07** (removed sync
> one-offs, bundle/openapi JSON dumps, and Baian draft payloads) and **+2 Baian
> scripts added** → **31 keepers**.
>
> **Do not recreate the deleted experiments** — if an endpoint needs probing,
> do it inline.

---

## Setup / Runtime

| Script | Purpose |
|--------|---------|
| `setup_db.py` | One-time DB init. Imports every SQLAlchemy model (including `app.scheduler.models`) and runs `create_all`. Cross-platform, no `-e PYTHONPATH=/app` needed. |
| `fix_runtime.py` | Switches workforce `runtime_mode` from `claw_code` to `claude_max`. Step 5 only reads/prints `model_name` (does not set it). |
| `check_runtime.py` | Verifies runtime mode + model for all agents. Reports any drift. |

## Lead Fetch

| Script | Purpose |
|--------|---------|
| `fetch_leads.py` | Google Places API lead fetcher. Text search by vertical + Riyadh location bias. Outputs `leads.csv`. |

## Clean / Dedup

| Script | Purpose |
|--------|---------|
| `step1_clean.py` | Stage 1 cleaner: address validation, phone regex, domain extraction. |
| `graphql_dedup.py` | English-name dedup vs Twenty CRM via GraphQL. Uses `first` + `after` + `cursor` (REST pagination is broken). |
| `crosslang_dedup.py` | Cross-language (Arabic ↔ English) dedup via transliteration + domain/phone/address overlap. |

## Enrich

| Script | Purpose |
|--------|---------|
| `enrich_emails.py` | Website crawl (homepage + 10 contact paths) + DuckDuckGo search. Found 4 new emails. |
| `fetch_emails_snov.py` | Snov.io v2 email fetcher (start task → poll for results). |
| `step2_snov_v2.py` | Snov.io v2 orchestrator (handles async polling). |
| `step2_snov_verify.py` | Snov.io v2 verification step. |

## Verify

| Script | Purpose |
|--------|---------|
| `verify_all_emails.py` | Snov.io v2 email verification for all leads. Updates `leads_enriched.csv` with `email_status`. |
| `verify_import.py` | Post-import verify — GraphQL `totalCount` check vs expected counts. |

## Import

| Script | Purpose |
|--------|---------|
| `import_all_leads.py` | Bulk import to Twenty CRM. 0.5s rate limit. Creates 35 companies + 35 people. |

## CRM Utils

| Script | Purpose |
|--------|---------|
| `configure_twenty.py` | Configure Twenty CRM connection (token, base URL). |
| `get_crm_schema.py` | Dump Twenty CRM schema (Company, Person fields). |
| `query_twenty.py` | Generic GraphQL query helper. |
| `dump_crm.py` | Dump all companies + contacts to JSON. |
| `gen_integration_sql.py` | Generate integration SQL from config. |

## Checks

| Script | Purpose |
|--------|---------|
| `check_snov_credits.py` | Check Snov.io credit balance. |
| `check_email_status.py` | Check current email verification status for all leads. |
| `check_cloud_integrations.py` | Check which integrations are connected on the cloud workforce. |

## WhatsApp (Baian) — cloud-only

| Script | Purpose |
|--------|---------|
| `baian_send.py` | Send a WhatsApp via Baian: `--to`, `--template`. Creates a cloud task → approves plan → prints `message_id`. See `playbooks/whatsapp_send_baian.md`. |
| `check_baian_templates.py` | Read-only: list Baian templates + Meta approval status (paginates all pages). |
| `manage_wa_templates.py` | Prune/fix the Meta template set via **direct Graph API** (cloud task → Tariq). Modes: `run1` (delete dup + rejected, recreate, sweep superseded/artifacts), `recreate` (create the `_v2` finance/training under the approved realestate structure), `inspect --ids` (GET exact approved bodies), `finalize` (delete `_t1` originals — only after `_v2` APPROVED). |

## Task Ops

| Script | Purpose |
|--------|---------|
| `create_lead_task.py` | Create a new lead-finding task assigned to Tariq. |
| `monitor_task.py` | Monitor a running task (poll status, log progress). |
| `check_task_status.py` | One-shot task status check. |
| `approve_task.py` | Approve a `WAITING_PLAN` task (resume with approval). |
| `reset_task.py` | Reset a stuck/failed task. |
| `update_csv_task.py` | Update task input CSV (re-point at a new dataset). |
| `update_task_with_key.py` | Update task description with an API key (for in-container use). |

---

## Why these scripts exist (context for the scripting model)

The `moonshotai/kimi-k2.6` model via the `navaia` CLI produced malformed JSON
for complex tool calls during the first lead-finding run (bash commands with
multi-line scripts). For reliable data fetching, the pipeline uses **direct
Python scripts** rather than relying on the agent runtime. The agent
orchestrates; the scripts do the work.

This is a deliberate architectural choice documented in §10.8 of the original
spec. **Do not "fix" this by trying to make the agent do the fetching** —
keep the scripts.

---

## Deleted Experiments (do not recreate)

These were deleted on 2026-07-06 per the "useful data upfront, no junk" rule:

| Category | Count | Why deleted |
|----------|-------|-------------|
| `test_*` | many | Throwaway test scripts |
| `debug_*` | several | One-off debugging artifacts |
| `inspect_*` | several | Schema/format inspection one-liners |
| Superseded duplicates | several | Old versions of canonical scripts |
| **Total deleted** | **36** | |

If you need a script that doesn't exist, write it inline (e.g., in a Python
REPL or a one-liner in the shell). Don't add new files to `scripts/` unless
they're a real, reusable pipeline stage.

---

## Pipeline Order (canonical)

```bash
# 1. Setup (one-time per fresh install)
python scripts/setup_db.py

# 2. Lead fetch
python scripts/fetch_leads.py

# 3. Clean
python scripts/step1_clean.py

# 4. Enrich
python scripts/enrich_emails.py
python scripts/fetch_emails_snov.py

# 5. Verify
python scripts/verify_all_emails.py

# 6. Import
python scripts/import_all_leads.py

# 7. Post-import verify
python scripts/verify_import.py

# 8. Review enrichment (trust-locked)
python scripts/enrich_reviews.py
```

> **No dedup steps.** The Twenty CRM backend handles duplicate elimination automatically — never run agent-side dedup. The dedup scripts (`graphql_dedup.py`, `crosslang_dedup.py`) are kept as manual one-off reconciliation tools only.
>
> **Single source of truth:** Twenty CRM. `leads_enriched.csv` from the initial Phase-1 run is historical reference only.