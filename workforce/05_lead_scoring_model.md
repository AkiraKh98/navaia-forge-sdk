# 05 — Lead Scoring Model

> **Rules-based 0–100 scoring model** for prioritizing outreach. Start
> transparent and rules-based; move to predictive once we have volume.
>
> **Implementation is the scripting model's work.** This file is the spec
> the scripting model will use to build the scoring pipeline.

---

## Philosophy

Weight **trigger events** heavily — external buying-intent correlates with
closed-won far more than engagement signals.

**Tune after first send batch.** The weights below are first-pass; real data
should be folded in after 50–100 sends to recalibrate.

---

## Scoring Signals & Weights

| Signal | Weight | Source | How to detect |
|--------|--------|--------|---------------|
| **Vertical fit** (appointment/inquiry-heavy: clinics, dentists, salons, reservation restaurants) | +30 | Lead's sector field | Sector ∈ {"Private Clinics"} or "has manual booking channel" |
| **Manual booking/inquiry channel** (phone/DM/form, active IG/WhatsApp business) | +20 | Lead's website / IG / Google listing | No online booking widget; phone/WhatsApp listed; IG active |
| **Has verified email** | +20 | Snov.io verification result | `email_status == "verified"` or `"found_unverified"` with `.sa` domain (treated as likely valid per Snov caveat) |
| **Trigger event / review pain** (reviews citing "no reply", missed calls, slow booking) | +15 | **`scripts/enrich_reviews.py`** — trust-locked to the lead's own Google reviews (exact place_id + phone match) → `leads_reviews.csv` + CRM | Non-empty `pain_line` for the lead. Also surfaced as `{trigger_line}` in the outreach opener. |
| **Employee count ~3–50** (loses real money to misses, fast owner decision) | +10 | Google Places / LinkedIn | `employeeCount` in [3, 50] |
| **Has website / LinkedIn** (digital maturity) | +10 | Lead's website URL, LinkedIn | Non-empty `domainName` or `linkedinLink` |
| **Named decision-maker identified** | +10 | Enrichment output | Person record exists with `decisionMaker: true` |

**Cap at 100.**

---

## Score Buckets

| Score | Bucket | Action |
|-------|--------|--------|
| 80–100 | **Hot** | Send first batch, high priority, manual sends acceptable |
| 50–79 | **Warm** | Send in normal cadence, automated |
| 20–49 | **Cool** | Send in later batch, test messaging first |
| 0–19 | **Cold** | Defer or skip (re-evaluate in next quarter) |

---

## Vertical Fit Detail

The 5 verticals from §5.1 are **all** in-scope, but the "vertical fit" score
applies when the lead is in a high-pain, high-margin vertical with a manual
booking/inquiry channel that our product can directly address:

| Vertical | Vertical fit score? | Notes |
|----------|---------------------|-------|
| Private Specialty Clinics (dental/derm/cosmetic/physio) | **+30** | Direct fit — missed appointments, no-shows |
| Contracting/Facilities | 0 (use other signals) | Fit is via RFQ/follow-up, not appointment-channel |
| Finance/Debt Collection | 0 (use other signals) | Fit is via collection consistency, not booking-channel |
| Real Estate | 0 (use other signals) | Fit is via response time, not booking-channel |
| Training Institutes | 0 (use other signals) | Fit is via registration surge, not booking-channel |

> **Note:** the +30 vertical fit is a "bonus" on top of the other signals. It's
> designed to push clinics to the top of the send list because they're the
> tightest vertical fit for the product. Other verticals can still score high
> via the other signals (e.g., Finance + verified email + trigger event +
> named decision-maker = 55+).

---

## Trigger Event Detection (cheapest signals first)

| Signal | Detection method | Confidence |
|--------|------------------|------------|
| Google review mentions "no reply" / "ما ردّوا" | Text search on reviews | Medium |
| Recent hiring post for front-desk / CS | LinkedIn / Google Jobs | High |
| New website or recent redesign | Archive.org `Wayback Machine` | High |
| New online booking system launched | Site crawl | High |
| New branch opened | Google Places new listing | High |
| Recent negative review spike (>2 in 30 days) | Google reviews | Medium |

**Cap trigger events at +15 total** (even if multiple signals are present —
avoid double-counting the same underlying event).

---

## What This Model Does NOT Consider (intentionally)

- **Engagement with our previous emails** — we don't have enough historical
  data to weight this meaningfully yet
- **Social media follower count** — weak signal for SMBs in our verticals
- **Revenue** — rarely accurate for SMBs; skip unless verified from a
  primary source
- **Industry awards / press** — irrelevant for the target verticals

---

## Implementation Notes (for the scripting model)

1. **Read from `leads_enriched.csv` + Twenty CRM.** Merge on place_id or
   company_id.
2. **Compute the score** for each lead using the signals above.
3. **Bucket and sort** by score descending.
4. **Cap at 100.**
5. **Output** to `leads_scored.csv` with the score + bucket + signals used.
6. **Hand off to the outreach pipeline** — Zoho agent reads the scored list
   and sends in bucket order (Hot → Warm → Cool).

### Pseudocode

```python
def score_lead(lead):
    score = 0
    signals = []

    # Vertical fit
    if lead.sector == "Private Clinics" and has_manual_booking_channel(lead):
        score += 30
        signals.append("vertical_fit_clinics")

    # Manual booking/inquiry channel
    if has_manual_booking_channel(lead):
        score += 20
        signals.append("manual_booking_channel")

    # Has verified email
    if lead.email and lead.email_status in ("verified", "found_unverified"):
        score += 20
        signals.append("verified_email")

    # Trigger event
    if has_trigger_event(lead):
        score += 15
        signals.append("trigger_event")

    # Employee count
    if 3 <= lead.employee_count <= 50:
        score += 10
        signals.append("employee_count_3_50")

    # Has website or LinkedIn
    if lead.domain or lead.linkedin:
        score += 10
        signals.append("digital_maturity")

    # Named decision-maker
    if has_named_decision_maker(lead):
        score += 10
        signals.append("named_decision_maker")

    return min(score, 100), signals
```

---

## Calibration Plan (after first send batch)

After 50–100 sends, measure reply rate by signal and re-weight:
- If "verified email" predicts reply strongly → keep at +20
- If "vertical fit" is noisy (clinics don't reply more than other verticals)
  → drop to +15 and redistribute
- If "trigger event" is the strongest predictor → consider raising to +25

**Target:** 10–15% reply rate (best-in-class on tight segments).

---

## Open Questions for the User

- Should we add a "company size penalty" for leads with employee_count > 200?
  (Longer sales cycle, more decision-makers.)
- Should we weight "Riyadh-based" higher than other Saudi cities?
- Should we add a "language preference" signal (Arabic-only vs bilingual)?