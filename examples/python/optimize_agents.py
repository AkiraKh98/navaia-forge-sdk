#!/usr/bin/env python3
"""Apply a cost-optimization policy to a workforce's agents — the SDK way.

Everything here uses SDK primitives (no hand-rolled router). Per agent it sets:
  - model_name       : a cheap default model
  - escalation_model : a ceiling model the runtime escalates to only when needed
  - max_turns        : a turn cap sized to the agent's job (leg-work = few turns)
Then it prints the SDK's native cost breakdown so you can see where the budget goes.

    export NAVAIA_API_KEY=nf_...          # your workforce API key
    export NAVAIA_WORKFORCE_ID=...        # target workforce id
    python examples/python/optimize_agents.py --dry-run   # show, write nothing
    python examples/python/optimize_agents.py             # apply
"""
from __future__ import annotations

import argparse
import os
import sys

from navaia_forge import NavaiaForgeClient

# Edit these to change your tiers (see openrouter.ai/models).
CHEAP = "qwen/qwen3.6-plus"
CEILING = "moonshotai/kimi-k2.6"
BASE_URL = os.environ.get("NAVAIA_BASE_URL", "https://fareegi.navaia.sa")


def policy(agent) -> tuple[str, str, int]:
    """Return (model_name, escalation_model, max_turns) for an agent, by its role.

    Cheap model is the default everywhere; the ceiling is the escalation target. Only
    max_turns really differs — leg-work agents get a hard cap because each turn is a
    paid model round-trip.
    """
    role = (agent.role or agent.name or "").lower()
    if any(k in role for k in ("general manager", "orchestrat", "gm")):
        return CHEAP, CEILING, 10   # routes/decomposes; escalate on genuinely hard calls
    if any(k in role for k in ("marketing", "writer", "content", "creative")):
        return CHEAP, CEILING, 8    # draft cheap, let the runtime escalate to polish
    return CHEAP, CEILING, 4        # leg-work / phased: cap turns hard


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Show changes, write nothing.")
    args = ap.parse_args()

    key = os.environ.get("NAVAIA_API_KEY")
    wf = os.environ.get("NAVAIA_WORKFORCE_ID")
    if not key or not wf:
        sys.exit("Set NAVAIA_API_KEY and NAVAIA_WORKFORCE_ID in the environment.")

    client = NavaiaForgeClient(api_key=key, base_url=BASE_URL)

    for a in client.agents.list(workforce_id=wf):
        model, esc, turns = policy(a)
        line = f"{a.name:<8} {(a.role or '')[:26]:<26} -> {model} | esc={esc} | max_turns={turns}"
        if args.dry_run:
            print("DRY", line)
            continue
        client.agents.update(a.id, model_name=model, escalation_model=esc, max_turns=turns)
        print("OK ", line)

    # Native cost visibility — no custom tracking needed.
    try:
        c = client.observability.cost(wf, days=30)
        print(f"\n30-day cost: ${c.total_cost_usd:.2f} across {c.total_tokens} tokens")
        for m in c.by_model:
            print(f"  {m.model:<28} ${m.cost_usd:.2f}")
    except Exception as e:  # cost endpoint may be empty on a brand-new workforce
        print(f"\n(cost summary unavailable: {e})")


if __name__ == "__main__":
    main()
