# Building Workforces on NavaiaForge — Intern Guide

> A practical, plain guide for anyone building a workforce on the NavaiaForge SDK.
> Readable by you **and** by your coding CLI/agent — point your agent at this file and it
> knows how things work. Keep it open while you build.

---

## 0. Before anything — get the latest (do this every time)

The SDK moves. Fixes land on **`main`** regularly. **Always start from the latest**, or
you'll waste hours on bugs that are already fixed.

```bash
# one-time: point at the original repo
git remote add upstream https://github.com/NavaiaSolutions/navaia-forge-sdk.git

# every time you start work:
git fetch upstream
git checkout main
git merge upstream/main        # or: git rebase upstream/main
pip install -e packages/python # reinstall in case the SDK changed
```

Check what changed before you assume anything:
```bash
git log --oneline main..upstream/main   # new fixes you don't have yet
```

**Rule:** if something breaks, `git fetch upstream` and check `main` **first**, before
debugging. Nine times out of ten it's already fixed.

---

## 1. The mental model: what lives where

The single most important thing to understand: **your machine runs the work; the cloud
watches it — and a few secrets live only in the cloud.**

| Lives on **your machine** (local) | Lives in the **cloud** (Fareegi dashboard) |
|-----------------------------------|--------------------------------------------|
| The SDK + the Docker backend (`localhost:8001`) | The dashboard: outputs, chats, scheduler, monitoring |
| The **agent runtime** — where tasks actually execute | A copy of your workforce (for visibility) |
| Your **`.env` secrets** (API keys, tokens) | **Cloud-only integration secrets** (e.g. a WhatsApp/Meta token) |
| Your scripts + data (leads, CSVs) | — |

**Golden rules:**
1. **Secrets live in `.env`. Never commit them.** `.env` is gitignored — keep it that way.
2. **Some integration tokens are cloud-only.** If an integration's secret only exists in
   the cloud (a WhatsApp/Baian token is the classic case), any task using it **must run on
   the cloud**, not locally. You can't call it from a local script — dispatch a task and
   let the cloud runtime do it.
3. **Local wins for execution; cloud wins for visibility.** If they disagree, trust local
   for *what ran*, cloud for *what you can see*.
4. **Data with PII (leads, contacts) stays local** and gitignored — even in a private repo.

---

## 2. Set up (once per machine)

```bash
python -m venv .venv
.venv/Scripts/pip install -e packages/python      # or: pip install navaia-forge
docker compose -f docker-compose.dist.yml up -d
curl http://localhost:8001/health                 # -> {"status":"healthy"}
.venv/Scripts/python scripts/setup_db.py          # one-time DB init
cp .env.example .env                               # then fill in YOUR keys
```

---

## 3. Build your workforce (the shape)

A workforce = **one orchestrator + a few specialists**, plus the integrations they use.

1. **Create the workforce** (SDK or dashboard).
2. **Add agents** — one **orchestrator** (the "GM"), and **specialists** for the real jobs.
3. **Connect integrations** — CRM, email, data providers, WhatsApp, etc. (keys go in the
   integration config / `.env`, never in code).
4. **Dispatch tasks** — you give a task to the workforce; the orchestrator routes it.
5. **Watch it** on the Fareegi dashboard; **sync** so cloud and local stay coherent.

---

## 4. Multi-agent, kept simple (don't over-build)

Multi-agent is easy when you keep it boring:

- **One orchestrator that knows its team.** Put the *map of every agent's capabilities*
  inside the orchestrator's instructions. It routes; it never does the specialist work
  itself.
- **Each specialist does one job.** SDR finds leads. Marketing writes copy. Etc.
- **Don't invent agents you don't need.** More agents = more coordination = more cost. Add
  one only when a real, distinct job appears.
- **Write self-contained task descriptions.** The single biggest driver of reliability:
  put *everything the agent needs to do the job* in the task itself — the steps, the
  endpoints, the rules — especially for weaker/cheaper models. A vague task fails; a
  spec-shaped task succeeds.

---

## 5. Don't burn expensive models on leg work ⚠️ (the money rule)

**The most capable model is not the default. Match the model to the job.** Most of what a
workforce does is routine leg work that a cheap model does just as well — paying top price
for it is pure waste.

| The job | Model tier | Why |
|---------|-----------|-----|
| Fetching data, formatting, dedup, filling a template, simple extraction/classification | **Cheap / small** | Mechanical. A big model adds cost, not quality. |
| Routing/orchestration, judging ambiguous input, multi-step planning | **Mid / capable** | Needs real reasoning. |
| Writing customer-facing copy, nuanced judgement, tricky reasoning | **Most capable** | Quality is visible to customers — worth it. |

Two habits that save the most:
- **Prefer a script over an LLM for deterministic work.** Don't pay a model to fetch from
  an API or reshape a CSV — a plain Python script is cheaper, faster, and doesn't
  hallucinate. Let the agent *orchestrate*; let scripts *do the mechanical work*.
- **Set the model per agent, not one-size-fits-all.** Your leg-work agents should run a
  cheap model; reserve the capable model for the orchestrator and the writer.

> Rule of thumb: **if a task has one correct output, use a cheap model (or a script). If it
> needs judgement, pay for capability.**

---

## 6. Keep secrets safe + contribute back

- **Never commit** `.env`, tokens, or PII (leads/contacts). Check before you push:
  `git ls-files | grep -iE '\.env$|leads.*csv'` should return nothing.
- **Sync fixes from `main` often** (see §0). Don't drift.
- **Found/made an SDK fix or doc improvement?** PR it to `NavaiaSolutions/navaia-forge-sdk`
  so everyone benefits — branch off `upstream/main`, make only the SDK change, open a PR.
- **Your own business workforce** (its data, strategy, private config) belongs in **your
  own private repo**, not in the public SDK.

---

## Cheat sheet

```bash
git fetch upstream && git merge upstream/main   # get latest fixes FIRST
docker compose -f docker-compose.dist.yml up -d # backend
.venv/Scripts/python scripts/setup_db.py        # once
# build: create workforce -> add orchestrator + specialists -> connect integrations -> dispatch tasks
# models: cheap for leg work, capable for orchestration/writing, script for deterministic
# secrets: .env only, never commit; cloud-only tokens => run those tasks on the cloud
```
