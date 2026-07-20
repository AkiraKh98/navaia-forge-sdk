#!/usr/bin/env python3
"""Refuse to publish real customer data or credentials. Run by the pre-push hook.

Three times on 2026-07-20 real third-party data reached a PUBLIC repository: a customer's
mailbox in a code comment, a named prospect in a commit message, and — after both were
fixed — the same class of mistake again in test fixtures. Every one was written while
explaining a bug, which is exactly when a real example feels most useful.

Discipline demonstrably did not prevent this, so a gate does. This exits non-zero and the
push does not happen.

What it looks for:
  1. Live credentials (OpenRouter/Snov/JWT/bearer shapes, .env contents).
  2. Third-party personal data — addresses at consumer mail hosts, and any name listed in
     the local prospect files, which are gitignored precisely because they are personal
     data under PDPL.
  3. The working-data files themselves, in case a .gitignore rule is ever lost.

It reads prospects.json/contacts.json to know WHICH names are real, so the check adapts as
the CRM grows without anyone maintaining a blocklist. Those files never leave the machine.

Usage:
    python scripts/check_no_leaks.py                 # scan staged + outgoing commits
    python scripts/check_no_leaks.py --range A..B    # scan an explicit range
    python scripts/check_no_leaks.py --all-tracked   # scan the whole working tree
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys

def _repo_root() -> str:
    """The git repo this is being run against, not the one this file lives in.

    The same scanner is deployed inside the public SDK repo at a different depth
    (mjeed/navaia-business/scripts/), where `__file__/..` is NOT the repo root — so
    `git ls-files` and the paths it returns would disagree and the scan would silently
    check nothing. Asking git keeps the two in step wherever the file is checked out.
    """
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             cwd=os.path.dirname(os.path.abspath(__file__)),
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except OSError:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


ROOT = _repo_root()
if (sys.stdout.encoding or "").lower().replace("-", "") != "utf8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Credential shapes. Deliberately narrow: matching "token" as a word would flag every line
# that merely reads a token from the environment, and a check that cries wolf gets bypassed.
_SECRETS = [
    ("OpenRouter key", re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}")),
    ("OpenAI-style key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")),
    ("Bearer literal", re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{24,}")),
    ("assigned secret", re.compile(
        r"(TWENTY_TOKEN|SNOV_USER_SECRET|ZOHO_PASS|BUSINESS_NF|SECRET_KEY|POSTGRES_PASSWORD)"
        r"\s*=\s*['\"]?[A-Za-z0-9._~+/-]{12,}")),
]

# A third party's mailbox at a consumer host is always personal data. Our own published
# addresses (ops@navaia.sa and the like) are marketing contact details, not a leak.
_CONSUMER_MAIL = re.compile(
    r"[A-Za-z0-9._%+-]+@(gmail|hotmail|outlook|yahoo|icloud|live|aol|proton(mail)?)\.[a-z.]{2,}",
    re.I)

# Files that must never be committed anywhere.
_FORBIDDEN_PATHS = re.compile(
    r"(prospects\.json|contacts\.json|company_size\.json|leads_enriched\.csv|"
    # .env.example is a committed template of placeholder values — every repo here allows it
    # explicitly (`!.env.example`). Flagging it made the full scan fail on a file that is
    # supposed to be there, and a check that always fires gets bypassed.
    r"_local_api_key|ONBOARDING_KEYS|\.env$|\.env\.(?!example$)[a-z]+$|discover_state\.json)")

# Sample values in .env.example and scrubbed snapshots match the secret shapes above but
# carry nothing. Flagging them would block every push, and a gate that always fires gets
# bypassed with --no-verify, which is worse than no gate.
_PLACEHOLDER_SECRET = re.compile(
    r"(replace-with|replace_me|changeme|change-me|placeholder|your[-_]|example|"
    r"REDACTED|xxxx|<[^>]+>|\.\.\.)", re.I)

# Placeholders that are obviously not real people, so fixtures stay usable.
_FIXTURE_OK = re.compile(r"(example\.|acme-demo|\.test\b|@test\.|foo@|bar@|user@|someone@)", re.I)


# Tokens that ride along in a name field but are not names. Snov returns qualifications and
# job words inside `last_name` (a real record reads "<first> <last> MBA Candidate"), and
# treating "candidate" as a protected name flags ordinary English prose. A gate that cries
# wolf gets bypassed, which would be worse than no gate at all.
_NOT_A_PERSON_TOKEN = {
    "candidate", "mba", "pmp", "cfm", "cmrp", "cscp", "leed", "iso", "osha", "iosh", "cldm",
    "engineer", "manager", "director", "officer", "chief", "executive", "senior", "junior",
    "company", "group", "limited", "holding", "trading", "contracting", "services",
    "general", "assistant", "supervisor", "consultant", "specialist", "coordinator",
}


# Common given names, transliterated and Arabic. A lone common given name is not identifying
# — there are thousands of them — and flagging it as a leak fires on ordinary prose (a
# docstring example, a transliteration guide). It is only PII when paired with the surname of
# the SAME real person, which the pair matcher below still catches. A distinctive surname on
# its own does still flag. Keeping the gate tight here is what stops it being bypassed wholesale.
_COMMON_GIVEN = {
    "abdullah", "abdallah", "abdulrahman", "abdulaziz", "abdulmajeed", "mohammed", "mohammad",
    "muhammad", "ahmed", "ahmad", "khalid", "faisal", "sultan", "nasser", "salman", "majed",
    "majeed", "turki", "fahad", "saud", "saad", "yousef", "yusuf", "ibrahim", "hamad", "hassan",
    "hussein", "sara", "noura", "nora", "fatima", "aisha", "maryam", "reem", "hana", "lina",
    "عبدالله", "عبدالرحمن", "عبدالعزيز", "عبدالمجيد", "محمد", "أحمد", "احمد", "خالد", "فيصل",
    "سلطان", "ناصر", "سلمان", "ماجد", "تركي", "فهد", "سعود", "سعد", "يوسف", "إبراهيم", "ابراهيم",
    "حمد", "حسن", "حسين", "سارة", "نورة", "فاطمة", "عائشة", "مريم", "ريم", "لينا",
}


def real_names() -> set[str]:
    """Distinctive single tokens of real people from the local (gitignored) prospect files.

    Common given names are excluded here and handled only as part of a full pair (see
    `real_name_pairs`), so a lone 'Abdullah' in prose is not treated as a leak while a
    distinctive surname still is.
    """
    names: set[str] = set()
    for fname in ("prospects.json", "contacts.json"):
        try:
            with io.open(os.path.join(ROOT, fname), encoding="utf-8") as f:
                for row in json.load(f):
                    full = (row.get("name") or "").strip()
                    for token in full.split():
                        cleaned = token.strip(".,-").strip().lower()
                        # Only distinctive tokens: a 3-letter fragment matches everything,
                        # and a common given name matches half the prose in the repo.
                        if (len(cleaned) >= 5 and cleaned not in _NOT_A_PERSON_TOKEN
                                and cleaned not in _COMMON_GIVEN
                                and not _FIXTURE_OK.search(cleaned)):
                            names.add(cleaned)
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, TypeError):
            continue
    return names


def real_name_pairs() -> list[tuple[str, str]]:
    """Full (given, surname) pairs of real people — the high-confidence identifier.

    A pair flags only when both tokens of the SAME person appear, so a common given name that
    is safe alone is still caught when it rides next to its real surname.
    """
    pairs: list[tuple[str, str]] = []
    for fname in ("prospects.json", "contacts.json"):
        try:
            with io.open(os.path.join(ROOT, fname), encoding="utf-8") as f:
                for row in json.load(f):
                    toks = [t.strip(".,-").strip().lower()
                            for t in (row.get("name") or "").split()]
                    toks = [t for t in toks
                            if len(t) >= 3 and t not in _NOT_A_PERSON_TOKEN
                            and not _FIXTURE_OK.search(t)]
                    if len(toks) >= 2:
                        pairs.append((toks[0], toks[-1]))
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, TypeError):
            continue
    return pairs


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace").stdout
    except Exception:
        return ""


def _added_lines(diff: str) -> str:
    """Only the lines a diff ADDS.

    A raw diff also carries every removed line, so the commit that DELETES a leaked secret
    trips the scanner on the secret it is removing — the fix for a leak becomes unpushable
    and the only way out is --no-verify, which disables the whole gate. Removing a secret is
    never a leak; adding one always is.
    """
    return "\n".join(l[1:] for l in diff.splitlines()
                     if l.startswith("+") and not l.startswith("+++"))


def scan_text(label: str, text: str, names: set[str], creds_only: bool = False,
              pairs: list[tuple[str, str]] | None = None) -> list[str]:
    hits = []
    for what, pattern in _SECRETS:
        for m in pattern.finditer(text):
            if _PLACEHOLDER_SECRET.search(m.group(0)):
                continue
            hits.append(f"{label}: {what} -> {m.group(0)[:28]}…")
    if creds_only:
        return hits
    for m in _CONSUMER_MAIL.finditer(text):
        if not _FIXTURE_OK.search(m.group(0)):
            hits.append(f"{label}: third-party mailbox -> {m.group(0)}")
    lowered = text.lower()
    for name in names:
        if name in lowered:
            hits.append(f"{label}: real prospect name -> {name}")
    # Full pairs catch a common given name riding next to its real surname, which the
    # distinctive-token pass above deliberately skips.
    for given, surname in (pairs or []):
        if given in lowered and surname in lowered:
            hits.append(f"{label}: real prospect name -> {given} {surname}")
    return hits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", dest="rng", default="")
    ap.add_argument("--all-tracked", action="store_true")
    # A range scan only sees the commits being pushed, so a credential committed before this
    # hook existed stays invisible forever — that is how a live OpenRouter key sat on
    # origin/main until 2026-07-20. Credentials therefore get scanned across the whole tree
    # every push; names and mailboxes stay range-scoped so the pre-existing cleanup backlog
    # does not block unrelated work.
    ap.add_argument("--credentials-only", action="store_true")
    args = ap.parse_args()

    names = real_names()
    pairs = real_name_pairs()
    hits: list[str] = []

    if args.all_tracked:
        for path in _git("ls-files").splitlines():
            if _FORBIDDEN_PATHS.search(path) and not args.credentials_only:
                hits.append(f"TRACKED FILE that must never be committed: {path}")
            try:
                with io.open(os.path.join(ROOT, path), encoding="utf-8") as f:
                    hits += scan_text(path, f.read(), names, args.credentials_only, pairs)
            except (OSError, UnicodeDecodeError):
                continue
    else:
        diff = _git("diff", "--cached") or _git("diff", "HEAD~1")
        if args.rng:
            diff = _git("diff", args.rng)
            hits += scan_text("commit message", _git("log", "--format=%B", args.rng), names, pairs=pairs)
        for path in (_git("diff", "--cached", "--name-only") or "").splitlines():
            if _FORBIDDEN_PATHS.search(path):
                hits.append(f"STAGED file that must never be committed: {path}")
        hits += scan_text("diff", _added_lines(diff), names, pairs=pairs)

    if hits:
        print("REFUSING — real data or credentials found:\n")
        for h in sorted(set(hits))[:40]:
            print("   " + h)
        print("\nThis content would become public. Replace real names and addresses with")
        print("invented ones (an @acme-demo.test address is fine), then retry.")
        sys.exit(1)

    print(f"no leaks found ({len(names)} real names checked against)")


if __name__ == "__main__":
    main()
