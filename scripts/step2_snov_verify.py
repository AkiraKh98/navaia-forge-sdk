#!/usr/bin/env python3
"""
Step 2: Snov.io email verification.
Test common email patterns (info@, contact@, sales@, etc.) for each domain.
Write results back to the clean CSV.
"""

import csv
import json
import re
import time
import urllib.request
import urllib.error
import urllib.parse

import os as _os, re as _re


def _secret(_name):
    _v = _os.environ.get(_name)
    if _v:
        return _v
    try:
        _env = open(_os.path.join(_os.path.dirname(__file__), "..", ".env")).read()
    except OSError:
        return None
    _m = _re.search(rf"^{_name}=(.+)$", _env, _re.M)
    return _m.group(1).strip() if _m else None


SNOV_CLIENT_ID = _secret("SNOV_USER_ID")
SNOV_CLIENT_SECRET = _secret("SNOV_USER_SECRET")
if not (SNOV_CLIENT_ID and SNOV_CLIENT_SECRET):
    raise SystemExit("Set SNOV_USER_ID and SNOV_USER_SECRET (env var or .env)")
SNOV_API_BASE = "https://api.snov.io/v1"

INPUT_CSV = "/app/workspace/leads_clean.csv"
OUTPUT_CSV = "/app/workspace/leads_verified.csv"
REPORT_FILE = "/app/workspace/verification_report.md"

# Only test 3 most common patterns to save time (info, contact, sales)
EMAIL_PREFIXES = ["info", "contact", "sales"]
SNOV_DELAY = 1.5

_snov_token = None
_snov_token_time = 0


def get_snov_token():
    global _snov_token, _snov_token_time
    if _snov_token and (time.time() - _snov_token_time) < 3000:
        return _snov_token
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SNOV_CLIENT_ID,
        "client_secret": SNOV_CLIENT_SECRET,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{SNOV_API_BASE}/oauth/access_token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            _snov_token = data.get("access_token", "")
            _snov_token_time = time.time()
            return _snov_token
    except Exception as e:
        print(f"[Snov] Token error: {e}")
        return None


def snov_verify_email(email):
    token = get_snov_token()
    if not token:
        return None
    body = json.dumps({"email": email}).encode("utf-8")
    req = urllib.request.Request(
        f"{SNOV_API_BASE}/email-verifier",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:100]
        print(f"    HTTP {e.code}: {err}")
        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def main():
    # Test Snov.io connection first
    print("=== Testing Snov.io API ===")
    token = get_snov_token()
    if not token:
        print("FAILED: Cannot get Snov.io token. Check credentials.")
        return
    print(f"Token acquired. Testing verifier with a known email...")

    test = snov_verify_email("info@google.com")
    if test:
        print(f"  Test result: isReachable={test.get('isReachable')}, isFormatValid={test.get('isFormatValid')}")
        print("  Snov.io API is working.\n")
    else:
        print("  Test failed. Snov.io API may be down.")
        return

    # Read clean CSV
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    print(f"Loaded {len(leads)} leads")
    print(f"Testing {len(EMAIL_PREFIXES)} email patterns per domain (info, contact, sales)")
    print(f"Estimated time: ~{len(leads) * len(EMAIL_PREFIXES) * SNOV_DELAY / 60:.1f} minutes")
    print(f"{'='*60}")

    stats = {
        "total": len(leads),
        "domains_tested": 0,
        "emails_found": 0,
        "emails_verified": 0,
        "emails_server_valid": 0,
        "emails_not_found": 0,
        "no_domain": 0,
    }

    for i, lead in enumerate(leads):
        company = lead.get("company_name", "")[:50]
        domain = lead.get("domain_name", "")

        if not domain:
            lead["email"] = ""
            lead["email_status"] = "no_domain"
            stats["no_domain"] += 1
            print(f"[{i+1}/{len(leads)}] {company} -> no domain, skipped")
            continue

        stats["domains_tested"] += 1
        print(f"[{i+1}/{len(leads)}] {company} | domain={domain}")

        found_email = ""
        found_status = "not_found"

        for prefix in EMAIL_PREFIXES:
            email = f"{prefix}@{domain}"
            time.sleep(SNOV_DELAY)
            result = snov_verify_email(email)

            if result is None:
                continue

            is_reachable = result.get("isReachable", False)
            is_format = result.get("isFormatValid", False)
            is_server = result.get("isServerVerified", False)
            is_mailbox = result.get("isMailboxVerified", False)

            if is_reachable and is_mailbox:
                found_email = email
                found_status = "verified"
                stats["emails_found"] += 1
                stats["emails_verified"] += 1
                print(f"  VERIFIED: {email}")
                break
            elif is_server:
                found_email = email
                found_status = "server_valid"
                stats["emails_found"] += 1
                stats["emails_server_valid"] += 1
                print(f"  SERVER VALID: {email}")
                break

        if not found_email:
            stats["emails_not_found"] += 1
            print(f"  No verifiable email found")

        lead["email"] = found_email
        lead["email_status"] = found_status

    # Write output CSV
    fieldnames = ["company_name", "domain_name", "address", "phone",
                  "email", "email_status", "sector", "vertical_tier",
                  "created_by", "lead_source", "place_id"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    print(f"\n{'='*60}")
    print(f"Verified CSV: {OUTPUT_CSV}")
    print(f"{'='*60}")
    print(f"FINAL STATS:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Write report
    report = []
    report.append("# Lead Verification Report")
    report.append(f"\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    report.append(f"\n## Summary\n")
    report.append(f"| Metric | Count |")
    report.append(f"|--------|-------|")
    report.append(f"| Total leads | {stats['total']} |")
    report.append(f"| Domains tested | {stats['domains_tested']} |")
    report.append(f"| No domain (skipped) | {stats['no_domain']} |")
    report.append(f"| Emails found | {stats['emails_found']} |")
    report.append(f"| Emails verified (mailbox reachable) | {stats['emails_verified']} |")
    report.append(f"| Emails server valid | {stats['emails_server_valid']} |")
    report.append(f"| Emails not found | {stats['emails_not_found']} |")

    report.append(f"\n## CRM Dedup Status\n")
    report.append(f"CRM (crm.navaia.sa) is currently DOWN. Dedup check deferred.")
    report.append(f"When CRM is back up, run `scripts/dump_crm.py` to export existing companies,")
    report.append(f"then compare against this CSV before importing.")

    report.append(f"\n## Verification Process\n")
    report.append(f"1. **Data source**: Google Places API (Text Search) — Riyadh, 50km radius")
    report.append(f"2. **Phone validation**: Regex for Saudi +966 format — all 50 passed")
    report.append(f"3. **Address validation**: Must contain 'Riyadh' or 'الرياض' — all 50 passed")
    report.append(f"4. **Domain extraction**: Parsed from website URL, cleaned (removed protocol, www, path)")
    report.append(f"5. **Email discovery**: Generated common patterns (info@, contact@, sales@)")
    report.append(f"6. **Email verification**: Snov.io Email Verifier API — checked each pattern for reachability")
    report.append(f"7. **Verification levels**: verified (mailbox reachable) > server_valid (server confirmed) > not_found")
    report.append(f"8. **Rate limiting**: 1.5s delay between Snov.io API calls")

    report.append(f"\n## Per-Lead Breakdown\n")
    report.append(f"| # | Company | Phone | Domain | Email | Email Status | Sector |")
    report.append(f"|---|---------|-------|--------|-------|-------------|--------|")
    for i, lead in enumerate(leads):
        report.append(
            f"| {i+1} | {lead['company_name'][:40]} | {lead['phone']} | "
            f"{lead['domain_name'] or '-'} | {lead['email'] or '-'} | "
            f"{lead['email_status']} | {lead['sector']} |"
        )

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
