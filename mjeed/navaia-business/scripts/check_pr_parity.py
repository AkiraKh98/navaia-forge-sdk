#!/usr/bin/env python3
"""Verify the SDK PR carries the SAME capabilities as the local workforce.

The whole point of the PR is that the deployed workforce can do what the local one does.
That guarantee is easy to lose silently: a script gets added or fixed here and nobody
mirrors it, and the deployed agents quietly run an older capability set. It has already
happened once — the payload was scoped from the import graph, which excludes standalone
operator commands, and `import_selected_leads.py` (the only path from a scraped pool into
the CRM) was left out.

This compares the two script sets and reports MISSING, MODIFIED and EXTRA. It writes
nothing; it is a check, not a sync.

Usage:
    python scripts/check_pr_parity.py
    python scripts/check_pr_parity.py --sdk <path-to-navaia-forge-sdk>
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import sys

if (sys.stdout.encoding or "").lower().replace("-", "") != "utf8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SDK = os.path.join(os.path.dirname(LOCAL), "..", "navaia-forge-sdk")
PR_SUBDIR = os.path.join("mjeed", "navaia-business")

# Local-only by design. These never belong in the PR:
#   check_pr_parity  — compares the two checkouts, meaningless inside one of them
#   fetch_prospects / reveal_prospect_emails — Snov tools, excluded from the agent pipeline
#     by operator decision, kept locally for manual use
LOCAL_ONLY = {"check_pr_parity.py"}


def _digest(path: str) -> str:
    """Content hash, newline-normalised — CRLF/LF differences are not a capability drift."""
    with io.open(path, "rb") as f:
        return hashlib.sha1(f.read().replace(b"\r\n", b"\n")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sdk", default=DEFAULT_SDK)
    args = ap.parse_args()

    pr_scripts = os.path.join(args.sdk, PR_SUBDIR, "scripts")
    if not os.path.isdir(pr_scripts):
        raise SystemExit(f"SDK scripts dir not found: {pr_scripts}\n"
                         f"Pass --sdk <path> if the checkout lives elsewhere.")

    local = {f for f in os.listdir(LOCAL) if f.endswith(".py")} - LOCAL_ONLY
    shipped = {f for f in os.listdir(pr_scripts) if f.endswith(".py")}

    missing = sorted(local - shipped)
    extra = sorted(shipped - local)
    modified = sorted(f for f in (local & shipped)
                      if _digest(os.path.join(LOCAL, f)) != _digest(os.path.join(pr_scripts, f)))

    if missing:
        print(f"MISSING from the PR ({len(missing)}) — deployed agents cannot do these:")
        for f in missing:
            print(f"   {f}")
    if modified:
        print(f"\nMODIFIED — local is newer ({len(modified)}):")
        for f in modified:
            print(f"   {f}")
    if extra:
        print(f"\nEXTRA in the PR ({len(extra)}) — deleted locally, or never local:")
        for f in extra:
            print(f"   {f}")

    if not (missing or modified):
        print(f"IN PARITY — {len(local)} scripts match the PR.")
    else:
        print(f"\n{len(missing)} missing, {len(modified)} stale. Copy them into "
              f"{os.path.join(PR_SUBDIR, 'scripts')} and commit before merging.")
        sys.exit(1)


if __name__ == "__main__":
    main()
