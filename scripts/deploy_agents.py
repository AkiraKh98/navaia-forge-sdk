"""Deploy the 7 agents' full instructions to the cloud workforce (IN-PLACE UPDATE).

Reads each agent's `### system_prompt (deploy payload)` block from
workforce/agents/*.md and PUTs it onto the matching EXISTING cloud agent
(matched by name). It never creates, renames, or deletes agents — the fixed
7-agent roster is untouched. Key read from .env (BUSINESS_NF); nothing hardcoded.

Usage:
    python scripts/deploy_agents.py              # deploy all 7
    python scripts/deploy_agents.py --only Ahmed,Tariq,Lina   # subset
    python scripts/deploy_agents.py --dry-run    # show what would change, write nothing

See workforce/playbooks/deploy_and_sync.md.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from navaia_forge import NavaiaForgeClient

CLOUD_BASE = "https://fareegi.navaia.sa"
CLOUD_WF = "131bb52f-e5eb-44ad-8134-03dc6908b485"
ROOT = os.path.join(os.path.dirname(__file__), "..")
AGENTS_DIR = os.path.join(ROOT, "workforce", "agents")

FILES = {
    "Ahmed": "ahmed_gm_orchestrator.md",
    "Tariq": "tariq_sdr_lead_fetcher.md",
    "Lina": "lina_marketing.md",
    "Ghida": "ghida_creative.md",
    "Nora": "nora_finance.md",
    "Rashid": "rashid_strategy.md",
    "Fahad": "fahad_account_manager.md",
}


def _env(key: str) -> str:
    m = re.search(rf"^{re.escape(key)}=(.+)$", open(os.path.join(ROOT, ".env")).read(), re.M)
    if not m:
        raise SystemExit(f"{key} not found in .env")
    return m.group(1).strip()


def extract_prompt(fname: str) -> str | None:
    text = open(os.path.join(AGENTS_DIR, fname), encoding="utf-8").read()
    m = re.search(r"###\s*system_prompt \(deploy payload\)\s*\n+```[a-zA-Z]*\n(.*?)\n```", text, re.S)
    return m.group(1).strip() if m else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="Comma-separated agent names (default: all 7).")
    ap.add_argument("--dry-run", action="store_true", help="Show changes, write nothing.")
    args = ap.parse_args()

    wanted = [n.strip() for n in args.only.split(",")] if args.only else list(FILES)

    cloud = NavaiaForgeClient(api_key=_env("BUSINESS_NF"), base_url=CLOUD_BASE)
    agents = {a.name: a for a in cloud.agents.list(workforce_id=CLOUD_WF)}

    for name in wanted:
        a = agents.get(name)
        if not a:
            print(f"!! {name}: no cloud agent found — skipping")
            continue
        prompt = extract_prompt(FILES[name])
        if not prompt:
            print(f"!! {name}: no deploy-payload block in {FILES[name]} — skipping")
            continue
        old = getattr(a, "system_prompt", None) or getattr(a, "instructions", None) or ""
        if args.dry_run:
            print(f"DRY  {name}: {len(old)} -> {len(prompt)} chars (no write)")
            continue
        try:
            cloud.agents.update(a.id, instructions=prompt)
            print(f"OK   {name}: {len(old)} -> {len(prompt)} chars")
        except Exception:
            print(f"!! {name}: update FAILED")
            traceback.print_exc()

    if not args.dry_run:
        print("\n=== verify (re-fetch) ===")
        for name in wanted:
            if name in agents:
                a = cloud.agents.get(agents[name].id)
                sp = getattr(a, "system_prompt", None) or getattr(a, "instructions", None) or ""
                print(f"{name}: now {len(sp)} chars | {sp[:60]!r}")


if __name__ == "__main__":
    main()
