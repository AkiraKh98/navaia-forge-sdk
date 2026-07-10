# AGENTS.md — NAVAIA Business workforce

> Entry point for any agent or LLM working in this repo (the [AGENTS.md](https://agents.md/)
> open standard). **➤ First read `workforce/README.md`** for the current state, hard rules,
> and next steps (2026-07-08). Then this file → the source of truth in **`workforce/`**.

## Project overview

**NAVAIA Business** is a business-development workforce of **exactly 7 agents** running on
the **NavaiaForge** platform (this repo is the NavaiaForge SDK; the workforce is the
business overlay in `workforce/`). It finds Riyadh leads across 5 verticals and does
outbound outreach (email + WhatsApp). Runtime: `claude_max` → OpenRouter, model
`moonshotai/kimi-k2.6`.

## The 7 agents (never invent more)

| Agent | Role | Owns |
|-------|------|------|
| **Ahmed** | GM / orchestrator | Routing, tracking; holds the capability map; enforces the two hard rules |
| **Tariq** | SDR | Lead gen + enrichment **and sending** (email + WhatsApp) |
| **Lina** | Marketing | **Writes** all outreach copy (Tariq sends it) |
| **Ghida** | Creative | Visual identity / design (phased) |
| **Nora** | Finance | Pricing, billing, reporting (phased) |
| **Rashid** | Strategy | Market/competitive analysis (phased) |
| **Fahad** | Account Manager | Post-sale success (phased) |

Full per-agent instructions: **`workforce/agents/`**. Outreach is a **capability**, not an
agent — there is no standalone email or WhatsApp agent.

## Two hard rules

1. **Baian (WhatsApp) is CLOUD-ONLY.** Its secret lives only in the cloud runtime. Route
   any WhatsApp/Baian task to the cloud; never run it locally.
2. **Email sends through Snov.io** (campaign → connected Zoho mailbox), **never Zoho
   directly.**

## How to run things (executor SOPs)

Each is a step-by-step playbook with exact commands:
- **`workforce/playbooks/lead_pipeline.md`** — fetch → clean → dedup → enrich → verify → import.
- **`workforce/playbooks/email_send_snov.md`** — email outreach (Snov → Zoho).
- **`workforce/playbooks/whatsapp_send_baian.md`** — WhatsApp via Baian (PROVEN).
- **`workforce/playbooks/deploy_and_sync.md`** — stack deploy, runtime, cloud↔local sync.

## How to dispatch a task to the workforce

The container holds thin agent shells; **behaviour comes from self-contained task specs in
`workforce/tasks/`**. Dispatch via the canonical scripts:
```bash
.venv/Scripts/python.exe scripts/baian_send.py --template <approved_template>   # WhatsApp
.venv/Scripts/python.exe scripts/create_lead_task.py                            # lead finding
.venv/Scripts/python.exe scripts/check_cloud_integrations.py                    # read-only: what's connected
```
Cloud workforce id `131bb52f-e5eb-44ad-8134-03dc6908b485`; Tariq (sender)
`6ba49326-4ec0-4b3b-8651-9526ec96894e`.

## Setup

```bash
python -m venv .venv && .venv/Scripts/pip install -e packages/python
docker compose -f docker-compose.dist.yml up -d
.venv/Scripts/python.exe scripts/setup_db.py
.venv/Scripts/python.exe scripts/check_runtime.py   # expect claude_max + moonshotai/kimi-k2.6
```

## Secrets & data

- Secrets live in **`.env`** (gitignored) — `BUSINESS_NF`, `TWENTY_TOKEN`, `SNOV_*`,
  `ZOHO_*`, `PLACES_API`, `MY_PHONE`, `OPENROUTER_API_KEY`. **Never commit them.** Baian's
  token is **not** here — it's cloud-only. Shapes documented in `workforce/10_integration_keys.md`.
- `leads_enriched.csv` (PII) is the single lead dataset — **gitignored**, never commit.

## Repo map

- `workforce/` — business source of truth (agents, `00–10` knowledge docs, `playbooks/`, `tasks/`).
- `scripts/` — canonical Python executors (lead pipeline, CRM utils, task ops, Baian send).
- `packages/`, `examples/`, `docs/`, `ASSESSMENT.md` — the NavaiaForge SDK/platform (do not modify for business changes).

## Change discipline

`workforce/` is the source of truth. Deploy the workforce once, then make changes via
**PRs** against this repo — not ad-hoc edits to the live cloud entity.
