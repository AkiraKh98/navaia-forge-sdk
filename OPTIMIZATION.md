# Cost Optimization for Workforces — Intern Guide

> Get frontier-level results on a low budget — using the **NavaiaForge SDK's own knobs**.
> The SDK already has the ladder built in; you mostly just set the right fields. Read
> `WORKFORCE_GUIDE.md` first.

## The one principle (everything below is this, repeated)

> **Cheapest tool that does the job — at every layer.**

## Two budgets — don't confuse them

- **Build-time** (writing/designing the workforce): free tools — Copilot Free in VS Code,
  and OpenRouter `…:free` models for prototyping. One-off, ~$0.
- **Run-time** (the workforce executing): metered OpenRouter, recurring. This is where the
  SDK knobs below matter. Do the expensive thinking once at build-time so run-time stays cheap.

---

## The SDK already gives you the ladder — set these, don't hand-roll a router

| Goal | SDK lever | How |
|------|-----------|-----|
| Don't pay an LLM for deterministic work | scripts; the agent orchestrates | your `scripts/` + `Agent.tools` |
| **Cheap default, escalate only when needed** | **`model_name` (cheap) + `escalation_model` (ceiling)** | `agents.update(id, model_name=…, escalation_model=…)` |
| **Cap spend per agent** | **`max_turns`** (+ `config_json.autonomy_limit`) | `agents.update(id, max_turns=…)` |
| Stop runaway agent-to-agent loops | edge **`max_runs`** | `workforces.edges.update(edge_id, max_runs=…)` |
| Give only the context needed | **`knowledge_bases`** (+ `config_json.memory`) | attach a KB → retrieval, not prompt-stuffing |
| Route to the right agent (skip the GM) | task **`agent_id`** + edge `condition_expr`/`approval_mode` | `tasks.create(…, agent_id=…)` |
| See where the money actually goes | **`observability.cost()` / `agent_metrics()`** | `client.observability.cost(wf)` |

---

### 1. Deterministic floor — scripts, not model calls
If a task has one correct output (fetch, parse, dedup, validate, format), a **script** does
it for $0. Give the agent `tools`/scripts and let it *orchestrate*; don't make the model do
the mechanical work. (Bonus: it also dodges flaky tool-call JSON from cheaper models.)

### 2. Native escalation — `model_name` + `escalation_model` (this replaces any custom router)
Set the cheap model as the default and the ceiling as the escalation target. The **runtime
escalates for you** — you do not build a router.
```python
client.agents.update(agent_id,
    model_name="qwen/qwen3.6-plus",          # cheap default (rung 1)
    escalation_model="moonshotai/kimi-k2.6", # ceiling, used only when the runtime escalates
)
```
This *is* the rung-1 → rung-2 cascade. (The exact escalation trigger is backend-controlled.)

### 3. Cap the spend — `max_turns` (the most overlooked knob)
Every "turn" is a model round-trip = money. A leg-work agent that just drives a script does
**not** need the default 25 turns — give it 3–5. This alone can cut an agent's cost several×.
```python
client.agents.update(agent_id, max_turns=4)          # leg-work agent
# extra caps: config_json={"autonomy_limit": N};  edges: max_runs=N to stop loops
```

### 4. Minimal context — knowledge bases + memory
Tokens = money. Attach a **knowledge base** so the agent *retrieves* the relevant slice
instead of you stuffing whole docs into the prompt.
```python
client.agents.update(agent_id, knowledge_bases=[kb_id])
# memory reuse via config_json (see AgentConfig.memory: short_term / long_term)
```

### 5. Route smart — dispatch to the agent, not the whole team
If you know who should do it, send the task straight to that agent and skip the
orchestrator's tokens entirely:
```python
client.tasks.create(wf, "…", agent_id=tariq_id)      # go direct
```
Use edges with `condition_expr` + `approval_mode="auto_run"` so a specialist only fires when
its condition holds — not on every task.

### 6. Measure it — the SDK tracks cost natively (don't guess)
```python
c = client.observability.cost(workforce_id, days=30)
for m in c.by_model:  print(m.model, f"${m.cost_usd:.2f}")
for a in c.by_agent:  print(a.agent_name, f"${a.cost_usd:.2f}")
```
Find the agent/model eating the budget, then lower its `model_name` or `max_turns`. Repeat.
`observability.agent_metrics()` and `agent_evaluations()` add per-agent quality/efficiency.

---

## Recommended per-agent policy

| Agent kind | `model_name` | `escalation_model` | `max_turns` |
|------------|-------------|--------------------|-------------|
| Orchestrator | cheap | ceiling | ~8–10 |
| Writer (customer-facing) | cheap (draft) | ceiling (polish) | ~8 |
| Leg-work / phased | cheap | none or ceiling | ~3–5 |

The ceiling model becomes "the ~10–20% of turns that truly need it," not the default.

## Checklist to hand an intern

```
[ ] Deterministic? -> a script, no LLM.  Agent gets tools + orchestrates.
[ ] Every agent: model_name = cheap.  escalation_model = ceiling (let the runtime escalate).
[ ] Set max_turns low on leg-work agents (3-5); modest on orchestrator/writer (~8).
[ ] Attach a knowledge_base instead of stuffing the prompt.
[ ] Route with task agent_id + edge condition_expr; edge max_runs to cap loops.
[ ] Read observability.cost() weekly; lower the top spender.
[ ] Prototype on OpenRouter :free models; code with Copilot Free — keep run-time metered spend small.
```

See `examples/python/optimize_agents.py` for a runnable version of this policy.

---

# Appendix — the long version (if it hasn't clicked yet)

New to this? Read this section slowly. By the end the knobs above will make obvious sense.

## 1. The workshop analogy

Picture a carpentry workshop. You have:
- **Machines** — a saw, a drill. Each does *one exact thing* perfectly, for basically free.
- **Apprentices** — competent, cheap, handle most of the day's work.
- **A master craftsman** — brilliant, expensive, and you only have so much of his time.

You would never pay the master to sweep the floor or cut a straight plank — a machine or an
apprentice does that. You call the master **only** for the delicate joinery a customer will
run their hand over.

Your LLM workforce is exactly this shop:
- **Machines = scripts** (rung 0) — deterministic work, ~$0.
- **Apprentices = the cheap model** (e.g. qwen) — the default for routine judgement.
- **Master = the ceiling model** (e.g. kimi) — reserved for the hard or customer-facing bits.

The entire optimization is just: **stop paying the master to sweep.**

## 2. How LLM cost actually works (so the knobs make sense)

Three things drive the bill. Each SDK knob targets one of them:

| What you pay for | Plain meaning | The knob that controls it |
|------------------|---------------|---------------------------|
| **Tokens** (in + out) | Every word in the prompt and the reply. Output usually costs 3–6× input. | `knowledge_bases` / minimal context |
| **Turns** | One turn = one full request→reply. A 12-turn agent costs ~12× a 1-turn one. | `max_turns` |
| **Model price** | A bigger model charges more per token. | `model_name` / `escalation_model` |

So roughly: **cost ≈ turns × tokens-per-turn × model-price.** Shrink any factor, shrink the bill.
That's why a leg-work agent left at `max_turns=25` on the ceiling model with a giant prompt is
the most expensive mistake you can make — all three factors maxed for work that needed none of it.

## 3. A worked example (feel the ratio)

*Task: classify 100 leads by sector.*

- **Naive:** ask the **ceiling** model, one call each, whole lead record in the prompt, turns
  uncapped. ≈ **$0.30**, and slower.
- **Optimized:** it's nearly deterministic → a **script** handles the clear ones for $0; the
  **cheap** model (half the price, `max_turns=1`, only the fields it needs) does the fuzzy ones;
  the ~10 genuinely ambiguous leads **escalate** to the ceiling model. ≈ **$0.05**.

Same output, ~6× cheaper. (Numbers illustrative — the *ratio* is the lesson.)

## 4. The three questions to ask before every task

1. **Does it have one correct output?** (fetch, parse, dedup, validate, format) → **a script.** No LLM.
2. **Is it routine judgement?** (classify, route, summarize, draft) → **the cheap model.**
3. **Will a human read it, or is it genuinely hard?** → **the ceiling model** (or keep it primary
   for a customer-facing agent).

If you can answer these three, you've internalized the whole guide.

## 5. Mistakes interns make (all of them cost money)

- Reaching for the ceiling model "to be safe." Most work shows **no measurable quality gain** from it.
- Paying an LLM to fetch / parse / reshape data — that's a **script's** job.
- Stuffing whole documents into the prompt. **Retrieve** the relevant slice with a knowledge base.
- Leaving `max_turns` at 25 for an agent that does one step.
- Spinning up a new agent for every little thing — each one adds coordination (and token) cost.
- Never reading `observability.cost()` — you can't optimize what you don't measure.

## 6. Mini-FAQ

- **"Won't a cheap model give worse answers?"** For routine work, not noticeably — and
  `escalation_model` catches the hard cases automatically. For customer-facing output, keep the
  ceiling model as the **primary** (that's why Lina stays on kimi).
- **"What is `escalation_model`, exactly?"** The model the runtime falls back to when the cheap
  default can't handle a task. You set it once per agent; the platform decides when to use it. It
  costs nothing on the turns where it doesn't fire.
- **"How low can `max_turns` go?"** As low as the job's real step count. A script-orchestrating
  agent: 3–5. A multi-step tool user (like a sender): 8–10. Start low; raise only if tasks get cut off.
- **"How do I know it's working?"** Run `client.observability.cost(wf)` weekly and watch the
  `by_model` split tilt toward the cheap model, with total cost flat or falling as volume grows.

> **The one line to remember:** *cheapest tool that does the job — a script if you can, a cheap
> model if you must, the ceiling model only when a human will feel the difference.*
