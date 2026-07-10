# Fareegi — Set Up Your AI Workforce (Locally Hosted)

> **The one guide** for standing up your own AI workforce on NavaiaForge, running it
> entirely on your own machine, and (optionally) watching it from the Fareegi cloud
> dashboard. General-purpose: it covers every workforce aspect, not one specific team.
> Point your coding CLI at this file and it will know how the whole thing fits together.

**"Fareegi" (فريقي) = "my team."** That's the product name (`fareegi.navaia.sa`) and the
mental model: you're assembling a small team of AI agents that work like colleagues.

---

## Table of contents

1. [The mental model — what runs where](#1-the-mental-model--what-runs-where)
2. [Do I need the SDK repo, or just `pip install`?](#2-do-i-need-the-sdk-repo-or-just-pip-install)
3. [Prerequisites](#3-prerequisites)
4. [Step 1 — Get the backend files](#4-step-1--get-the-backend-files)
5. [Step 2 — Configure `.env`](#5-step-2--configure-env)
6. [Step 3 — Start the stack + initialize the database](#6-step-3--start-the-stack--initialize-the-database)
7. [Step 4 — Choose your agent runtime (the CLI)](#7-step-4--choose-your-agent-runtime-the-cli)
8. [Step 5 — Install the SDK + mint an API key](#8-step-5--install-the-sdk--mint-an-api-key)
9. [Step 6 — Build your workforce](#9-step-6--build-your-workforce)
10. [Step 7 — Connect integrations (optional, and entirely your choice)](#10-step-7--connect-integrations-optional-and-entirely-your-choice)
11. [Step 8 — Run tasks and watch them](#11-step-8--run-tasks-and-watch-them)
12. [Step 9 (optional) — Sync to the Fareegi dashboard](#12-step-9-optional--sync-to-the-fareegi-dashboard)
13. [Secrets & data hygiene](#13-secrets--data-hygiene)
14. [Troubleshooting — real errors, real fixes (no workarounds)](#14-troubleshooting--real-errors-real-fixes-no-workarounds)
15. [Cheat sheet](#15-cheat-sheet)

---

## 1. The mental model — what runs where

The single most important thing to understand: **your machine runs the work; the cloud
just watches it.**

```
Your machine (you own this)                    fareegi.navaia.sa (optional)
┌─────────────────────────────────────┐        ┌──────────────────────────┐
│  Backend container (Docker)         │  sync  │  Dashboard / UI          │
│   API + Postgres + Weaviate + Redis │ ─────▶ │  Outputs, chats,         │
│  Agent runtime CLI (navaia-code /   │        │  scheduler, monitoring   │
│    claude) + YOUR LLM keys          │        │  Marketplace catalog     │
│  Your .env secrets + your data      │        │                          │
│                                     │        │  ← display only:         │
│  ← runs EVERYTHING:                │        │    no execution,         │
│    agents, LLM calls, tasks, RAG    │        │    no LLM keys           │
└─────────────────────────────────────┘        └──────────────────────────┘
        ▲                                               ▲
        │ SDK (pip install navaia-forge)                │ browser
```

| Lives on **your machine** (local)                     | Lives in the **cloud** (Fareegi)              |
|-------------------------------------------------------|-----------------------------------------------|
| The Docker backend (`localhost:8001`)                 | The dashboard: outputs, chats, scheduler      |
| The **agent runtime** — where tasks actually execute  | A copy of your workforce (for visibility)     |
| Your **`.env` secrets** (LLM keys, integration tokens)| **Cloud-only integration secrets** (see below)|
| Your scripts + data (leads, CSVs, PII)                | The marketplace (publish / install teams)     |

**Golden rules**

1. **Secrets live in `.env` (gitignored). Never commit them.**
2. **Some integration tokens are cloud-only.** If an integration's secret exists only in
   the cloud runtime, any task using it **must run on the cloud** — you cannot call it from
   a local script. Dispatch the task and let the cloud runtime do it.
3. **Local wins for execution; cloud wins for visibility.** If the two disagree, trust
   local for *what ran* and cloud for *what you can see*.
4. **Data with PII (leads, contacts) stays local** and gitignored — even in a private repo.

> **Prefer not to run the backend yourself?** Contact `info@navaia.sa` for managed hosting
> where Navaia runs the infrastructure for you. That is **not** the default path this guide
> describes.

---

## 2. Do I need the SDK repo, or just `pip install`?

This trips everyone up, so here it is plainly. There are **two separate things**:

| Piece | What it is | How you get it |
|-------|-----------|----------------|
| **The SDK** (`navaia-forge`) | A typed Python HTTP client — how your code talks to the backend | `pip install navaia-forge` — that's all |
| **The backend** | The Docker image + a few support files (`docker-compose.dist.yml`, `.env.example`, `scripts/setup_db.py`) | From the **repo** |

So:

- **`pip install navaia-forge` alone is NOT enough** to run a workforce. It gives you the
  client, but nothing to talk to. You still need the backend running.
- **You do not need to clone the whole repo** either — the backend is a published Docker
  image. You only need **three files** from the repo to start it: the compose file, an
  `.env`, and the DB init script.

**Two valid setups:**

**A) Clone the repo (simplest — recommended for first-timers).** You get the compose file,
`.env.example`, `scripts/setup_db.py`, examples, and the `workforce/` reference material all
at once, and you can `pip install -e packages/python` to track the SDK with the backend.

```bash
git clone https://github.com/NavaiaSolutions/navaia-forge-sdk.git
cd navaia-forge-sdk
```

**B) Grab only the files you need (minimal — no clone).** Good for a server or CI box.

```bash
# The compose file + a starter env; then pip-install the published SDK.
curl -fLO https://raw.githubusercontent.com/NavaiaSolutions/navaia-forge-sdk/main/docker-compose.dist.yml
curl -fLO https://raw.githubusercontent.com/NavaiaSolutions/navaia-forge-sdk/main/.env.example
curl -fLO https://raw.githubusercontent.com/NavaiaSolutions/navaia-forge-sdk/main/scripts/setup_db.py
pip install navaia-forge
```

> **On Windows** use `curl.exe` (not the PowerShell `curl` alias) so `-fLO` behaves.

**Rule of thumb:** *repo for the backend + tooling, `pip` for the client.* If you only ran
`pip install` and nothing works, you skipped the backend — go back to Step 1.

---

## 3. Prerequisites

- **Docker 24+** with Compose v2 (the `docker compose` subcommand, **not** the old
  `docker-compose` binary).
- **Python ≥ 3.10** (3.12 recommended) for the SDK.
- **~4 GB RAM, 2 vCPUs** free for the stack (API + Postgres + Weaviate + Redis).
- **One LLM credential**, depending on the runtime you pick in Step 4:
  - an **OpenRouter API key** (`https://openrouter.ai/keys`) for `navaia_code`, **or**
  - the **Claude Code CLI** logged in (`claude login`) for `claude_max`.

---

## 4. Step 1 — Get the backend files

Follow **A** or **B** from [§2](#2-do-i-need-the-sdk-repo-or-just-pip-install). After this
you should have, in your working directory:

```
docker-compose.dist.yml
.env.example
scripts/setup_db.py
```

The compose file defines four services — the API (`navaia-forge-api`), Postgres, Weaviate
(vector DB), and Redis. Your data lives in Docker volumes you control.

---

## 5. Step 2 — Configure `.env`

```bash
cp .env.example .env
```

Then edit `.env`. The essentials:

```bash
# ── Core ──────────────────────────────────────────────
SECRET_KEY=<openssl rand -hex 32>      # app secret, ≥32 random bytes
DEBUG=true                             # REQUIRED for local dev (see note below)

# ── Database ──────────────────────────────────────────
POSTGRES_USER=navaia_forge
POSTGRES_PASSWORD=<a strong password>
POSTGRES_DB=navaia_forge

# ── Agent runtime ─────────────────────────────────────
OPENROUTER_API_KEY=sk-or-v1-...        # needed for the navaia_code runtime
# CLAUDE_CLI_PATH=claude               # uncomment if you use the claude_max runtime

# ── Ports / vector DB / CORS ─────────────────────────
API_PORT=8001
WEAVIATE_API_KEY=<openssl rand -hex 32>   # or leave empty for anonymous access
ALLOWED_ORIGINS=http://localhost:3030,http://localhost:3000
```

> **`DEBUG=true` is required for local dev.** As the `.env.example` notes, `DEBUG=true`
> skips the production-only security checks that don't apply to a localhost setup. Keep it
> `true` locally; only set `false` when you deploy behind a real domain with real origins.

Generate the two secrets:

```bash
openssl rand -hex 32     # run twice — one for SECRET_KEY, one for WEAVIATE_API_KEY
```

---

## 6. Step 3 — Start the stack + initialize the database

```bash
docker compose -f docker-compose.dist.yml up -d
```

Wait ~30 seconds for the services to go healthy, then verify:

```bash
curl http://localhost:8001/health        # → {"status":"healthy",...}
```

**Initialize the database (one-time).** A fresh install needs its tables created once. The
repo ships `scripts/setup_db.py` for this — run it inside the API container:

```bash
docker cp scripts/setup_db.py navaia-forge-api:/tmp/
docker exec navaia-forge-api python /tmp/setup_db.py
```

> You can also run `python scripts/setup_db.py` from the host if your host can reach
> Postgres, but running it inside the container avoids host networking issues. Use the
> container form and you won't hit them.

Your backend is now at `http://localhost:8001` with a schema ready to use.

---

## 7. Step 4 — Choose your agent runtime (the CLI)

This is the part most guides get wrong, so read it carefully.

You bring your own LLM by installing a **coding-agent CLI** and pointing your workforce at
it. Which CLI is used is decided by the workforce's **`runtime_mode`** field. **The mode you
set MUST correspond to a CLI you have actually installed and authenticated** — otherwise
tasks fail (often *silently*: the task just never progresses).

The SDK supports **exactly two** runtime modes — `RuntimeMode = Literal["claude_max",
"navaia_code"]`. Those are your only valid choices:

| `runtime_mode`      | CLI it drives                          | Credential you provide            | Notes |
|---------------------|----------------------------------------|-----------------------------------|-------|
| **`navaia_code`** ⭐ | **Navaia Code** (multi-model via OpenRouter) | `OPENROUTER_API_KEY` in `.env` | **The recommended default.** You pay OpenRouter directly; pick any model on the OpenRouter catalog. |
| `claude_max`        | **Claude Code** (the `claude` CLI)     | `claude login` **or** `OPENROUTER_API_KEY` | Use when you standardize on the Claude Code CLI. It's the SDK's built-in default. |

> You may see `claw_code` in older notes. It is **not** a supported `runtime_mode` (it only
> exists as a model-*provider* value). Setting it leaves the runtime pointing at a `claw`
> binary that isn't there, so tasks fail silently. Use one of the two modes above.

### ⭐ Recommended: Navaia Code

Navaia Code is the intended primary runtime — one CLI, any model, billed through your own
OpenRouter account with no markup.

```bash
navaia-code --version           # confirm it's installed
export OPENROUTER_API_KEY=sk-or-v1-your-key    # already in .env; export for host use
```

Create workforces with `runtime_mode="navaia_code"` (see Step 6).

### Alternative: Claude Code

```bash
claude --version                # https://www.anthropic.com/claude-code
claude login                    # authenticate with your Anthropic subscription / key
```

Create workforces with `runtime_mode="claude_max"`.

### ⚠️ The runtime-mode gotcha (know this before you debug anything)

> **`runtime_mode` must map to a CLI you have actually installed and authenticated.**
> If you set `navaia_code` but Navaia Code isn't installed, the workforce points at a CLI
> that isn't there and **the task fails silently.** The *correct* fix is to
> install/authenticate the CLI the mode names — **not** to flip modes at random until one
> appears to work. Verify the mode any time tasks stall (see the troubleshooting table).

That's the entire model-configuration story. **The SDK never sees or stores your LLM
credentials** — they stay in your `.env` / your CLI login.

---

## 8. Step 5 — Install the SDK + mint an API key

Install the client (skip if you did `pip install -e packages/python` from the clone):

```bash
pip install navaia-forge        # Python ≥ 3.10
```

Every SDK call authenticates with an `nf_...` API key. Get one by registering/logging in,
then creating a long-lived key:

```python
from navaia_forge import NavaiaForgeClient

# 1. Register or log in (email/password) to get a JWT
client = NavaiaForgeClient(base_url="http://localhost:8001")
pair = client.auth.login(email="you@example.com", password="...")

# 2. Use the JWT to mint a long-lived API key
authed = NavaiaForgeClient(base_url="http://localhost:8001", api_key=pair.access_token)
key = authed.auth.create_key("my-dev-key")
print(key.api_key)   # nf_... — shown ONCE, store it in .env, never commit it
```

From then on:

```python
client = NavaiaForgeClient(base_url="http://localhost:8001", api_key="nf_...")
```

> **Auth detail (relevant if you're on an older SDK):** JWTs (`eyJ...`) go in the
> `Authorization: Bearer` header; long-lived `nf_...` keys go in `X-API-Key`. The SDK
> (≥ 0.2.3) picks the right header automatically by detecting the `eyJ` prefix. If you get
> spurious `401 User not found` / `500` on key creation, your SDK is too old — **upgrade**,
> don't hand-set headers.

---

## 9. Step 6 — Build your workforce

Every workforce is **run by exactly one orchestrator**, plus **any number of specialists**
(from zero upward — there is no fixed or required agent count). The orchestrator is the one
non-negotiable: it receives the task, holds the map of the team's capabilities, and routes
work. You then add however many specialists your job actually needs, wired by edges and
sharing knowledge and tools. Keep it boring and small; add an agent only when a real,
distinct job appears.

### The shape

```python
from navaia_forge import NavaiaForgeClient

client = NavaiaForgeClient(base_url="http://localhost:8001", api_key="nf_...")

# 1. Create the workforce — set the runtime_mode you chose in Step 4.
wf = client.workforces.create(name="Research Team", runtime_mode="navaia_code")

# 2. Add an orchestrator (the "GM") that knows its team and routes work.
gm = client.agents.create(
    workforce_id=wf.id, name="GM", role="orchestrator",
    instructions=(
        "You route work to the right specialist. You hold the map of every "
        "agent's capabilities. You never do specialist work yourself."
    ),
    model_provider="openrouter", model_name="<cheap-model>",
)

# 3. Add specialists — each does ONE job.
researcher = client.agents.create(
    workforce_id=wf.id, name="Researcher", role="research",
    instructions="Find and summarize information on any topic.",
    model_provider="openrouter", model_name="<cheap-model>",
)
writer = client.agents.create(
    workforce_id=wf.id, name="Writer", role="writer",
    instructions="Turn research notes into a polished, customer-ready brief.",
    model_provider="openrouter", model_name="<ceiling-model>",  # customer-facing → best model
)

# 4. Wire the flow with edges: researcher → writer.
client.workforces.edges.create(
    workforce_id=wf.id, source_agent_id=researcher.id, target_agent_id=writer.id,
)
```

### Give the team shared knowledge (RAG)

```python
kb = client.knowledge.create(name="Product Docs", workforce_id=wf.id)
# Now every agent can retrieve from it instead of you stuffing docs into prompts.
hits = client.knowledge.search(kb.id, query="deployment checklist")
```

### The four principles that make multi-agent reliable

1. **One orchestrator that knows its team.** Put the *capability map of every agent* in the
   orchestrator's instructions. It routes; it never does the specialist work.
2. **Each specialist does one job.** Researcher researches. Writer writes. Don't blur roles.
3. **Don't invent agents you don't need.** More agents = more coordination = more cost. Add
   one only for a real, distinct job.
4. **Write self-contained task descriptions.** The single biggest driver of reliability: put
   *everything the agent needs* in the task itself — the steps, the endpoints, the rules —
   especially for cheaper models. A vague task fails; a spec-shaped task succeeds.

---

## 10. Step 7 — Connect integrations (optional, and entirely your choice)

> **Integrations are 100% user-driven.** NavaiaForge ships **no** business integrations of
> its own — it gives you the *mechanism* to attach whichever third-party services **you**
> decide your workforce needs (a CRM, an email/SMTP provider, a data/enrichment provider, a
> messaging channel, or none at all). Which providers you use, and the keys behind them, are
> **yours**. A workforce with zero integrations is perfectly valid — add one only when an
> agent actually needs that service.

Browse what plugins your backend exposes, then attach the ones you want. The provider names
below are **placeholders** — substitute whatever `list_plugins()` returns for your setup:

```python
client.integrations.list_plugins()   # see which plugins your backend supports
client.integrations.create(
    workforce_id=wf.id,
    plugin_name="<plugin-from-list_plugins>",   # e.g. your CRM, email, or data provider
    display_name="<your label>",
    config_json={"api_key": "..."},             # YOUR secret — lives here, encrypted at rest
)
```

You can also add them over the REST API (handy for scripting or letting an AI do it):

```bash
curl -X POST http://localhost:8001/api/v1/integrations \
  -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json" \
  -d '{"workforce_id":"YOUR_WF_ID","plugin_name":"<your-plugin>",
       "config_json":{"api_key":"..."}}'
```

> **Keep secrets in the integration record — not in task text.** The **correct** place for
> a provider secret is the integration's `config_json` (as above), where it's stored
> encrypted. Do **not** paste secrets into task descriptions or hard-code them; that's the
> anti-pattern to avoid.

> **Cloud-only integrations.** Some providers hold their secret only in the cloud runtime.
> Those come back **redacted** locally, and any task using them **must be dispatched to the
> cloud** — a local script cannot call them. This is by design, not a bug to route around.

---

## 11. Step 8 — Run tasks and watch them

Submit work to the **workforce**, not to a specific agent (unless you want to skip the
orchestrator — see below). The platform routes, executes, retries, and streams events.

```python
task = client.tasks.create(workforce_id=wf.id, title="Survey 2025 LLM efficiency papers")
final = client.tasks.wait_for_completion(task.id)   # blocks with smart polling
print(final.status, final.result)
```

Route straight to a specialist to save the orchestrator's tokens when you already know who
should do it:

```python
client.tasks.create(workforce_id=wf.id, title="...", agent_id=researcher.id)
```

Watch everything live over WebSocket (no polling):

```python
from navaia_forge import NavaiaForgeWs, HttpConfig

ws = NavaiaForgeWs(HttpConfig(base_url="http://localhost:8001", api_key="nf_..."))
ws.on("task:status",  lambda e: print("task:",  e["task_id"], e["status"]))
ws.on("agent:status", lambda e: print("agent:", e["agent_id"], e["status"]))
ws.on("chat:message", lambda e: print(e["role"], e["content"]))
ws.connect()
ws.run_forever()
```

Inspect cost and performance when you want to:

```python
client.observability.cost(workforce_id=wf.id)          # cost by model / by agent
client.observability.agent_metrics(agent_id=writer.id) # per-agent performance
```

---

## 12. Step 9 (optional) — Sync to the Fareegi dashboard

Everything above works **fully offline**. When you want a visual dashboard, to share a team,
or to publish to the marketplace, push to the cloud. **Execution still happens locally** —
the cloud is display only.

```python
import os
from navaia_forge import NavaiaForgeClient

local = NavaiaForgeClient(base_url="http://localhost:8001",
                          api_key=os.environ["NAVAIA_LOCAL_API_KEY"])
cloud = NavaiaForgeClient(base_url="https://fareegi.navaia.sa",
                          api_key=os.environ["NAVAIA_CLOUD_API_KEY"])

result = local.sync.push(wf.id, remote=cloud)   # now visible on the dashboard
print("Synced:", result.action)
```

Get a cloud API key by signing up at `fareegi.navaia.sa` → **Settings → API Keys**.

**Sync rules (so you don't clobber anything):**

- **A bundle sync is a schema merge, not a secret push.** Cloud exports ship a
  `redacted_fields` list; the import side honours it and does **not** overwrite local
  secrets. Don't try to "force-sync" tokens — populate secrets via the integration record
  instead, and re-authenticate after any sync that touched a non-empty `config_json`.
- **Diff before you sync.** List workforces/agents/integrations/edges on both sides and
  compare, so you decide push vs pull vs a surgical `PUT` *before* writing.
- **To change one field**, use a targeted `update()` / `PUT` — not a full bundle push.
- Every entity carries an `origin_id`, so round-trips **don't duplicate** entities.

Publish / install from the marketplace:

```python
cloud.workforces.publish(result.workforce_id, tagline="...", category="research")
wf2 = cloud.marketplace.install(listing_id)     # someone else installs it
local.sync.pull(wf2.id, remote=cloud)           # pull down to actually run it
```

---

## 13. Secrets & data hygiene

- **Never commit** `.env`, tokens, or PII (leads/contacts). Verify before pushing:

  ```bash
  git ls-files | grep -iE '\.env$|leads.*csv'   # must return NOTHING
  ```

- **`.env` is gitignored — keep it that way.** Secrets belong in `.env` or the integration
  record, never in code, task text, or chat.
- **PII stays local and gitignored**, even in a private repo.
- **Cloud-only tokens** (see §1/§10) never come down to local — that's intentional.

---

## 14. Troubleshooting — real errors, real fixes (no workarounds)

Each row is the **root-cause fix**, not a patch over the symptom.

| Symptom | Root cause | Correct fix |
|---------|-----------|-------------|
| `pip install navaia-forge` → *"requires a different Python"* | SDK needs Python ≥ 3.10 | `python3.12 -m venv .venv` and install into that |
| SDK calls raise `ConnectionError` | Backend isn't running | `docker compose -f docker-compose.dist.yml ps`; `curl http://localhost:8001/health`. Start it if down. |
| Backend **won't boot** at all | `DEBUG` not set to `true` for local dev | Set `DEBUG=true` in `.env` (§5). Only use `false` when deployed behind a real domain with real origins. |
| Every SDK call `500`s / *"no such table"* | Database wasn't initialized | Run the DB init **inside the container**: `docker cp scripts/setup_db.py navaia-forge-api:/tmp/ && docker exec navaia-forge-api python /tmp/setup_db.py` (§6). |
| `401 Unauthorized` on normal calls | Wrong/revoked API key | Mint a fresh `nf_...` key (§8) and update `.env`. |
| `401 User not found` / `500` when **creating** a key | Old SDK sent the JWT in the wrong header | **Upgrade the SDK** (≥ 0.2.3 auto-detects `eyJ` JWTs → `Authorization: Bearer`). Don't hand-set headers. |
| Task fails *"can't reach the language model"* | Runtime CLI not configured | Set `OPENROUTER_API_KEY` (for `navaia_code`) **or** `claude login` (for `claude_max`) on the host — Step 4. |
| Task **hangs / fails silently**, no LLM error | `runtime_mode` points at a CLI that isn't installed/reachable (e.g. `navaia_code` with no Navaia Code, or an invalid legacy value like `claw_code`) | Verify the mode, then **install/authenticate the CLI that mode names** (§7). Set the workforce to one of the two supported modes whose CLI is actually present — don't flip modes blindly. |
| An agent can't use a provider secret | Secret wasn't registered as an integration | Add it via the integration's `config_json` (§10) — not in task text or hard-coded. |
| A cloud-only integration's task fails locally | Its secret is held only in the cloud (redacted locally) | Dispatch that task **to the cloud** runtime — it can't run locally by design (§1). |
| WebSocket events never arrive | Reverse proxy strips the upgrade | Configure WebSocket upgrade headers (`Upgrade`, `Connection`) on the proxy; confirm the SDK `base_url` reaches the backend. |
| Windows: `setup_db` one-liner / `curl` misbehaves | PowerShell quoting + the `curl` alias | Use the `setup_db.py` script (not `python -c`) and `curl.exe` (not the `curl` alias). |
| Sync overwrote/blanked a local secret | Tried to push tokens through a bundle sync | Bundles honour `redacted_fields` and won't carry secrets. Set secrets via the integration record and re-authenticate after sync (§12). |

**When in doubt:** check `docker compose ps`, then `/health`, then the workforce's
`runtime_mode`, then your API key — in that order. Most failures are one of those four.

For SDK bugs, open an issue on
[`navaia-forge-sdk`](https://github.com/NavaiaSolutions/navaia-forge-sdk/issues). For
backend/licensing/managed hosting: `info@navaia.sa`.

---

## 15. Cheat sheet

```bash
# ── Get the backend (repo OR three files) ──────────────────────
git clone https://github.com/NavaiaSolutions/navaia-forge-sdk.git && cd navaia-forge-sdk
#   ...or minimal:
#   curl -fLO .../docker-compose.dist.yml .env.example scripts/setup_db.py

# ── Configure ──────────────────────────────────────────────────
cp .env.example .env            # set SECRET_KEY, POSTGRES_PASSWORD, DEBUG=true,
                                # OPENROUTER_API_KEY (navaia_code) or `claude login` (claude_max)

# ── Start + init ──────────────────────────────────────────────
docker compose -f docker-compose.dist.yml up -d
curl http://localhost:8001/health                                 # {"status":"healthy"}
docker cp scripts/setup_db.py navaia-forge-api:/tmp/ && \
  docker exec navaia-forge-api python /tmp/setup_db.py            # one-time DB init

# ── Client ─────────────────────────────────────────────────────
pip install navaia-forge        # (or: pip install -e packages/python from the clone)

# ── Build (in Python) ─────────────────────────────────────────
# workforces.create(runtime_mode="navaia_code")  →  add orchestrator + specialists
#   → edges.create() to wire the flow  →  integrations.create() for the services you need
#   → tasks.create() to run  →  observability / WebSocket to watch status

# ── Rules of thumb ────────────────────────────────────────────
# runtime_mode MUST match an installed CLI (navaia_code = OpenRouter key; claude_max = claude login)
# every workforce has one orchestrator; add specialists only when a real, distinct job appears
# secrets: .env + integration config only, never committed; cloud-only tokens → run those tasks on the cloud
```

---

