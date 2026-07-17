"""Export / import the whole workforce as a portable, git-committable bundle.

This is the "reconstruct anywhere, even without this backend" mechanism.

  export  snapshots the live workforce — workforce settings, all agents + edges,
          knowledge bases (incl. their GitHub repo links), and integrations
          (secrets REDACTED) — into one JSON committed to git.
  import  rebuilds that snapshot on ANY NavaiaForge backend (the current cloud,
          a replacement backend, or a future managed one), creating/updating in
          place by origin_id. Nothing is tied to a specific container.

Which backend a command targets follows NAVAIA_BASE_URL (default: cloud);
see scripts/nav_env.py. Combined with the config-as-code in workforce/agents/*.md
(deployed by scripts/deploy_agents.py), this makes the workforce fully portable.

Reconstruction caveats — by design, secrets never travel in a bundle:
  * Integration secrets are redacted. On a fresh backend, re-enter them (or keep
    them in .env); `import` lists which integrations still need setup.
  * GitHub-backed knowledge repos come back with requires_reauth=True. Reconnect
    GitHub (OAuth) on the target so agents can read the private repo again.

Usage:
    python scripts/workforce_snapshot.py export           # backend -> file
    python scripts/workforce_snapshot.py import           # file -> backend (create/update in place)
    python scripts/workforce_snapshot.py import --force    # win even if the target changed since last sync
"""
from __future__ import annotations

import argparse
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav_env
from navaia_forge import NavaiaForgeClient
from navaia_forge.errors import SyncConflictError

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNAPSHOT = os.path.join(ROOT, "workforce", "snapshot", "workforce_bundle.json")


def _client() -> NavaiaForgeClient:
    key = nav_env.env("BUSINESS_NF")
    if not key:
        raise SystemExit("BUSINESS_NF not found in environment or .env")
    return NavaiaForgeClient(api_key=key, base_url=nav_env.base_url())


def _summarize(bundle) -> None:
    wf = bundle.workforce
    print(f"  workforce : {wf.name}  (runtime_mode={wf.runtime_mode}, status={wf.status})")
    print(f"  agents    : {len(bundle.agents)}   edges: {len(bundle.edges)}")
    print(f"  knowledge : {len(bundle.knowledge_bases)} KB(s)")
    for kb in bundle.knowledge_bases:
        repos = ", ".join(f"{r.owner}/{r.repo}@{r.default_branch}" for r in kb.repos) or "—"
        print(f"      • {kb.name}: repos=[{repos}] texts={len(kb.texts)}")
    print(f"  integrations: {len(bundle.integrations)}")
    for i in bundle.integrations:
        redacted = f" (redacted: {', '.join(i.redacted_fields)})" if i.redacted_fields else ""
        print(f"      • {i.plugin_name} [{i.status}]{redacted}")


def do_export() -> None:
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    client = _client()
    print(f"Exporting workforce {nav_env.CLOUD_WORKFORCE_ID} from {nav_env.base_url()} ...")
    bundle = client.sync.export_to_file(nav_env.CLOUD_WORKFORCE_ID, SNAPSHOT)
    print(f"Wrote {SNAPSHOT}")
    _summarize(bundle)
    print("\nCommit workforce/snapshot/workforce_bundle.json to git to make this state reproducible.")


def do_import(force: bool) -> None:
    if not os.path.exists(SNAPSHOT):
        raise SystemExit(f"No snapshot at {SNAPSHOT} — run `export` first.")
    client = _client()
    print(f"Importing {SNAPSHOT} into {nav_env.base_url()} (force={force}) ...")
    try:
        result = client.sync.import_from_file(SNAPSHOT, force=force)
    except SyncConflictError as e:
        print("CONFLICT: the target was modified since the last sync.")
        print("Re-run with --force to overwrite, after reviewing the remote state.")
        raise SystemExit(1) from e
    print(f"Done: workforce {result.workforce_id} — {result.action}")
    print(f"  agents       created={result.agents.created} updated={result.agents.updated} deleted={result.agents.deleted}")
    print(f"  knowledge    created={result.knowledge_bases.created} updated={result.knowledge_bases.updated}")
    print(f"  integrations created={result.integrations.created} updated={result.integrations.updated}")
    if result.integrations_require_setup:
        print("  ⚠ integrations still needing secrets/re-auth: " + ", ".join(result.integrations_require_setup))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("export", help="Snapshot the backend workforce into the git-committed bundle.")
    imp = sub.add_parser("import", help="Rebuild the workforce on the target backend from the bundle.")
    imp.add_argument("--force", action="store_true", help="Overwrite even if the target changed since last sync.")
    args = ap.parse_args()

    if args.cmd == "export":
        do_export()
    else:
        do_import(args.force)


if __name__ == "__main__":
    main()
