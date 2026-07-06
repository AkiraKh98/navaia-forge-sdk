# NAVAIA Business — Workforce Workflow Specification

> Living document. Iterate with the user until the workforce behaves exactly as needed.
> Last updated: 2026-07-06 (added §0 known-good setup + fixes; outreach templates done)

> **For future sessions: read §0 (Current known-good setup + fixes), §10.10
> (Post-Import Pipeline) and §11 (Outreach Strategy) before re-running any
> setup/lead/email/import work. The state of the setup, data, and CRM is
> documented there, not assumed.**

> ## ▶ NEXT STEP (as of 2026-07-06) — read before doing anything
>
> The outreach **templates are DONE** — see `OUTREACH_TEMPLATES.md` (5 verticals ×
> 3 touches, subjects, signature, positive-reply + Ramadan variants) and the strategy
> in §11. A clean PDF exists at `NAVAIA_Outreach_Templates.pdf`. **Do NOT rebuild the
> templates, and do NOT re-run lead-finding/enrichment/import — that is all finished
> (§9, §10.10).**
>
> What actually remains, in order:
>
> 1. **[Needs user input]** The non-clinic impact numbers are placeholders on purpose:
>    `{نسبة الأثر}`, `{نسبة التحصيل}`, `{نسبة خفض التكاليف}`. Clinics already have real
>    figures (+30% / 40–60%). **Do NOT invent numbers** — ask the user, then fill.
> 2. **[Scripting/execution model, NOT this planning session]** Wire sending: merge
>    templates with CRM lead data, apply the §11.5 lead score, send via the Zoho email
>    agent (§5.3); WhatsApp via Baian is **Blocked** until the team restores the token
>    (§9). Also still-blank: the sender's honorific/name per lead (`{honorific+name}`)
>    and each lead's `{pain_line}`.
> 3. **[Planning]** Optional: extend cadence to +10/+17 (proposed in §11.1, not approved).
>
> **Role boundary:** this repo/session is **planning only** — templates, specs, docs.
> All executable work (enrichment, verification, sending, import, the scoring pipeline)
> is done by a **separate scripting model** from a written spec. See the §11 scope note.
> If you are that scripting model, your spec is §11.5 (scoring) + §5.3/§5.2 (send) +
> `OUTREACH_TEMPLATES.md` (content).

---

## 0. Current Known-Good Setup + Fixes Applied

> **Read this first.** This is the authoritative record of how the setup/workflow/
> agent/workforce is *actually* configured and working now, plus the fixes that got
> it there. Reconstructed from git history + the runtime scripts in `scripts/`
> (`fix_runtime.py`, `check_runtime.py`, `setup_db.py`) — it is not the generic
> `ASSESSMENT.md` example (see the drift note at the end).

### 0.1 Known-good current config

| Piece | Current value |
|-------|---------------|
| Backend | Local Docker stack, `http://localhost:8001` (all execution + storage here) |
| Workforce | "NAVAIA Business" — local `8515d24a-6195-4a73-9cd3-37eb02f08693`, cloud `131bb52f-e5eb-44ad-8134-03dc6908b485` |
| **Runtime mode** | **`claude_max`** (NOT `claw_code` / `navaia_code`) |
| **Model (all agents)** | **`moonshotai/kimi-k2.6`** (valid on OpenRouter) |
| Agents | 7 pre-built (Ahmed GM + Tariq SDR + 5 future — see §3) |
| SDK version | `0.2.3` (PyPI, `__init__.py`/`pyproject.toml` synced) |
| Auth | JWT (`eyJ…`) → `Authorization: Bearer`; long-lived `nf_…` keys → `X-API-Key` |
| Local dev flag | `DEBUG=true` in `.env` (required locally) |
| DB init | `scripts/setup_db.py` (run once after first backend start) |

### 0.2 Fixes applied (what was broken → what fixed it)

**Setup / SDK (from git history):**

1. **JWT auth header** — SDK sent JWT tokens as `X-API-Key`, so the backend
   couldn't resolve the user → 401 "User not found" and 500 on API-key creation.
   Fixed `http.py` to detect the `eyJ` prefix and send JWTs as `Authorization:
   Bearer`; `nf_…` keys still go as `X-API-Key`. (SDK `0.2.3`, `b55f0e3` / `4e4a7dd`)
2. **`DEBUG=false` blocked startup** — backend refused to boot with localhost-only
   `ALLOWED_ORIGINS`. `.env.example` set to `DEBUG=true` for local dev. (`b55f0e3`)
3. **DB tables not auto-created** — the backend image does not auto-migrate, so a
   fresh install had no tables. Added `scripts/setup_db.py` that imports every
   SQLAlchemy model and runs `create_all`. (`b55f0e3` → `b7b8cae`)
4. **Cross-platform DB setup** — replaced the inline `python -c` one-liner (broke
   on Windows PowerShell quoting) with `setup_db.py`, plus a `sys.path` fix so it
   runs without `-e PYTHONPATH=/app`. (`b7b8cae`)
5. **Scheduler tables missing** — added `import app.scheduler.models` to
   `setup_db.py` so scheduler/pipeline tables are created. (`eb291d2`)
6. **Version + doc drift** — synced `__init__.py` to `0.2.3`; added a default
   timeout to `HttpConfig` (standalone WS example); fixed README (`send_message`
   takes no `agent_id`; `integrations.create` needs `workforce_id` + `config_json`);
   pointed `pyproject.toml` + compose download URLs to the public
   `NavaiaSolutions/navaia-forge-sdk`; improved Windows notes (`curl.exe`, setup
   script download). (`b7b8cae`, `c4ec6b4`, `f20f36b`)

**Workforce / runtime (from `scripts/fix_runtime.py`):**

7. **Runtime `claw_code` → `claude_max`** — the `claw` CLI binary is not present in
   the container, so tasks couldn't execute. Switched the "NAVAIA Business"
   workforce to `claude_max` (the `claude` wrapper calls `navaia -p`, routing
   through OpenRouter). Verify with `scripts/check_runtime.py`.
8. **Agent model = `moonshotai/kimi-k2.6`** — this is a *config fact*, not a fix by
   the runtime script: `fix_runtime.py` (step 5) and `check_runtime.py` only **read
   and print** each agent's `model_name` to confirm it; they do not set it. The
   model is configured at agent creation (per §3) and treated as valid on OpenRouter.

### 0.3 Drift to be aware of

`ASSESSMENT.md` (the candidate brief) still shows the *generic example* config —
`runtime_mode="navaia_code"` and `anthropic/claude-sonnet-4`. That is a template,
**not** the running workforce. The live workforce uses `claude_max` +
`moonshotai/kimi-k2.6` as in §0.1. Don't copy the assessment example values into
the real workforce.

---

## 1. Purpose

Run the "NAVAIA Business" workforce fully locally (Docker stack) while keeping it
two-way synced to the Fareegi cloud (`fareegi.navaia.sa`) for monitoring via the
dashboard (outputs, knowledgebase, chats, scheduler/pipeline).

The workforce is a business-development team. The user is a BD intern learning
sales and inbound capture, so the workflow must be **customizable** and
**expandable** — new data sources, new agents, and new outreach channels should
be addable without re-architecting the whole thing.

---

## 2. Workforce IDs

| Environment | Workforce ID |
|---|---|
| Local  | `8515d24a-6195-4a73-9cd3-37eb02f08693` |
| Cloud  | `131bb52f-e5eb-44ad-8134-03dc6908b485` |

Sync is bidirectional via `local.sync.push/pull(workforce_id, remote=cloud)`.
`origin_id` on every entity prevents duplication on round-trips.

---

## 3. Current Agents (pre-built in backend image)

| Name    | Role              | Notes |
|---------|-------------------|-------|
| Ahmed   | GM (orchestrator) | Pure orchestration — see §4 |
| Tariq   | SDR               | Lead fetching + outreach candidate |
| Lina    | Marketing         | Future expansion |
| Ghida   | Creative          | Future expansion |
| Nora    | Finance          | Future expansion |
| Rashid  | Strategy          | Future expansion |
| Fahad   | Account Manager   | Future expansion |

Runtime mode: `claude_max` (switched from `claw_code` — `claw` CLI binary not present in container; `claude` wrapper calls `navaia -p` which routes through OpenRouter)
Model (all agents): `moonshotai/kimi-k2.6` (verified valid on OpenRouter)
OpenRouter key: `OPENROUTER_API_KEY` in `.env` (already in container env)

---

## 4. GM Agent — Ahmed (Orchestrator)

**Principle:** Ahmed never executes domain work himself. He only routes, delegates,
and tracks.

### 4.1 Interaction Modes

1. **Task Assignment Mode**
   - A task is assigned to the workforce (via SDK or Fareegi dashboard).
   - Ahmed receives it, breaks it down, and delegates sub-tasks to the right
     specialist agents.
   - He tracks completion and re-routes if an agent fails or needs more input.

2. **Conversational Chat Mode**
   - The user (or another agent) chats with Ahmed directly.
   - Goal: let Ahmed grasp and fully understand the task/context before he
     delegates.
   - He asks clarifying questions, summarizes his understanding, and only once
     confident, spawns sub-tasks to the specialists.

### 4.2 Orchestration Responsibilities

- Parse the incoming task/request.
- Decide which specialist agent(s) are needed.
- Delegate with clear, scoped sub-task instructions.
- Aggregate results and report back to the requester.
- Escalate to the user when a step is blocked or ambiguous.
- Log everything to the Fareegi dashboard (outputs, chats).

### 4.3 Non-responsibilities

- Does not fetch leads himself.
- Does not write outreach templates himself.
- Does not send emails or WhatsApp messages himself.

---

## 5. Specialist Agents

### 5.1 Lead Fetcher Agent (Tariq / SDR)

**Goal:** Find real, targeted business leads in Riyadh region and store them
in Twenty CRM with full contact info. Never invent data — only record what is
verified from a real source.

#### Target Verticals (from Navaia co-founder strategy)

**Tier 1 — deepest pain, zero competition:**

1. **Contracting, Maintenance & Facilities Management** (المقاولات والصيانة وإدارة المرافق)
   - Pain: lose contracts every week because they have no proposals team.
   - Decision maker: owner directly.
   - Value measured by: won contract.

2. **Finance, Installment & Debt Collection** (التمويل والتقسيط ومكاتب التحصيل)
   - Pain: stuck debts = dead revenue, human collectors burn out and quit,
     SAMA regulations make a compliant agent an advantage.
   - Pricing model: percentage of collected amount (purest results-based).

3. **Private Specialty Clinics** (العيادات الخاصة) — dental, dermatology,
   cosmetic, physiotherapy only. NOT general hospitals.
   - Pain: bookings lost every night after hours, cancelled appointments with
     no follow-up, reception staff quit annually.
   - High margins = fast buying decision. Value = one booked appointment.

**Tier 2 — secondary:**

4. **Real Estate & Property Management** (العقار وإدارة الأملاك)
   - Pain: interested client goes cold in minutes without a reply, late rent
     collection links this sector to the debt-collection agent — a sector
     that buys two agents.

5. **Training Institutes** (معاهد التدريب)
   - Pain: registration season drowns them, they also bid on government
     training tenders — dual buyer.

#### Data Sources
- **Google Places API** (primary) — `PLACES_API` key in `.env`. Text search
  by vertical + Riyadh location bias. Returns: name, formatted address,
  international phone number, website, place types.
- **Overpass/OpenStreetMap** (secondary, free, no key) — backup for places
  Google doesn't return well.
- **Snov.io** (enrichment only) — use to find/verify contact emails for
  companies already discovered via Places. NOT for lead generation itself.
- Future: user-defined sources (LinkedIn, directories, inbound forms).

#### CRM — Twenty CRM (active)

Base URL: `https://crm.navaia.sa`
Token: `TWENTY_TOKEN` in `.env`

**Company schema (exact fields — fill all known, never invent):**
```
name: string (required)
domainName: { primaryLinkUrl: string }
address: { addressStreet1, addressStreet2, addressCity, addressPostcode,
           addressState, addressCountry, addressLat, addressLng }
sector: string — one of: "Contracting & Facilities", "Finance & Debt Collection",
        "Private Clinics", "Real Estate", "Training Institutes"
employeeCount: integer
annualRevenue: { amountMicros, currencyCode }
linkedinLink: { primaryLinkUrl }
createdBy: { source: "AGENT", name: "Mjeed", context: {} }
```

**Person schema (exact fields — fill all known, never invent):**
```
name: { firstName, lastName }
emails: { primaryEmail, additionalEmails: [] }
phones: { primaryPhoneNumber, primaryPhoneCountryCode, primaryPhoneCallingCode,
          additionalPhones: [] }
jobTitle: string
sector: string (same values as company sector)
companyId: UUID (link to company)
leadStatus: "Not Contacted"
leadSource: "Google-Places" | "Overpass-OSM" | "Snov-Enrichment"
leadScore: integer (0-100)
decisionMaker: boolean
linkedinLink: { primaryLinkUrl }
createdBy: { source: "AGENT", name: "Mjeed", context: {} }
```

**Rules:**
- Every lead MUST have at least a phone number or email (preferably both).
- Never invent data. If a field is unknown, leave it empty — do not guess.
- Check existing CRM records before adding to avoid duplicates.
- All leads must be localized in Riyadh region.
- `createdBy` is always `{ source: "AGENT", name: "Mjeed", context: {} }`.

#### Customization Hooks
- `lead_sources` — list of enabled sources (editable).
- `target_verticals` — the 5 verticals above (editable, tier-aware).
- `target_geography` — Riyadh region (expandable later).
- `enrichment_fields` — which contact fields are required vs. optional.

### 5.2 Baian Outreach Agent (WhatsApp + Email via Baian)

**Goal:** Send WhatsApp messages and emails through **Baian** (a NavaiaSolutions
product connected to Meta). Generate message templates dynamically based on the
GM's task and the receiver's context.

#### Capabilities (use Baian's built-in tools fully)
- WhatsApp message sending (via Meta / Baian).
- WhatsApp template generation (submitted to Meta through Baian).
- Email sending through Baian if Baian exposes that channel.
- The agent must **know which Baian tool to call for each action** — it should
  introspect Baian's capability list, not hardcode a single endpoint.

#### Template Generation Rules
- Generated per-task (from GM's instructions) and per-receiver (context-aware).
- Tone, language, and CTA adapt to the lead's profile and the outreach stage.
- Templates are reviewable in the Fareegi dashboard before sending (warm reach)
  or sent directly (cold reach) depending on configuration.

#### Configuration Hooks
- `default_language` — e.g., Arabic / English / bilingual.
- `tone` — formal, friendly, etc.
- `approval_required` — whether warm-reach templates need user approval first.
- `baian_capability_allowlist` — which Baian tools this agent may invoke.

### 5.3 Zoho Email Outreach Agent

**Goal:** Send warm-reach and cold-reach emails through the user's **Zoho Mail**
integration.

#### Modes
- **Warm reach:** personalized follow-ups to known contacts (e.g., after a
  WhatsApp reply or a prior interaction).
- **Cold reach:** first-touch outreach to new leads from the Lead Fetcher.

#### Behavior
- Pulls lead + context from the CRM file (Phase 1) or Twenty CRM (Phase 2).
- Drafts subject + body aligned with the GM's task.
- Sends via Zoho Mail integration.
- Logs the send + any reply to the Fareegi dashboard.

#### Configuration Hooks
- `reach_mode` — warm | cold | both.
- `daily_send_limit` — throttle.
- `signature` — user's Zoho signature block.
- `followup cadence` — optional auto-follow-up schedule (ties into scheduler).

---

## 6. Fareegi Dashboard Integration

The cloud dashboard is the monitoring surface. Everything the workforce does
should be visible there:

| Dashboard surface | What lands here |
|---|---|
| **Outputs**        | Lead lists, generated templates, sent emails, reports |
| **Knowledgebase**  | CRM file (Phase 1), lead enrichment notes, context docs |
| **Chats**          | GM conversations, agent-to-agent handoffs, user escalations |
| **Scheduler / Pipeline** | Automated outreach cadences, follow-ups, periodic lead-fetch runs |

Because sync is two-way, anything produced locally appears on cloud and any
task assigned on cloud flows down to local execution.

---

## 7. End-to-End Flow (happy path)

1. User assigns a task to the workforce (SDK or dashboard), e.g.
   "Find 20 SaaS founders in Riyadh and reach out."
2. **Ahmed (GM)** receives it, asks clarifying questions if needed (chat mode),
   then breaks it into sub-tasks.
3. Ahmed delegates to **Lead Fetcher**: "Find 20 SaaS founders in Riyadh,
   store with contacts in the CRM file."
4. Lead Fetcher runs, writes leads to the updatable CRM file, reports back.
5. Ahmed delegates to **Baian Outreach** and/or **Zoho Outreach** with the
   lead list + per-lead context + the task framing.
6. Outreach agents generate templates, send messages/emails, log results.
7. Ahmed aggregates outcomes, updates task status, surfaces to the user via
   the dashboard.
8. Replies / inbound signals flow back through the dashboard or sync, and
   Ahmed routes follow-ups.

---

## 8. Future Expandability

- **More agents** — the user wants to explore additional agents together
  (e.g., inbound-lead-qualifier, meeting-scheduler, analytics agent).
- **More data sources** — Lead Fetcher's source list is editable.
- **Twenty CRM** — swap the file CRM for the API once the account is ready.
- **Scheduler automation** — turn the happy path above into a scheduled
  pipeline (e.g., weekly lead-fetch + outreach cadence) via the Fareegi
  scheduler.
- **Agent enhancements** — each agent's instructions/tools can be iteratively
  refined through the SDK without touching the backend image.

---

## 9. Open Items / Status

| Item | Status | Note |
|---|---|---|
| Hunter.io record deletion | Blocked | Cloud backend returns HTTP 500 on DELETE/PUT. Retry later or report to Navaia team. |
| **Twenty CRM** | **Up** | Configured locally with token from `.env`. Base URL: `https://crm.navaia.sa`. REST + GraphQL both reachable. See §10.10 for current state. |
| **Twenty CRM dedup (English-name match)** | **Done** | `scripts/graphql_dedup.py` — 48 raw leads → 36 clean. 12 dups removed by name + domain. |
| **Twenty CRM cross-language dedup (Arabic ↔ English)** | **Done** | `scripts/crosslang_dedup.py` — transliteration + domain/phone/address overlap. 0 dups found across all 645 companies. |
| **Bulk import to Twenty CRM** | **Done** | `scripts/import_all_leads.py` — 35 companies + 35 people created (شركة اتقان العقارية imported separately as test). 0.5s rate limit. |
| **Email verification pipeline (Snov.io v2)** | **Done (with caveat)** | `scripts/verify_all_emails.py`. All 15 verified `.sa` emails return `smtp_status: unknown` — Saudi mail servers don't respond to SMTP probes. Treat as "likely valid, unverified at SMTP layer." |
| **Email enrichment (website crawl + web search)** | **Done** | `scripts/enrich_emails.py` — homepage + 10 contact paths + DuckDuckGo. Found 4 new emails. |
| Baian (WhatsApp) | Blocked | Token redacted on cloud, Baian service offline. Resume when team provides token. |
| **Outreach templates (5 verticals × 3 touches)** | **Done** | `OUTREACH_TEMPLATES.md` — formal Arabic, field vocab, per-vertical compliance, cal.com CTA, 4-line signature. Clean PDF: `NAVAIA_Outreach_Templates.pdf`. Decisions + research in §11. |
| Outreach — non-clinic impact numbers | **Blocked on user** | Placeholders `{نسبة الأثر}` / `{نسبة التحصيل}` / `{نسبة خفض التكاليف}` — clinics have real figures. Do NOT invent. See NEXT STEP at top. |
| Outreach — sending / automation | Pending (scripting model) | Merge templates + CRM leads, apply §11.5 score, send via Zoho email agent (§5.3); WhatsApp via Baian is Blocked. Planning session does NOT do this. |
| Lead scoring model | **Designed** | Rules-based 0–100 model specified in §11.5. Implementation is scripting-model work. |
| Scheduler/pipeline automation | Pending | Design after outreach sending is wired and tested. |
| Additional agents | Pending | Explore with user. |

---

## 10. Lead Finding — First Run Results (2026-07-06)

### 10.1 Task

Task ID: `69795c7f-9c17-456b-a0df-2093c4a15868`
Assigned to: Tariq (SDR)
Goal: Find 50 real business leads in Riyadh across 5 verticals (10 each)

### 10.2 Execution Path

1. Task created and assigned to Tariq via SDK
2. First attempt failed — `claw_code` runtime couldn't find `claw` CLI binary in container
3. **Fix**: Switched workforce `runtime_mode` from `claw_code` to `claude_max` (uses `claude` wrapper -> `navaia -p` -> OpenRouter)
4. Second attempt: agent produced a plan, entered `WAITING_PLAN` state
5. Plan approved, but agent produced another plan instead of executing (approval response not passed back to agent on resume)
6. **Fix**: Added `JDI:` prefix to task title to skip planning phase
7. Third attempt: agent executed, fetched leads from Google Places API, but blocked on CRM (DNS resolution failed for `crm.navaia.sa`)
8. **Fix**: CRM was down — rewrote task to output leads to CSV file instead
9. Fourth attempt: agent couldn't find `PLACES_API` env var (not passed to container)
10. **Fix**: Embedded API key directly in task description
11. Fifth attempt: agent model (`moonshotai/kimi-k2.6`) produced malformed JSON for tool calls
12. **Fix**: Wrote direct Python script (`scripts/fetch_leads.py`) to fetch leads from Google Places API — reliable, no agent dependency

### 10.3 Data Source

- **Google Places API** (Text Search) — `PLACES_API` key in `.env`
- Endpoint: `POST https://places.googleapis.com/v1/places:searchText`
- Location bias: Riyadh center (24.7136, 46.6753), 50km radius
- Field mask: displayName, formattedAddress, internationalPhoneNumber, websiteUri, id, types

### 10.4 Filtering Rules Applied

- Address must contain "Riyadh" or "الرياض"
- Must have international phone number (no phone = skip)
- Deduplicated by Google Places ID and company name
- No fabricated data — only real Google Places results

### 10.5 Results — 50 Leads Collected

| Vertical | Tier | Leads |
|----------|------|-------|
| Contracting & Facilities | Tier 1 | 10 |
| Finance & Debt Collection | Tier 1 | 10 |
| Private Clinics (dental) | Tier 1 | 10 |
| Real Estate | Tier 2 | 10 |
| Training Institutes | Tier 2 | 10 |
| **Total** | | **50** |

### 10.6 Verification Process

1. **Phone validation**: Regex for Saudi +966 format — all 50 passed
2. **Address validation**: Must contain "Riyadh" — all 50 passed
3. **Domain extraction**: Parsed from website URL, cleaned (removed protocol, www, path)
   - 40 leads have valid domains
   - 10 leads have no website (domain missing)
4. **Snov.io email count check** (v1 `get-domain-emails-count`, free API):
   - 27 domains have emails in Snov database
   - 13 domains have 0 emails
   - 10 leads have no domain
5. **Snov.io email discovery** (v2 `domain-search/domain-emails` + `generic-contacts`):
   - 25 leads with real email addresses found
   - 1 lead email cleared (BROS Dental — Instagram URL was treated as domain, produced `info@instagram.com`)
   - Email selection priority: info@ > contact@ > sales@ > admin@ > first available
6. **CRM dedup**: Deferred — CRM is down

### 10.7 Output Files

| File | Location | Description |
|------|----------|-------------|
| `leads.csv` | Project root + `/app/workspace/` | Raw leads from Google Places API (50 leads) |
| `leads_final.csv` | Project root | Final verified CSV with emails from Snov.io (50 leads, 25 with emails) |
| `verification_report.md` | Project root | Full verification report with per-lead breakdown |
| `scripts/fetch_leads.py` | scripts/ | Google Places API lead fetcher script |
| `scripts/quick_snov_count.py` | scripts/ | Snov.io free email count check |
| `scripts/fetch_emails_snov.py` | scripts/ | Snov.io v2 email fetcher |
| `scripts/clean_final.py` | scripts/ | CSV cleaner (removes fake emails, Instagram domains) |

### 10.8 Key Findings

- **Agent runtime limitation**: The `claw_code` runtime requires a `claw` CLI binary that doesn't exist in the container. The `claude_max` runtime works via the `claude` wrapper -> `navaia -p` -> OpenRouter pipeline.
- **Agent model limitation**: `moonshotai/kimi-k2.6` via the `navaia` CLI produces malformed JSON for complex tool calls (bash commands with multi-line scripts). For reliable data fetching, direct Python scripts are more effective than relying on the agent runtime.
- **Container env vars**: Only `OPENROUTER_API_KEY` is passed to the container. Other `.env` vars (`PLACES_API`, `TWENTY_TOKEN`, `SNOV_*`, `ZOHO_*`) are NOT available inside the container. Must be embedded in task descriptions or added to `docker-compose.yml`.
- **Snov.io API**: v1 endpoints (email count) work reliably. v2 endpoints (domain search) are async (start task -> poll for results) and slower. Many small Saudi businesses are not in Snov's database.
- **CRM availability**: `crm.navaia.sa` was down during this run. Leads written to CSV for later import.

### 10.9 CSV Schema (for CRM import)

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

### 10.10 Post-Import Pipeline (2026-07-06)

**This is the authoritative reference for the current state of the data and CRM.
Read this before re-running dedup/enrichment/import scripts.**

#### 10.10.1 CRM — Twenty CRM is now live

- **Base URL:** `https://crm.navaia.sa`
- **Auth:** `TWENTY_TOKEN` in `.env` (header: `Authorization: Bearer <token>`)
- **REST endpoint:** `/rest/companies` (POST), `/rest/people` (POST with `companyId`)
- **GraphQL endpoint:** `/graphql` (use for pagination — see below)
- **Current state:** 645 companies, ~491 contacts. Of these, 36 are from this
  Riyadh lead run (35 bulk + 1 test = شركة اتقان العقارية).

#### 10.10.2 Critical CRM quirks (don't re-discover these)

| Quirk | Detail |
|---|---|
| **REST pagination is broken** | `?after=<cursor>` is silently ignored. Always returns page 1. **Do not use REST for reads across pages.** |
| **GraphQL pagination works** | Use `first` + `after` + `cursor` on the `/graphql` endpoint. `scripts/graphql_dedup.py` is the working pattern. |
| **Link-object fields** | `domainName`, `linkedinLink`, `annualRevenue` are link objects: `{"primaryLinkUrl": "https://..."}`. Not strings. |
| **`createdBy` is required** | Format: `{"source": "AGENT", "name": "Mjeed using "}`. The trailing space is intentional (matches the test script's pattern). |
| **`address` is structured** | Use `{"addressStreet1": "..."}`. Not a flat string. |
| **Sector field** | Free-text on Company and Person. Use the 5 vertical names from §5.1 exactly. |
| **Person needs `companyId`** | UUID returned from `createCompany`. Confirmed working as `companyId` in the request body. |

#### 10.10.3 Pipeline steps (in order — do not skip)

1. **Raw fetch** → `leads.csv` (50, first run) → `leads_to_import.csv` (48, second run)
2. **English-name dedup vs CRM** → `scripts/graphql_dedup.py` → `leads_clean.csv` (36 leads, 12 dups removed)
3. **Email enrichment (website crawl + web search)** → `scripts/enrich_emails.py` → `leads_enriched.csv` (36 leads, +4 new emails)
4. **Email verification (Snov.io v2)** → `scripts/verify_all_emails.py` → status updates in `leads_enriched.csv`
5. **Bulk import to CRM** → `scripts/import_all_leads.py` → 35 companies + 35 people created
6. **Cross-language dedup** → `scripts/crosslang_dedup.py` → confirmed 0 dups across 645 companies
7. **Post-import verify** → `scripts/verify_import.py` → GraphQL `totalCount` check

#### 10.10.4 Snov.io v2 — the only working endpoints

| Purpose | Endpoint | Method | Notes |
|---|---|---|---|
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

#### 10.10.5 Cross-language dedup approach (reuse this)

`scripts/crosslang_dedup.py` catches Arabic/English duplicate company names by:
1. Fetching all companies + contacts via GraphQL.
2. Normalizing: lowercase, strip diacritics, remove `شركة` / `مؤسسة` / `Co.` / `LLC` / `Ltd` / `Inc`.
3. **Transliteration match:** map Arabic chars to Latin equivalents (ا→a, ع→a/aa, ح→h, etc.) and compare.
4. **Domain match:** exact or suffix match (e.g. `saudico.com.sa` matches `www.saudico.com.sa`).
5. **Phone match:** normalize to digits only, last 9 digits must match.
6. **Address overlap:** token Jaccard similarity ≥ 0.6 on street/city tokens.

**Result on 2026-07-06:** 0 duplicates found across 645 companies.

#### 10.10.6 Current data state (single source of truth)

**Junk cleanup done 2026-07-06:** all stale/intermediate/duplicate lead files were
eliminated. **`leads_enriched.csv` is now the one and only lead dataset** — do not
recreate the intermediates.

| File / Source | Rows | Status |
|---|---|---|
| **`leads_enriched.csv`** | 36 | **THE dataset** — clean + enrichment + Snov verification. Columns: company_name, domain_name, address, phone, email, email_status, sector, vertical_tier, created_by, lead_source, place_id. |
| CRM (Twenty) | 645 companies | Includes 35 from this run + 1 test (اتقان) |
| CRM contacts | ~491 | Includes 35 from this run + 1 test |

**Before re-running import:** run `scripts/verify_import.py` and
`scripts/crosslang_dedup.py` to confirm no new collisions. The 35
already-imported companies are in CRM and will create dupes if
`leads_enriched.csv` is re-imported as-is.

#### 10.10.7 Eliminated junk (deleted 2026-07-06 — do not recreate)

These were stale/intermediate/duplicate and have been **deleted** per the
"useful data upfront, no junk" rule. Listed so nobody re-generates them by habit:

| File | Why it was junk |
|---|---|
| `leads.csv`, `leads_final.csv`, `leads_verified.csv` | 50-row raw/intermediate first/second-run stages, superseded. |
| `leads_to_import.csv` | 48-row pre-dedup intermediate. |
| `leads_clean.csv` | 36-row subset of `leads_enriched.csv`. |
| `leads_verified_final.csv` | Byte-identical duplicate of `leads_clean.csv`. |
| `scripts/existing_crm_data.json` | Stale cache (claimed 21,500; actual 645). |
| `scripts/dedup_output.txt`, `scripts/test_crm.json` | Throwaway console dump / test artifact. |

#### 10.10.8 Canonical scripts (post-cleanup 2026-07-06)

`scripts/` was pruned from 65 → **29** — deleted 36 junk (all `test_*`, `debug_*`,
`inspect_*`, and superseded duplicates). The 29 keepers are the real pipeline:

- **Setup/runtime:** `setup_db.py`, `fix_runtime.py`, `check_runtime.py`
- **Lead fetch:** `fetch_leads.py`
- **Clean/dedup:** `step1_clean.py`, `graphql_dedup.py`, `crosslang_dedup.py`
- **Enrich:** `enrich_emails.py`, `fetch_emails_snov.py`, `step2_snov_v2.py`, `step2_snov_verify.py`
- **Verify:** `verify_all_emails.py`, `verify_import.py`
- **Import:** `import_all_leads.py`
- **CRM utils:** `configure_twenty.py`, `get_crm_schema.py`, `query_twenty.py`, `dump_crm.py`, `gen_integration_sql.py`
- **Checks:** `check_snov_credits.py`, `check_email_status.py`, `check_cloud_integrations.py`
- **Task ops:** `create_lead_task.py`, `monitor_task.py`, `check_task_status.py`, `approve_task.py`, `reset_task.py`, `update_csv_task.py`, `update_task_with_key.py`

Do not recreate the deleted experiments — if an endpoint needs probing, do it inline.

---

## 11. Outreach Strategy (design — planning only)

**Status: design phase.** Product context: Navaia — SaaS for missed-appointment /
inquiry recovery and customer-response automation. **Verticals are the 5 from the
co-founder strategy in §5.1** (NOT the generic set an earlier draft assumed):
Tier 1 — Contracting/Facilities, Finance & Debt Collection, Private Specialty
Clinics; Tier 2 — Real Estate, Training Institutes.

**Scope note (2026-07-06):** This repo/session does **planning only** — specs,
templates, decision docs. All executable work (enrichment, verification, sending,
import, scoring pipeline) is handed to a separate scripting model with a written
spec. Do not add scripts here.

Original user ask (2026-07-06): vertical-specific templates in formal Arabic
(عربي فصحى), one personalized line per lead, signed by user's name + company,
`cal.com` scheduling link, no AI tells (no em-dashes, no "I hope this finds you
well"), lead prioritization/ranking, free decision-maker lookup, inbound-sales
research.

### 11.1 Decisions locked (from user, 2026-07-06)

| Dimension | Decision |
|-----------|----------|
| **Tone** | Formal فصحى but **direct / brief** — value fast, short paragraphs, warm honorific greeting, no government-letter clichés. |
| **Cadence** | **Sequence: day 0 / +3 / +7** (research suggests optionally stretching last touch to +10 with a short +17 breakup — proposed, not yet approved). |
| **Channel** | **Email first; WhatsApp later** (via Baian once unblocked). For **high-priority leads, manual sends** are acceptable. |
| **Targeting** | **Not executive-only.** Leads are matched to the company's current need (warm/inbound-matched, not pure cold). Target the lead's **most-responsive channel / most likely respondent**, whoever that is — value the first channel that comes back, not just senior titles. |

### 11.2 Identity & config (resolved 2026-07-06)

| Field | Value |
|-------|-------|
| **Name** | عبدالمجيد الوردي / Abdulmajeed Alwardi |
| **Role** | تطوير الأعمال / Business Development |
| **Company** | نڤايا / NAVAIA |
| **Phone** | {{CONTACT_PHONE}} |
| **cal.com** | https://cal.com/abdulmajeed-alwardi |

**Per-vertical value props** (first-pass, correct 5 verticals, pending final sign-off).
Compliance regime differs per vertical — noted for the touch-1 assurance line.

| Vertical (tier) | Arabic value prop | Compliance line |
|-----------------|-------------------|-----------------|
| المقاولات والصيانة وإدارة المرافق (T1) Contracting/Facilities | نڤايا تلتقط طلبات العروض والاستفسارات وتردّ عليها فوراً وتتابع العروض حتى الترسية، فلا يضيع عقد بسبب تأخّر الردّ. | PDPL + أنظمة العمل |
| التمويل والتقسيط ومكاتب التحصيل (T1) Finance & Debt Collection | نڤايا تتابع المتعثّرين بانتظام ووفق أنظمة ساما وحماية البيانات، فيرتفع التحصيل دون إرهاق فريقكم. | **ساما (SAMA)** + PDPL |
| العيادات الخاصة (T1) Private Specialty Clinics (dental/derm/cosmetic/physio) | نڤايا تردّ على استفسارات المرضى وتؤكّد المواعيد وتتابع المتأخّرين، فيبقى الجدول ممتلئاً دون عبء على فريقكم. | **وزارة الصحة (MoH)** + PDPL |
| العقار وإدارة الأملاك (T2) Real Estate | نڤايا تردّ على المهتمّين خلال ثوانٍ قبل أن يبردوا، وتتابع تحصيل الإيجارات في وقتها، فلا تضيع صفقة ولا دفعة. | PDPL + الأنظمة العقارية (REGA) |
| معاهد التدريب (T2) Training Institutes | نڤايا تستوعب زحام موسم التسجيل وتردّ على كل مستفسر في حينه وتتابع الفرص حتى التسجيل، فلا يضيع طالب ولا فرصة. | PDPL + أنظمة التدريب (TVTC) |

### 11.3 Inbound-sales research findings (condensed, 2026-07-06)

Full brief captured from research; key operating rules for the templates:

- **Sequence beats single touch decisively** — first email captures ~58% of
  eventual replies; follow-ups the other ~42%. Multi-touch roughly doubles total
  responses. Each touch must add a **new angle** (new proof/pain framing), not just
  "bumping" the thread. Reply-rate baselines: ~3.4% platform avg, 5–10% solid,
  10–15% excellent, 15%+ best-in-class on tight segments. (Global baselines —
  Gulf-specific public data is thin; instrument our own.)
- **Personalization:** one specific, researched opening line beats a paragraph.
  Keep the whole email **6–8 sentences max** (13+ nearly halves reply rate).
  Reference-line priority for our verticals: (1) concrete vertical pain point,
  (2) their booking/inquiry channel observation, (3) location, (4) recent news
  (only if it exists — don't force it). Only the first 1–2 lines are per-lead.
- **Subject lines:** short (~6 words / <35 chars, renders on mobile), specific,
  question- or benefit-led, ≤1 punctuation mark, business name/vertical when
  possible. Personalized subjects open ~50% more. Avoid stiff openers like
  "بالإشارة إلى الموضوع أعلاه". Sample set stored in template file (see 11.6).
- **Cultural norms:** high formality; greeting **السلام عليكم ورحمة الله وبركاته**;
  honorific + name (**أستاذ/أستاذة** default, **دكتور** for clinics/doctorates,
  **المهندس** for engineers). Lead with brief respectful framing then value fast.
  Work week **Sun–Thu**; best windows Sun AM and Tue–Wed ~10am–12pm AST (UTC+3);
  **never Fri–Sat**. Ramadan: soften tone, add رمضان مبارك, send early AM or
  post-iftar. WhatsApp is the dominant business channel — email as credible cold
  open, move to WhatsApp on engagement (on-brand for Navaia).
- **AI/translation tells to avoid (Arabic):** don't calque English marketing-speak
  ("نأخذ عملك إلى المستوى التالي"), don't start every sentence with the same
  connector (وَ/كما/بالإضافة), don't mix فصحى with colloquial, don't over-formalize
  into government-letter clichés. Vary sentence length; native Gulf read-aloud QA
  on the first line before sending.
- **CTA:** **soft, interest-based CTA on touch 1** (yes/no ask, e.g. "هل تسمحون لي
  بمشاركة فكرة قصيرة…") — interest CTAs ~12% reply vs ~7% for time-asks, and links
  in a cold email hurt deliverability. **Send the cal.com link only after a
  positive reply** (alongside a WhatsApp option). Switch to a hard, specific-slot
  CTA once they're evaluating (~2.5x better at that stage).

### 11.4 Free decision-maker + email lookup playbook (condensed, 2026-07-06)

For a lead with just name + domain + city, fastest **free** path to a named
contact + verified email (hand this to the scripting/enrichment model as the
enrichment spec; keep LinkedIn steps **manual & low-volume** to stay within ToS):

1. **Company website /about + Instagram/X bio** — Saudi SMBs often name the owner
   there. 30 seconds, zero risk.
2. **Google dork LinkedIn for name+title** (manual; read the SERP snippet, avoid
   the authwall). Run **both English + Arabic** title variants:
   `site:linkedin.com/in "<company>" (manager OR مدير OR owner OR مالك OR founder OR مؤسس)`
3. **Apollo.io free plan** (sign up with a corporate-domain email → ~250/day
   credits vs ~100/mo on gmail) — best single free tool for the email.
4. **Hunter.io free** (25 searches + 50 verifies/mo) — Domain Search reveals the
   company's **email pattern**; use it to construct `first.last@domain`
   (+ transliteration variants: Mohammed/Mohammad/Muhammad, Abdullah/Abdallah).
5. **Verify** before sending — MyEmailVerifier (~100/day), Hunter (50/mo),
   Verifalia (25/day, has API). **KSA caveat:** many SMBs run catch-all mail →
   "accept-all/unknown" is **not** confirmation; fall back to `info@` / phone /
   WhatsApp.
6. **Fallback name sources:** Maroof (maroof.sa) for e-commerce sellers; Google
   Maps **owner replies to reviews** are often signed; Chambers of Commerce for
   legal name + landline.
7. **Stack free tiers** to stay at $0: Apollo (~unlimited-ish) + Hunter (25+50) +
   Snov (50) + Lusha (70) + MyEmailVerifier (~100/day) = hundreds/month.

**Compliance:** LinkedIn — manual public-profile viewing OK, **no automated
scraping** (User-Agreement breach → bans). PDPL — contact people in professional
capacity, prefer business/role addresses, honor opt-outs, include an Arabic
opt-out line on any linked page. Never send to unverified guesses (spam-trap /
reputation risk).

### 11.5 Lead prioritization / scoring model (rules-based, 0–100)

Start transparent and rules-based; move to predictive once we have volume.
Weight **trigger events** heavily (external buying-intent correlates with
closed-won far more than engagement). Proposed weights (to hand to scripting model):

| Signal | Weight |
|--------|--------|
| Vertical fit (appointment/inquiry-heavy: clinics, dentists, salons, reservation restaurants) | +30 |
| Manual booking/inquiry channel (phone/DM/form, active IG/WhatsApp business) | +20 |
| Has verified email | +20 |
| Trigger event (new branch, hiring front-desk/CS, new/revamped website, new online booking, reviews citing "no reply") | +15 |
| Employee count ~3–50 (loses real money to misses, fast owner decision) | +10 |
| Has website / LinkedIn (digital maturity) | +10 |
| Named decision-maker identified | +10 |

(Cap at 100; tune after first send batch.)

### 11.6 Template blueprint (to be written once 11.2 answers arrive)

Deliverable = a per-vertical Arabic sequence file. Structure per touch:

> **CTA decision (user override, 2026-07-06):** the cal.com link + a short brief
> (نبذة موجزة) go in **touch 1**, not gated behind a reply. This overrides the
> research rec in §11.3 (which favored a soft, no-link touch 1 for deliverability).
> Mitigation handed to the sending model: warmed sending domain + plain-text link.

- **Touch 1 (day 0)** — fixed flow: subject = the pain point (from real info,
  catchy, short) → warm honorific greeting (warmth ~6/10) → open on **this
  company's** pain → **what we do (actions, not the how)** → **impact stated as
  plain fact** ("ليست وعوداً بل نتائج"), pick **2 of 3 benefits** matched to the
  lead (cost −40–60% / profit +30% / staff productivity) → **regulatory assurance**
  (clinics: MoH + PDPL; others: PDPL + relevant work regs), clear not overstated →
  **cal.com link + WhatsApp** → **4-line signature** (name / تطوير الأعمال Business
  Development / phone / NAVAIA نڤايا). Conversational فصحى, no middot bullets.
- **Touch 2 (day +3):** new angle (a proof point / specific number, e.g.
  "٣ مواعيد ضائعة أسبوعياً") → shorter → cal.com link again.
- **Touch 3 (day +7):** brief value restatement + gentle breakup → cal.com /
  WhatsApp as convenience.
- **On positive reply (any touch):** confirm cal.com link + WhatsApp option; switch
  to hard specific-slot CTA.
- **Ramadan variant:** رمضان مبارك opener, softened tone, timing early AM / post-iftar.

Personalization tokens: `{اسم}` (business name), `{honorific+name}`,
`{vertical_value_prop}`, `{pain_line}`. Only `{pain_line}` and `{honorific+name}`
are per-lead; the rest are per-vertical.

---

## 12. Change Log

| Date       | Change |
|------------|--------|
| 2026-07-05 | Initial draft from user's workflow description. |
| 2026-07-05 | Updated verticals from co-founder strategy (5 verticals, 2 tiers). Twenty CRM active. Google Places API added. Snov.io scoped to enrichment only. E-commerce removed. General hospitals removed — private specialty clinics only. |
| 2026-07-06 | Runtime switched from `claw_code` to `claude_max` (claw CLI missing in container). First lead-finding run completed: 50 leads from Google Places API, 25 enriched with Snov.io emails. CRM down — leads in CSV. Added §10 with full execution results and findings. |
| 2026-07-06 | CRM came back up. Bulk import completed: 35 companies + 35 contacts created in Twenty CRM (609 → 645 companies). Cross-language dedup ran clean (0 dups). Email verification + enrichment pipeline built and ran. Added §10.10 (Post-Import Pipeline) as the authoritative state reference for future sessions. Added §11 (Outreach Strategy) as a placeholder for the next phase — pending user's answers to §11.1 questions and inbound-sales research. |
| 2026-07-06 | Outreach strategy built out (planning only — scripting handed off to a separate model). User locked 4 decisions: tone (formal but direct/brief), cadence (day 0/+3/+7), channel (email first, WhatsApp later, manual for high-priority), targeting (most-responsive contact, not executive-only). Ran two research sub-agents → folded findings into §11.3 (inbound-sales best practices) and §11.4 (free decision-maker/email lookup playbook). Added §11.5 (rules-based 0–100 scoring model) and §11.6 (template blueprint). Remaining blockers in §11.2: user's name, company name, cal.com URL, per-vertical value prop. |
| 2026-07-06 | Identity resolved: عبدالمجيد الوردي / Abdulmajeed Alwardi, نڤايا / NAVAIA, https://cal.com/abdulmajeed-alwardi. Drafted first-pass per-vertical value props (§11.2). Created `OUTREACH_TEMPLATES.md` with the Private Clinics reference sequence. **User override:** cal.com link + short brief now go in touch 1 (not gated behind a reply) — updated §11.6 and the templates accordingly; deliverability mitigation (warmed domain + plain-text link) noted for the sending model. |
| 2026-07-06 | Touch-1 voice reworked per user: conversational فصحى (warmth 5→6/10), fixed flow (pain subject → company pain → actions-not-how → impact as plain fact → regulatory assurance → link), **benefit bank of 3 real results** (cost −40–60%, profit +30%, staff productivity) with **2 chosen per lead**, MoH + PDPL compliance line stated clearly-not-overstated, **no middot bullets**, **4-line signature** (name / Business Development / phone / NAVAIA نڤايا). Updated §11.6. **Still needed from user:** phone number (`{رقم الهاتف}`) for the signature. |
| 2026-07-06 | Positioning rule added: frame as **حلول (solutions), not منصّة (platform)** — platform implies work/onboarding for the reader; pair with a "works on your behalf, no extra load" clause and a "we start from…" framing so one pain implies broader scope without a services list. |
| 2026-07-06 | **Vertical correction:** earlier templates used a wrong generic set (restaurants/retail/professional services). Rebuilt on the **correct 5 co-founder verticals** (§5.1): Contracting/Facilities, Finance & Debt Collection, Private Specialty Clinics (T1); Real Estate, Training Institutes (T2). `OUTREACH_TEMPLATES.md` now has full 3-touch sequences for all 5, each with its own pain line, benefit pairing, and **vertical-specific compliance** (SAMA for finance, MoH for clinics, REGA for real estate, TVTC for training, PDPL throughout). Fixed §11.2 value props to match. |
| 2026-07-06 | Template copy fixes per user: (1) "وأتّصل بكم" → "لأتّصل بكم"; (2) positive-reply now branches on whether they already booked via cal.com (check first, two replies A/B); (3) "تعمل نيابةً عنكم" (works *instead of* you) → "تعمل إلى جانبكم" (works *alongside* you) throughout; (4) **the +30% / 40–60% numbers are clinic-only** — all other verticals now carry placeholders (`{نسبة الأثر}`, `{نسبة التحصيل}`, `{نسبة خفض التكاليف}`) for the user to fill. **Still needed from user:** phone number + non-clinic impact rates. |
| 2026-07-06 | **Scripts pruned 65 → 29** — deleted 36 junk (all `test_*`, `debug_*`, `inspect_*`, and superseded duplicates); kept the real pipeline. Canonical set documented in §10.10.8. Also gitignored `leads*.csv` (PII) and `scripts/*.json` dumps. |
| 2026-07-06 | **Junk data eliminated** ("useful data upfront" rule): deleted 9 stale/intermediate/duplicate files (`leads.csv`, `leads_clean.csv`, `leads_final.csv`, `leads_to_import.csv`, `leads_verified.csv`, `leads_verified_final.csv`, `scripts/existing_crm_data.json`, `dedup_output.txt`, `test_crm.json`). **`leads_enriched.csv` (36 leads) is now the single source of truth.** Rewrote §10.10.6 (single dataset) and §10.10.7 (now lists what was deleted, not "stale but keep"). |
| 2026-07-06 | Handoff clarity for future sessions (any model): added a prominent **▶ NEXT STEP** block at the top (templates done; remaining = user's non-clinic numbers + scripting-model send/automation; explicit planning-vs-scripting role boundary). Refreshed **§9** — the stale "outreach In progress / needs cal.com+tone" row replaced with accurate Done/Blocked/Pending rows. |
| 2026-07-06 | Added **§0 Current Known-Good Setup + Fixes Applied** at the top of the spec — consolidates the actual running config (runtime `claude_max`, model `moonshotai/kimi-k2.6`, SDK 0.2.3, JWT→Bearer, DEBUG=true, `setup_db.py`) and the fixes that got there (JWT header, DB init, cross-platform setup, scheduler tables, version/doc sync, runtime switch from `claw_code`). Reconstructed from git history + `scripts/fix_runtime.py`/`check_runtime.py`. Flags the `ASSESSMENT.md` example drift (navaia_code/claude-sonnet-4 is generic, not live). Also fixed the templates signature to `تطوير الأعمال - Business Development` (no brackets, single dash) and regenerated the PDF. |
| 2026-07-06 | Added **per-vertical field vocabulary** — each sequence now weaves 2–3 well-known Arabic field terms to signal domain familiarity, with a documented **Field lexicon** line per vertical: Contracting (عروض أسعار/RFQ, مناقصات وعطاءات, مواعيد تسليم العطاءات, عقود صيانة وقائية, SLA); Finance (محفظة التحصيل, أعمار الديون, الأقساط المتأخّرة, لوائح ممارسات التحصيل); Clinics (المراجعين, عدم الحضور/no-show, قائمة الانتظار, إشغال الجدول); Real Estate (الوحدات الشاغرة, المعاينة, دفعات الإيجار وسنداتها); Training (المتدربين, الالتحاق بالدفعة, المنافسات الحكومية, منصة اعتماد/Etimad). Positioning rule added in the templates conventions. |
