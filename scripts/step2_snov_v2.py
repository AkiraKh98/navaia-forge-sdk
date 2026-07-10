#!/usr/bin/env python3
"""
Snov.io email enrichment — simplified approach:
1. Use free get-domain-emails-count to check which domains have emails
2. For domains with emails, use v2 domain-search to fetch them
3. Write results to CSV
"""

import csv
import json
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
SNOV_API = "https://api.snov.io"

INPUT_CSV = "/app/workspace/leads_clean.csv"
OUTPUT_CSV = "/app/workspace/leads_verified.csv"
REPORT_FILE = "/app/workspace/verification_report.md"

SNOV_DELAY = 2.0

_snov_token = None
_snov_token_time = 0


def get_token():
    global _snov_token, _snov_token_time
    if _snov_token and (time.time() - _snov_token_time) < 3000:
        return _snov_token
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SNOV_CLIENT_ID,
        "client_secret": SNOV_CLIENT_SECRET,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{SNOV_API}/v1/oauth/access_token",
        data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        _snov_token = data["access_token"]
        _snov_token_time = time.time()
        return _snov_token


def snov_request(path, params=None, method="POST"):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        data = None
    req = urllib.request.Request(f"{SNOV_API}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8", errors="replace")[:200]}
    except Exception as e:
        return {"error": str(e)}


def main():
    # Get token
    token = get_token()
    print(f"Snov.io token acquired")

    # Read CSV
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    print(f"Loaded {len(leads)} leads")
    print(f"{'='*60}")

    stats = {
        "total": len(leads),
        "domains_checked": 0,
        "domains_with_emails": 0,
        "domains_no_emails": 0,
        "no_domain": 0,
        "emails_found": 0,
    }

    for i, lead in enumerate(leads):
        company = lead.get("company_name", "")[:50]
        domain = lead.get("domain_name", "")

        if not domain:
            lead["email"] = ""
            lead["email_status"] = "no_domain"
            stats["no_domain"] += 1
            print(f"[{i+1}/{len(leads)}] {company} -> no domain")
            continue

        stats["domains_checked"] += 1
        print(f"[{i+1}/{len(leads)}] {company} | {domain}")

        # Free API: check email count
        time.sleep(SNOV_DELAY)
        result = snov_request("/v1/get-domain-emails-count", {"domain": domain})

        if "error" in result:
            lead["email"] = ""
            lead["email_status"] = "api_error"
            print(f"  API error: {result.get('error')}")
            continue

        count = result.get("result", 0)
        webmail = result.get("webmail", False)
        print(f"  Snov DB: {count} emails (webmail={webmail})")

        if count == 0 or webmail:
            lead["email"] = ""
            lead["email_status"] = "no_emails_in_snov"
            stats["domains_no_emails"] += 1
            continue

        stats["domains_with_emails"] += 1

        # V2 API: search domain emails (async)
        time.sleep(SNOV_DELAY)
        start_result = snov_request("/v2/domain-search/domain-emails/start", {"domain": domain})
        task_hash = start_result.get("meta", {}).get("task_hash", "") if isinstance(start_result, dict) else ""

        if not task_hash:
            lead["email"] = ""
            lead["email_status"] = "search_failed"
            print(f"  Search failed to start: {start_result}")
            continue

        # Poll for results (max 3 attempts)
        emails = []
        for attempt in range(3):
            time.sleep(SNOV_DELAY + 2)
            result_data = snov_request(f"/v2/domain-search/domain-emails/result/{task_hash}", method="GET")
            if isinstance(result_data, dict) and "data" in result_data:
                emails = [item["email"] for item in result_data["data"] if "email" in item]
                status = result_data.get("status", "")
                if status == "completed":
                    break
                print(f"  Status: {status}, retrying...")

        # Also try generic contacts
        time.sleep(SNOV_DELAY)
        gen_start = snov_request("/v2/domain-search/generic-contacts/start", {"domain": domain})
        gen_hash = gen_start.get("meta", {}).get("task_hash", "") if isinstance(gen_start, dict) else ""

        gen_emails = []
        if gen_hash:
            for attempt in range(2):
                time.sleep(SNOV_DELAY + 2)
                gen_data = snov_request(f"/v2/domain-search/generic-contacts/result/{gen_hash}", method="GET")
                if isinstance(gen_data, dict) and "data" in gen_data:
                    gen_emails = [item["email"] for item in gen_data["data"] if "email" in item]
                    if gen_data.get("status") == "completed":
                        break

        all_emails = list(set(emails + gen_emails))
        print(f"  Found: {len(all_emails)} emails total")

        if not all_emails:
            lead["email"] = ""
            lead["email_status"] = "no_emails_found"
            continue

        # Pick best email
        best = ""
        for pref in ["info", "contact", "sales", "admin", "office", "hello", "mail", "general"]:
            for e in all_emails:
                if e.lower().startswith(pref + "@"):
                    best = e
                    break
            if best:
                break
        if not best:
            best = all_emails[0]

        lead["email"] = best
        lead["email_status"] = "found_unverified"
        stats["emails_found"] += 1
        print(f"  Selected: {best}")

    # Write CSV
    fieldnames = ["company_name", "domain_name", "address", "phone",
                  "email", "email_status", "sector", "vertical_tier",
                  "created_by", "lead_source", "place_id"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    print(f"\n{'='*60}")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"{'='*60}")
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
    report.append(f"| Domains checked | {stats['domains_checked']} |")
    report.append(f"| Domains with emails in Snov DB | {stats['domains_with_emails']} |")
    report.append(f"| Domains with no emails | {stats['domains_no_emails']} |")
    report.append(f"| Leads with no domain | {stats['no_domain']} |")
    report.append(f"| Emails found | {stats['emails_found']} |")

    report.append(f"\n## CRM Dedup Status\n")
    report.append(f"CRM (crm.navaia.sa) is currently DOWN. Dedup check deferred.")

    report.append(f"\n## Verification Process\n")
    report.append(f"1. **Data source**: Google Places API (Text Search) — Riyadh, 50km radius")
    report.append(f"2. **Phone validation**: Regex for Saudi +966 format — all 50 passed")
    report.append(f"3. **Address validation**: Must contain 'Riyadh' — all 50 passed")
    report.append(f"4. **Domain extraction**: Parsed from website URL, cleaned")
    report.append(f"5. **Email count check**: Snov.io v1 `get-domain-emails-count` (free)")
    report.append(f"6. **Email discovery**: Snov.io v2 `domain-search/domain-emails` + `generic-contacts`")
    report.append(f"7. **Email selection**: info@ > contact@ > sales@ > admin@ > first available")
    report.append(f"8. **Email status**: `found_unverified` = found in Snov DB; `no_emails_in_snov` = not in DB; `no_domain` = no website")

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
