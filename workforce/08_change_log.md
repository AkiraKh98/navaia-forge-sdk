# 08 — Change Log

> Chronological record of all decisions, fixes, and milestones for the
> NAVAIA Business workforce. Reconstructed from git history + the runtime
> scripts in `scripts/`.

---

## 2026-07-05

- Initial draft from user's workflow description.
- Updated verticals from co-founder strategy (5 verticals, 2 tiers). Twenty
  CRM active. Google Places API added. Snov.io scoped to enrichment only.
  E-commerce removed. General hospitals removed — private specialty clinics
  only.

## 2026-07-06

- **Runtime switched** from `claw_code` to `claude_max` (claw CLI missing in
  container).
- **First lead-finding run completed:** 50 leads from Google Places API, 25
  enriched with Snov.io emails. CRM was down — leads in CSV.
- **Added §10** with full execution results and findings.
- **CRM came back up.** Bulk import completed: 35 companies + 35 contacts
  created in Twenty CRM (609 → 645 companies).
- **Cross-language dedup** ran clean (0 dups).
- **Email verification + enrichment pipeline** built and ran.
- **Added §10.10** (Post-Import Pipeline) as the authoritative state
  reference for future sessions.
- **Added §11** (Outreach Strategy) as a placeholder for the next phase —
  pending user's answers to §11.1 questions and inbound-sales research.
- **Outreach strategy built out** (planning only — scripting handed off to
  a separate model). User locked 4 decisions: tone (formal but direct/brief),
  cadence (day 0/+3/+7), channel (email first, WhatsApp later, manual for
  high-priority), targeting (most-responsive contact, not executive-only).
- Ran two research sub-agents → folded findings into §11.3 (inbound-sales
  best practices) and §11.4 (free decision-maker/email lookup playbook).
- Added §11.5 (rules-based 0–100 scoring model) and §11.6 (template
  blueprint).
- **Identity resolved:** عبدالمجيد الوردي / Abdulmajeed Alwardi, نڤايا /
  NAVAIA, https://cal.com/abdulmajeed-alwardi. Drafted first-pass
  per-vertical value props (§11.2).
- Created `OUTREACH_TEMPLATES.md` with the Private Clinics reference
  sequence.
- **User override:** cal.com link + short brief now go in touch 1 (not gated
  behind a reply) — updated §11.6 and the templates accordingly;
  deliverability mitigation (warmed domain + plain-text link) noted for the
  sending model.
- **Touch-1 voice reworked** per user: conversational فصحى (warmth 5→6/10),
  fixed flow (pain subject → company pain → actions-not-how → impact as
  plain fact → regulatory assurance → link), **benefit bank of 3 real
  results** (cost −40–60%, profit +30%, staff productivity) with **2 chosen
  per lead**, MoH + PDPL compliance line stated clearly-not-overstated,
  **no middot bullets**, **4-line signature** (name / Business Development /
  phone / NAVAIA نڤايا). Updated §11.6.
- Positioning rule added: frame as **حلول (solutions), not منصّة (platform)**
  — platform implies work/onboarding for the reader; pair with a "works on
  your behalf, no extra load" clause and a "we start from…" framing.
- **Vertical correction:** earlier templates used a wrong generic set
  (restaurants/retail/professional services). Rebuilt on the **correct 5
  co-founder verticals** (§5.1). `OUTREACH_TEMPLATES.md` now has full
  3-touch sequences for all 5, each with its own pain line, benefit
  pairing, and **vertical-specific compliance** (SAMA for finance, MoH for
  clinics, REGA for real estate, TVTC for training, PDPL throughout).
- **Template copy fixes** per user:
  1. "وأتّصل بكم" → "لأتّصل بكم"
  2. Positive-reply now branches on whether they already booked via
     cal.com (check first, two replies A/B)
  3. "تعمل نيابةً عنكم" (works *instead of* you) → "تعمل إلى جانبكم"
     (works *alongside* you) throughout
  4. The +30% / 40–60% numbers were clinic-only — all other verticals now
     carry placeholders (`{نسبة الأثر}`, `{نسبة التحصيل}`,
     `{نسبة خفض التكاليف}`) for the user to fill.
- **Scripts pruned 65 → 29** — deleted 36 junk (all `test_*`, `debug_*`,
  `inspect_*`, and superseded duplicates); kept the real pipeline.
  Canonical set documented in §10.10.8.
- Gitignored `leads*.csv` (PII) and `scripts/*.json` dumps.
- **Junk data eliminated** ("useful data upfront" rule): deleted 9
  stale/intermediate/duplicate files. **`leads_enriched.csv` (36 leads) is
  now the single source of truth.**
- Handoff clarity for future sessions (any model): added a prominent
  **▶ NEXT STEP** block at the top. Refreshed **§9** — the stale "outreach
  In progress / needs cal.com+tone" row replaced with accurate
  Done/Blocked/Pending rows.
- **Added §0 Current Known-Good Setup + Fixes Applied** at the top of the
  spec — consolidates the actual running config (runtime `claude_max`,
  model `moonshotai/kimi-k2.6`, SDK 0.2.3, JWT→Bearer, DEBUG=true,
  `setup_db.py`) and the fixes that got there.
- Reconstructed §0 from git history + `scripts/fix_runtime.py` /
  `check_runtime.py`. Flags the `ASSESSMENT.md` example drift
  (navaia_code/claude-sonnet-4 is generic, not live).
- Fixed the templates signature to `تطوير الأعمال - Business Development`
  (no brackets, single dash) and regenerated the PDF.
- **Added per-vertical field vocabulary** — each sequence now weaves 2–3
  well-known Arabic field terms to signal domain familiarity, with a
  documented **Field lexicon** line per vertical: Contracting (عروض
  أسعار/RFQ, مناقصات وعطاءات, مواعيد تسليم العطاءات, عقود صيانة وقائية,
  SLA); Finance (محفظة التحصيل, أعمار الديون, الأقساط المتأخّرة, لوائح
  ممارسات التحصيل); Clinics (المراجعين, عدم الحضور/no-show, قائمة
  الانتظار, إشغال الجدول); Real Estate (الوحدات الشاغرة, المعاينة, دفعات
  الإيجار وسنداتها); Training (المتدربين, الالتحاق بالدفعة, المنافسات
  الحكومية, منصة اعتماد/Etimad).

## 2026-07-07

- **Impact numbers confirmed across verticals:** cost −40%, profit +30%.
  Replaced all placeholder tokens and clinic-only range (40–60%) with
  universal figures in both `OUTREACH_TEMPLATES.md` and the spec. Removed
  §9 blocker; updated NEXT STEP (item 1 no longer needs user input).
- **Agent roster restructured to the canonical 7 (boss directive):** the
  workforce is exactly Ahmed (GM), Tariq (SDR), Lina (Marketing), Ghida
  (Creative), Nora (Finance), Rashid (Strategy), Fahad (Account Manager).
  **Never invent agents.** Deleted the two invented standalone agents
  (`zoho_email_outreach_agent.md`, `baian_outreach_agent.md`) — outreach is a
  **capability**, not an agent. Reassigned: **Lina writes** all outreach copy;
  **Tariq sends** (email via **Snov.io campaign → Zoho mailbox**; WhatsApp via
  **Baian, cloud-only**). **Baian = cloud-execution only** (secret lives only in
  cloud; route WhatsApp tasks to cloud, never local). Ahmed's instructions now
  hold the **full capability map** of all 7 agents + the two hard rules. Each
  agent given an **Acceptable Tasks** section + a complete deploy-ready
  `system_prompt`. Reconciled README, `01_workforce_identity`,
  `02_end_to_end_flow`, `07_open_items_and_status`. No keys/secrets touched
  (`.env` and cloud integration config untouched; `10_integration_keys.md` holds
  only shapes). Next: deploy the workforce; thereafter change via PRs.
- **Baian WhatsApp VERIFIED end-to-end.** Two real messages delivered to the owner
  via cloud workforce → Tariq → Baian → Meta template (`meeting_confirmation`, then
  approved custom `navaia_connectivity_test_v1`). Learned: the cloud workforce executes
  tasks even in `draft` (no activation needed); first-contact needs a Meta-APPROVED
  template (`send_template`); new-template approval ≈ minutes; `waiting_blocked` does not
  self-resume. Captured as `playbooks/whatsapp_send_baian.md` + `scripts/baian_send.py` +
  `scripts/check_baian_templates.py`. Baian status corrected Blocked → Active.
- **Repo consolidated into a single executor-ready source of truth.** Renamed
  `workforce_export/` → `workforce/`. Merged + removed duplicate root docs
  (`WORKFLOW_SPEC.md`, `OUTREACH_TEMPLATES.md`) — content lives in `workforce/`. Added a
  root **`AGENTS.md`** entry point (open standard); repointed `START_HERE.md`. Added
  `workforce/playbooks/` (SOP runbooks) and `workforce/tasks/` (self-contained task specs
  — the "container holds only tasks" model). Cleaned `scripts/` (removed sync one-offs,
  bundle/openapi JSON dumps, Baian draft payloads; +2 Baian scripts) → 31 canonical.
  Deleted `logs/` (folded into `deploy_and_sync.md`) and `verification_report.md` (PII,
  superseded by `leads_enriched.csv`). SDK/platform files untouched; no secrets committed.

## 2026-07-08

- **Cloud workforce fully configured:** all 7 agents got their full `system_prompt`
  deployed (`deploy_agents.py`); model cost policy applied (`set_agent_models.py`) —
  kimi ceiling on Lina (customer-facing), qwen + `escalation_model=kimi` + tuned
  `max_turns` on the rest. Baian WhatsApp proven; email limits found + handed to tech
  team (`INTEGRATION_CAPABILITIES_AND_GAPS.md`). Company HTML signature saved to
  `assets/email_signature.html`.
- **Outreach doctrine adopted (HubSpot inbound, adapted to outbound):** buyer-2:1,
  question-close on its own line, <200 words, ≤3-word subjects, ≤5 touches, trigger-event
  openers, free-consult, speed-to-lead. Added to `03_outreach_strategy.md` + Lina's
  instructions (redeployed).
- **All 15 templates rewritten** to the doctrine (`04_outreach_templates.md`) with two new
  opener slots: `{trigger_line}` (from the trigger pass) and `{inbound_context}`
  (reserved/inactive until website inbound exists).
- **Dedup step removed** (boss directive): the **Twenty CRM backend handles duplicates**, so
  the agent no longer checks for dups (it cost tokens for nothing). Add all leads; the CRM
  dumps dups; **count only what was actually added** and **top up until N NEW records exist** —
  the reported number equals the count actually in the CRM. (`dedup_local.py` removed;
  `graphql_dedup`/`crosslang_dedup` kept only as manual reconciliation tools.)
- **Trust-locked review enrichment** (`enrich_reviews.py`, replaces `enrich_triggers.py`):
  reads a lead's OWN Google reviews via the exact `place_id` **and** a matching phone (never a
  name search that could hit a similarly-named business), reasons the specific pain from those
  reviews, and **updates the lead in place** (`pain_line`/`pain_date`, preserving every column
  incl. `created_by`), idempotent, ~$0.0004/lead. **Validated on 5 real leads** → feeds `{trigger_line}`.
- **Handoff prepared** (`workforce/HANDOFF.md`): current state + hard rules + open items + next
  steps for the next CLI. `START_HERE.md` and `AGENTS.md` now point to it first. Boss directives
  captured as confirmed: model policy = kimi floor + frontier escalation (pending frontier
  confirm); dedup + email-send = boss mechanism + tech team (no agent-side dedup, no added cost).

## 2026-07-10

- **WhatsApp template set pruned + reconciled to the MJ option-B set** (via direct
  Graph API — Baian's create/delete tools were unreliable). Live Meta account 29 → 17.
  Deleted: the `navaia_mj_realestate_t1` **en** duplicate (by `hsm_id`, kept the `ar`), the
  4 superseded vertical originals (`navaia_clinics_t1`, `_v6`, `navaia_contracting_t1`,
  `navaia_realestate_t1`), and 5 stray MJ artifacts (`navaia_mj_clinics_t1_v2`/`_v3`,
  `navaiamjclinicst1`, `mjclinicst001`, `navaia_mj_contracting_t1_20260710_144937`).
  **Kept:** approved MJ set (`navaia_mj_clinics_t1`, `navaia_mj_contracting_t1`,
  `navaia_mj_realestate_t1`), the finance/training `_t1` originals as fallback, and all
  utility/test/survey templates.
- **Two hard Meta template rules discovered (root-causes the finance/training rejections):**
  1. **No trailing/leading variable** — a body may not end (or start) on a `{{n}}`
     (`error_subcode 2388299`). Every approved sibling carries **fixed text after `{{5}}`**
     (realestate: `{{5}}\nشاكراً لكم`) plus an `example.body_text`. Our original bodies ended
     on `{{5}}` with no example → INVALID_FORMAT.
  2. **30-day name lock** — a deleted template's name+language can't be reused for ~30 days
     (`error_subcode 2388023`, "language is being deleted").
- **Finance/training v2 APPROVED** — `navaia_mj_finance_t1_v2` / `navaia_mj_training_t1_v2`
  submitted (fresh `_v2` names to avoid 30-day lock on `_t1`), both polled to APPROVED.
  All 5 option-B MJ Touch-1 templates now live.
- `scripts/manage_wa_templates.py` refactored: removed the stale `run1` mode (which
  attempted an impossible recreate on locked `_t1` names). Added `cleanup` mode — deletes
  everything non-approved in one shot (superseded originals + test junk + old
  `navaia_finance_t1`/`navaia_training_t1`). The `inspect` / `recreate` / `finalize` modes
  remain. DUP_NAME/DUP_HSM_ID constants removed (only one realestate version now).
- Scrubbed a leaked Google Places API key from a FAILED task's `result` in the local DB
  (task `69795c7f`); key rotated in `.env`.

## Setup / SDK Fixes (from git history)

| Commit | Fix |
|--------|-----|
| `b55f0e3` | JWT auth header — SDK sent JWTs as `X-API-Key` → 401. Fixed `http.py` to detect `eyJ` prefix and send JWTs as `Authorization: Bearer`. |
| `b55f0e3` | `DEBUG=false` blocked startup — set `.env.example` to `DEBUG=true` for local dev. |
| `b55f0e3` → `b7b8cae` | DB tables not auto-created — added `scripts/setup_db.py`. |
| `b7b8cae` | Cross-platform DB setup — replaced inline `python -c` with `setup_db.py` + `sys.path` fix. |
| `eb291d2` | Scheduler tables missing — added `import app.scheduler.models` to `setup_db.py`. |
| `b7b8cae`, `c4ec6b4`, `f20f36b` | Version + doc drift — synced `__init__.py` to `0.2.3`; added default timeout; fixed README; pointed `pyproject.toml` + compose URLs to public repo; improved Windows notes. |

## Workforce / Runtime Fixes

| Item | Fix |
|------|-----|
| Runtime `claw_code` → `claude_max` | The `claw` CLI binary is not present in the container. Switched to `claude_max` (uses `claude` wrapper → `navaia -p` → OpenRouter). |
| Agent model = `moonshotai/kimi-k2.6` | Config fact, not a runtime-script fix. `fix_runtime.py` (step 5) and `check_runtime.py` only read/print the model; they don't set it. Model is set at agent creation. |
| Agent malformed JSON for complex tool calls | `moonshotai/kimi-k2.6` via `navaia` CLI produced malformed JSON for bash commands with multi-line scripts. Fallback: direct Python scripts (see `09_canonical_scripts.md`). |
| Container env vars | Only `OPENROUTER_API_KEY` is passed. Other vars must be embedded in task descriptions or added to `docker-compose.yml`. |