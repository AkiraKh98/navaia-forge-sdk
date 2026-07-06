# START HERE

**First instruction for any new session (any model):**

> Read `WORKFLOW_SPEC.md` now — the **"▶ NEXT STEP"** block at the top and **§0** —
> before doing anything else, then do exactly what NEXT STEP says. Don't rebuild
> templates or re-run lead/import work; that's done.

---

## 30-second orientation

- **`WORKFLOW_SPEC.md`** — the source of truth. Start at the top:
  - **▶ NEXT STEP** — what's done, what remains, and the planning-vs-scripting boundary.
  - **§0** — known-good setup (`claude_max`, `moonshotai/kimi-k2.6`, SDK 0.2.3, JWT→Bearer auth, `DEBUG=true`, `setup_db.py`) + the fixes that got there.
  - **§9** — current status (Done / Blocked / Pending).
  - **§10.10** — CRM state, data of record, canonical scripts.
  - **§11** — outreach strategy + decisions.
- **`OUTREACH_TEMPLATES.md`** — finished Arabic outreach templates (5 verticals × 3 touches). Clean copy also in `NAVAIA_Outreach_Templates.pdf`.
- **`leads_enriched.csv`** — the single lead dataset (36 leads). Everything else was junk and was deleted.

## Role boundary

This repo is **planning only** — templates, specs, docs. All executable work
(enrichment, verification, sending, import, the scoring pipeline) is done by a
**separate scripting model** from a written spec.

- If you are the **scripting/execution** model, your spec is **§11.5** (lead scoring)
  + **§5.2/§5.3** (send channels) + **`OUTREACH_TEMPLATES.md`** (content).
- If you are a **planning** session, don't write scripts — hand executable work off.

## Do NOT

- Rebuild the outreach templates (done).
- Re-run lead finding / enrichment / import (done — see §9, §10.10).
- Invent the non-clinic impact numbers — they're placeholders; ask the user.
- Recreate deleted `test_*` / `debug_*` / intermediate CSV files.
