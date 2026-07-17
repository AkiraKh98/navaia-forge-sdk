# Playbook — Email outreach (Snov.io campaign → Zoho mailbox)

> SOP for outbound email. **Lina writes the copy; Tariq sends it.** The send path is
> **Snov.io campaign → connected Zoho mailbox** (`ops@navaia.sa`) — **never call Zoho Mail
> send directly.**

## Preconditions
- Snov.io connected (`SNOV_USER_ID`/`SNOV_USER_SECRET`), Zoho mailbox connected on the
  workforce (verify via `scripts/check_cloud_integrations.py`).
- Copy is ready: Lina has produced finished, approved per-lead templates from
  `../04_outreach_templates.md` (5 verticals × 3 touches). See `../agents/lina_marketing.md`.
- Leads live in Twenty CRM / `leads_enriched.csv`, scored per `../05_lead_scoring_model.md`.

## Steps
1. **Lina → copy.** For each lead's vertical, fill per-lead tokens (`{honorific+name}`,
   company noun, `{pain_line}`, `{benefit_pair}` — pick 2 of 3: cost −40% / profit +30% /
   productivity). **No signature in the body** — Snov.io auto-appends the account's configured
   signature (verified 2026-07-13). Do not embed one or pass `--signature-file`, or it
   double-stamps. Reference copy: `../assets/email_signature.html`; the signature's `M` phone is
   Baian's WhatsApp number `+966 58 284 1599` (the lead contact), distinct from the rep's phone.
2. **Tariq → send.** Create/launch a **Snov.io campaign** using the Zoho mailbox as the
   connected sender. Prioritise by lead score.
3. **Cadence:** day 0 / +3 / +7. Send **Sun–Thu ~10am–12pm AST**, never Fri–Sat.
4. **Deliverability:** warmed domain; **plain-text** cal.com link (not hyperlinked); no
   tracking pixels; start **20/day**, ramp to **50/day** after a week; personalised subjects.
5. **Replies:** positive → cal.com link; booked → confirm; negative → graceful close;
   no reply after +7 → end cadence. Log sends + replies to the Fareegi dashboard.

## Note
Email sending automation is not yet wired as a script (unlike the lead pipeline and the
Baian send). When wired, add a canonical `scripts/` entry and link it here.
