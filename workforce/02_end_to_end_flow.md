# 02 — End-to-End Flow (Happy Path)

> The complete orchestration flow from user task to sent outreach, with all
> handoffs between agents documented.

---

## Happy Path (8 steps)

### 1. User assigns a task to the workforce

Via SDK or Fareegi dashboard. Example:
> "Find 20 SaaS founders in Riyadh and reach out."

The task is assigned to the workforce as a whole. Ahmed (GM) receives it.

### 2. Ahmed (GM) parses the task

Ahmed enters **Conversational Chat Mode** if the task is ambiguous. He asks
clarifying questions, summarizes his understanding, and only once confident
proceeds.

For clear tasks, he proceeds directly to delegation.

### 3. Ahmed delegates to Lead Fetcher (Tariq)

> "Find 20 SaaS founders in Riyadh, store with contacts in the CRM file."

Tariq runs the lead-fetch pipeline (see `agents/tariq_sdr_lead_fetcher.md`):
1. Raw fetch via Google Places API
2. English-name dedup vs CRM
3. Email enrichment (website crawl + web search + Snov.io)
4. Email verification (Snov.io v2)
5. Bulk import to Twenty CRM
6. Cross-language dedup
7. Post-import verify

Leads land in `leads_enriched.csv` + Twenty CRM. Tariq reports back to Ahmed.

### 4. Ahmed delegates outreach — Lina writes, Tariq sends

Outreach is not an agent; it's a two-step handoff Ahmed orchestrates:

**Lina (Marketing) — writes:**
- Receives the lead list + per-lead context (sector, pain, decision maker) + framing
  ("first-touch cold reach") + which of the 5 verticals to use.
- Produces finished, approved copy from `04_outreach_templates.md`: subject + body per
  touch, benefit pair chosen, tokens filled (`{honorific+name}`, `{pain_line}`,
  `{benefit_pair}`, vertical noun). WhatsApp variant is shorter.

**Tariq (SDR) — sends:**
- Pulls lead + context from Twenty CRM (or `leads_enriched.csv` for Phase 1).
- Applies the §11.5 lead score to prioritize.
- **Email:** launches a **Snov.io campaign** using the connected **Zoho mailbox**
  (`ops@navaia.sa`) — never Zoho-direct.
- **WhatsApp:** sends via **Baian** — **cloud-only**, so Ahmed routes the task to the
  cloud runtime; Tariq never sends Baian locally.
- Logs every send + reply to the Fareegi dashboard.

### 6. Ahmed aggregates outcomes

Ahmed collects:
- Number of leads found
- Number of emails sent
- Open / reply / conversion rates (when available)
- Any errors or escalations

He updates the task status and surfaces results to the user via the dashboard.

### 7. Replies / inbound signals flow back

- Email replies → Zoho Mail → Fareegi dashboard → Ahmed
- WhatsApp replies → Baian → dashboard → Ahmed
- Inbound form submissions → CRM → dashboard → Ahmed

Ahmed routes follow-ups:
- Positive reply → confirm cal.com booking + WhatsApp option
- Question reply → answer or route to specialist
- Negative reply → graceful close
- No reply after +7 → end of cadence

### 8. Follow-up cadence (day 0 / +3 / +7)

- **Day 0:** Touch 1 (pain → actions → impact → compliance → link)
- **Day +3:** Touch 2 (new angle: proof point or specific number)
- **Day +7:** Touch 3 (warm door-open breakup)
- **On positive reply:** Confirm cal.com + WhatsApp option; switch to hard CTA

---

## Agent Handoff Map

```
User
  ↓ (assign task)
Ahmed (GM)
  ↓ (delegate: find leads)
Tariq (SDR)
  ↓ (leads in CRM + CSV)
Ahmed (GM)
  ↓ (delegate: write outreach)
Lina (writes copy)
  ↓ (finished, approved copy)
Tariq (sends: email via Snov→Zoho; WhatsApp via Baian on cloud)
  ↓ (sends logged to dashboard)
  ↓ (replies come back)
Ahmed (GM)
  ↓ (route follow-ups)
Tariq (send) / Lina (rewrite) / User
```

---

## Failure Modes & Escalation

| Failure | What happens | Escalation |
|---------|--------------|------------|
| Tariq can't find enough leads | Reports back to Ahmed with count | Ahmed asks user to broaden criteria |
| Email send fails | Logged to dashboard, retry queue | If >10% fail rate, Ahmed escalates |
| Lead has no email | Skipped (Tariq should have flagged) | Ahmed asks user to provide channel |
| Recipient replies negatively | Routed to Ahmed | Ahmed sends graceful close |
| Recipient replies positively | Routed to Ahmed | Ahmed confirms cal.com + WhatsApp |
| Baian unavailable / can't route to cloud | WhatsApp sends held | Ahmed falls back to email (Snov→Zoho) only |
| Agent model produces malformed JSON | Scripted fallback (direct Python) | Ahmed notes in dashboard |

---

## Role Boundary (planning vs. scripting)

This repo/session is **planning only** — templates, specs, docs. All
executable work (enrichment, verification, sending, import, the scoring
pipeline) is done by a **separate scripting model** from a written spec.

- If you are the **scripting/execution** model, your spec is:
  - `05_lead_scoring_model.md` (lead scoring)
  - `agents/lina_marketing.md` (outreach copy) + `agents/tariq_sdr_lead_fetcher.md` → "Outbound Sending"
  - `04_outreach_templates.md` (content)
- If you are a **planning** session, don't write scripts — hand executable work off.