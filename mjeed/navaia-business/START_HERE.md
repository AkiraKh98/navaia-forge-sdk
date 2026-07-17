# START HERE

**First instruction for any new session/CLI (any model):**

> **Read `workforce/HANDOFF.md` FIRST** — it is the current state, the hard rules, what's
> done vs open, and the next steps as of 2026-07-08. Do not drift from it.
> Then read **`AGENTS.md`** (the entry point → the 7 agents + `workforce/`).

Then, depending on what you're doing:
- Running a job → the relevant SOP in `workforce/playbooks/`.
- Dispatching a task → a spec in `workforce/tasks/` via the canonical `scripts/`.
- Understanding an agent → `workforce/agents/<name>.md`.
- Current status → `workforce/07_open_items_and_status.md`.

Do **not** rebuild outreach templates or re-run lead finding/import — that's done
(`workforce/07_open_items_and_status.md`). Secrets stay in `.env` (never commit).
