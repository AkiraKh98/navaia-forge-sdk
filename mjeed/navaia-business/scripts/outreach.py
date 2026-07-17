#!/usr/bin/env python3
"""OUTREACH — the script-authority pipeline. One command, scripts decide everything.

Born from the 2026-07-14 postmortem (workforce/POSTMORTEM_2026-07-14.md): every failure
that day came from putting an LLM in charge of deterministic steps. This script keeps
FULL AUTHORITY locally and uses the cloud for exactly ONE thing — the physical send by
Tariq, because the Meta/WhatsApp token lives only in the cloud env. Structural guarantees:

  - RENDERING IS LOCAL AND DETERMINISTIC (templates verbatim + lina_compose token logic).
    No cloud render → no waiting states, no clarification loops, no ~18k output-cap
    truncation, no improvised subjects. What you approve is BYTE-EXACT what is sent.
  - APPROVAL IS LOCAL AND FAST: compact per-lead summary in the terminal + the full
    render written to outreach_render.md for reading; approve all / skip by number.
  - THE CLOUD TASK IS A LITERAL EXECUTION CHECKLIST (exact per-lead payloads, exact
    API shapes, no judgment, no gate, ends [DONE]). This pattern sent 30/30 on 07-14.
  - CRM STATUS UPDATES RUN LOCALLY afterwards (direct crm.navaia.sa PATCH) — the
    in-task CRM tool is flaky per-run and is not trusted with anything.

Usage:
    .venv/Scripts/python.exe scripts/outreach.py                    # all verticals
    .venv/Scripts/python.exe scripts/outreach.py --verticals "Real Estate,Training Institutes"
    .venv/Scripts/python.exe scripts/outreach.py --dry-run          # render + review only
    .venv/Scripts/python.exe scripts/outreach.py --self-test        # fake leads, no CRM/cloud
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
from datetime import datetime

if (sys.stdout.encoding or "").lower().replace("-", "") != "utf8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx

import nav_env
import lina_compose
import pipeline_prep as prep
from navaia_forge import NavaiaForgeClient
from submit_lead_batch import ALL_VERTICALS, resolve_agent

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RENDER_FILE = os.path.join(ROOT, "outreach_render.md")
CAL = "https://cal.com/abdulmajeed-alwardi"
SIG = "عبدالمجيد الوردي"
CRM_BASE = "https://crm.navaia.sa"

# CRM sector -> lina_compose LIBRARY key
VKEY = {
    "Private Clinics": "clinics",
    "Contracting & Facilities": "contracting",
    "Finance & Debt Collection": "finance",
    "Real Estate": "realestate",
    "Training Institutes": "training",
}

# Per-vertical trigger sentence for the email {trigger_line} token — the approved,
# unattributed general-pain line (doctrine: never cite reviews; Arabic commas; no em-dash).
TRIGGER = {
    "Contracting & Facilities": "في مثل عملكم قد يتأخّر الردّ على العروض والعطاءات في أوقات الذروة، فتفوتكم فرص.",
    "Real Estate": "في مثل عملكم قد يتأخّر الردّ على الاتصالات والرسائل في أوقات الذروة، فيبرد المهتمّ.",
    "Training Institutes": "في مواسم التسجيل قد يتأخّر الردّ على الاستفسارات، فيضيع مستفسرون مهتمّون.",
    "Private Clinics": "في مثل عملكم قد تفوت مكالمات المراجعين بعد الإغلاق أو في أوقات الذروة.",
    "Finance & Debt Collection": "بين متابعة الأقساط المتأخّرة وتذكير العملاء، قد يتقادم بعض الديون.",
}

# Email {lina_pain} must be a NOUN PHRASE (it follows "تعاني من …"); the library's general
# pains are full sentences, so generals use these instead (the approved email wording).
EMAIL_PAIN = {
    "Contracting & Facilities": "تأخر متابعة العطاءات والعروض",
    "Real Estate": "تأخّر الردّ على المهتمّين والمتابعة",
    "Training Institutes": "تأخّر الردّ على المستفسرين في موسم التسجيل",
    "Private Clinics": "المكالمات الفائتة والإلغاءات دون تذكير",
    "Finance & Debt Collection": "تقادم الديون بسبب تأخّر المتابعة",
}

# Company-name suffixes that are trimmed to get the short form used in {{1}}.
_TAIL = re.compile(
    r"\s*(للمقاولات( العامة)?|للخدمات العقارية|العقارية|لإدارة (المرافق|الأملاك|العقارات)|"
    r"للتجارة والمقاولات( العامة)?( المحدودة)?|للتدريب|العالي للتدريب|المحدودة|"
    r"Training (Institute|Centre|Center|Academy)|Institute|L\.?L\.?C\.?|Co\.?|Company|Group)\s*$",
    re.I)


def short_name(company: str) -> str:
    s = company.strip()
    for _ in range(3):  # peel up to 3 trailing descriptors
        s2 = _TAIL.sub("", s).strip(" -–—|،,")
        if s2 == s or len(s2) < 3:
            break
        s = s2
    return s or company.strip()


def _email_subject_and_body(vertical: str) -> tuple[str, str]:
    """Split the verbatim email template into (primary subject, body with tokens)."""
    tpl = prep.email_touch1_templates()[vertical]
    lines = tpl.splitlines()
    subject = ""
    body_start = 0
    for i, line in enumerate(lines):
        m = re.match(r"\*\*الموضوع:\*\*\s*(.+)", line.strip())
        if m:
            subject = re.split(r"\s*\*\(alt", m.group(1))[0].strip().strip("`*")
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:]).strip()
    return subject, body


def render_lead(lead: dict, use_llm: bool, or_key: str | None) -> dict:
    """Deterministic render for one lead: WA vars + preview, email subject/body."""
    vertical = lead["sector"]
    vkey = VKEY[vertical]
    company = lead["company"]
    honorific = (f"الأستاذ {lead['contact_name']}" if lead.get("contact_name")
                 else f"القائمون على {short_name(company)} الكرام")
    pain_line = lead.get("pain_line") or lead.get("pain_hints") or ""
    block, meta = lina_compose.compose_block(vkey, pain_line, use_llm=use_llm, key=or_key)

    wa = prep.wa_templates()[vertical]
    wa_vars = [honorific, block, company, CAL, SIG]
    preview = wa["body"]
    for i, v in enumerate(wa_vars, 1):
        preview = preview.replace("{{%d}}" % i, v)

    email_subject = email_body = None
    if lead.get("email"):
        email_subject, body = _email_subject_and_body(vertical)
        # noun-phrase pain: the matched category's pain fits "تعاني من …"; generals don't.
        pain_phrase = (meta.get("pain") if meta.get("source") not in (None, "general")
                       else EMAIL_PAIN[vertical])
        fills = {
            "{honorific+name}": honorific,
            "{inbound_context}": "",
            "{trigger_line}": TRIGGER[vertical],
            "{lina_pain}": pain_phrase,
            "{اسم الشركة}": company, "{اسم العيادة}": company, "{اسم المعهد}": company,
        }
        for k, v in fills.items():
            body = body.replace(k, v)
        # Format the body text to HTML with proper RTL directionality and styling
        formatted_body = body.strip().replace("\n", "<br>")
        email_body = (
            f'<div dir="rtl" style="text-align: right; direction: rtl; font-family: Arial, sans-serif; font-size: 11pt; line-height: 1.6;">'
            f'{formatted_body}'
            f'</div>'
        )

    phone = re.sub(r"\D", "", lead.get("phone") or "")
    if phone.startswith("0"):
        phone = phone[1:]
    if phone and not phone.startswith("966"):
        phone = "966" + phone

    return {**lead, "wa_template": wa["name"], "wa_vars": wa_vars, "wa_preview": preview,
            "email_subject": email_subject, "email_body": email_body,
            "phone_intl": phone, "pain_source": meta.get("source", "general")}


def write_render_file(rendered: list[dict]) -> None:
    parts = [f"# Outreach render — {datetime.now():%Y-%m-%d %H:%M} (approve in the terminal)\n"]
    for i, r in enumerate(rendered, 1):
        parts.append(f"\n## {i}. {r['company']}  ({r['sector']})")
        parts.append(f"person_id `{r['person_id']}` | phone `{r['phone_intl'] or '-'}` | "
                     f"email `{r['email'] or '-'}` | pain: {r['pain_source']}")
        parts.append(f"\n**WhatsApp** (`{r['wa_template']}`):\n\n```\n{r['wa_preview']}\n```")
        if r["email_body"]:
            parts.append(f"\n**Email** — subject: {r['email_subject']}\n\n```\n{r['email_body']}\n```")
    open(RENDER_FILE, "w", encoding="utf-8").write("\n".join(parts))


def review(rendered: list[dict]) -> list[dict] | None:
    """Compact terminal review. Returns the approved subset, or None if aborted."""
    print(f"\nFull render written to {os.path.basename(RENDER_FILE)} — open it to read every message.")
    print(f"\n{'#':>2} {'vertical':24} {'company':38} {'WA':>2} {'email':28} pain")
    for i, r in enumerate(rendered, 1):
        print(f"{i:>2} {r['sector'][:24]:24} {r['company'][:38]:38} "
              f"{'✓' if r['phone_intl'] else '✗':>2} {(r['email'] or '-')[:28]:28} {r['pain_source']}")
    raw = input("\nApprove: Enter = ALL | numbers to SKIP (e.g. 2,5) | q = abort: ").strip().lower()
    if raw in ("q", "quit", "n", "no"):
        return None
    skip = {int(x) for x in re.findall(r"\d+", raw)}
    return [r for i, r in enumerate(rendered, 1) if i not in skip]


def build_send_task(vertical: str, leads: list[dict]) -> str:
    wa_name = leads[0]["wa_template"]
    lead_blocks = []
    for r in leads:
        item = {
            "person_id": r["person_id"], "company": r["company"], "to": r["phone_intl"],
            "wa_template": r["wa_template"], "wa_variables": r["wa_vars"],
        }
        if r["email_body"]:
            item["email"] = {"to": r["email"], "subject": r["email_subject"],
                             "body": r["email_body"]}
        lead_blocks.append(item)
    payload = json.dumps(lead_blocks, ensure_ascii=False, indent=1)
    return f"""## EXECUTE SENDS — {vertical} (operator ALREADY approved locally; no gate, no questions)

This is a literal execution checklist. Every decision is already made. Do not rephrase,
re-render, or alter ANY text. Never ask anything: if a step fails, record the exact error
for that lead and continue. End your final output with the marker [DONE] on its own line.

### 1. WhatsApp — for EVERY lead in the JSON below with a non-empty "to"
Use the direct Graph API (the proven primary — Baian's tool 404s on its cached id):
read env NF_BAIAN_WABA_ID + NF_BAIAN_META_TOKEN, discover the phone-number id ONCE via
GET https://graph.facebook.com/v24.0/{{WABA_ID}}/phone_numbers, then for each lead POST
https://graph.facebook.com/v24.0/{{PHONE_NUMBER_ID}}/messages with EXACTLY:
{{"messaging_product":"whatsapp","to":"<to>","type":"template","template":{{"name":"{wa_name}",
"language":{{"code":"ar"}},"components":[{{"type":"body","parameters":[
{{"type":"text","text":"<wa_variables[0]>"}},{{"type":"text","text":"<wa_variables[1]>"}},
{{"type":"text","text":"<wa_variables[2]>"}},{{"type":"text","text":"<wa_variables[3]>"}},
{{"type":"text","text":"<wa_variables[4]>"}}]}}]}}}}
(substitute the five wa_variables strings verbatim, in order).

### 2. Email — ONLY for leads whose JSON block has an "email" object
Send via the Snov.io tool through the connected Zoho mailbox (ops@navaia.sa), subject and
body EXACTLY as given. The body carries no signature (Snov auto-appends it). Max 20/day.

### 3. DO NOT touch the CRM. Status updates are handled outside this task.

### 4. REPORT — final output, machine-readable, one line per lead:
RESULT | <person_id> | wa=<sent|failed:reason> | email=<sent|failed:reason|none>
Then the totals, then [DONE].

## LEADS (the complete, final list — nothing else is in scope)
```json
{payload}
```
"""


def apply_crm_updates(report: str) -> tuple[int, int]:
    """Parse RESULT lines and PATCH leadStatus locally. Returns (ok, failed)."""
    hdr = {"Authorization": f"Bearer {nav_env.env('TWENTY_TOKEN')}",
           "Content-Type": "application/json"}
    ok = fail = 0
    for pid, wa, em in re.findall(
            r"RESULT\s*\|\s*([0-9a-f-]{36})\s*\|\s*wa=(\S+)\s*\|\s*email=(\S+)", report):
        status = ("Emailed" if em.startswith("sent")
                  else "WhatsApped" if wa.startswith("sent") else None)
        if not status:
            continue
        r = httpx.patch(f"{CRM_BASE}/rest/people/{pid}", headers=hdr,
                        json={"leadStatus": status}, timeout=30)
        ok += r.status_code < 300
        fail += r.status_code >= 300
        print(f"  {'OK ' if r.status_code < 300 else 'ERR'} CRM {pid[:8]} -> {status}")
    return ok, fail


def preflight_key_check() -> bool:
    """Fault-1 guard: warn BEFORE submitting send tasks if the cloud's LLM key is near its
    rolling cap or its account is nearly drained (a dead key = silent pending stalls)."""
    key = nav_env.env("MY_OPENROUTER_KEY")
    if not key:
        print("(!) MY_OPENROUTER_KEY not in .env — cannot pre-check the cloud key balance.")
        return True
    try:
        hdr = {"Authorization": f"Bearer {key}"}
        d = httpx.get("https://openrouter.ai/api/v1/auth/key", headers=hdr, timeout=15).json()["data"]
        cr = httpx.get("https://openrouter.ai/api/v1/credits", headers=hdr, timeout=15).json()["data"]
        remaining = d.get("limit_remaining")
        account_left = (cr.get("total_credits") or 0) - (cr.get("total_usage") or 0)
        print(f"Key pre-flight: window remaining="
              f"{'∞' if remaining is None else f'${remaining:.2f}'} | account left ${account_left:.2f}")
        if (remaining is not None and remaining < 0.5) or account_left < 1.0:
            print("(!) The key is nearly exhausted — cloud tasks will stall SILENTLY in "
                  "pending (see POSTMORTEM_2026-07-14 Fault 1). Top up before sending.")
            return input("Submit send tasks anyway? (yes/N) ").strip().lower() == "yes"
    except Exception as e:
        print(f"(key pre-flight skipped: {e})")
    return True


def _fake_leads() -> list[dict]:
    return [
        {"person_id": "00000000-0000-0000-0000-000000000001",
         "company": "شركة الاختبار للمقاولات العامة", "contact_name": "",
         "sector": "Contracting & Facilities", "email": "test@example.com",
         "phone": "112345678", "website": ""},
        {"person_id": "00000000-0000-0000-0000-000000000002",
         "company": "معهد التجربة العالي للتدريب", "contact_name": "",
         "sector": "Training Institutes", "email": "", "phone": "0501234567", "website": ""},
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verticals", default=",".join(ALL_VERTICALS))
    ap.add_argument("--dry-run", action="store_true", help="render + review, send nothing")
    ap.add_argument("--self-test", action="store_true", help="render fake leads, no CRM/cloud")
    ap.add_argument("--llm-pain", action="store_true",
                    help="allow the cheap LLM step for novel pain lines (MY_OPENROUTER_KEY)")
    args = ap.parse_args()
    verticals = [v.strip() for v in args.verticals.split(",") if v.strip()]
    bad = [v for v in verticals if v not in ALL_VERTICALS]
    if bad:
        raise SystemExit(f"Unknown vertical(s) {bad}; valid: {ALL_VERTICALS}")
    or_key = nav_env.env("MY_OPENROUTER_KEY") if args.llm_pain else None

    if args.self_test:
        leads = _fake_leads()
    else:
        print("CRM prep (local, deterministic)…")
        prep.normalize_crm_people()
        prep.enrich_crm_not_contacted()
        leads = prep.not_contacted_leads(verticals)
    if not leads:
        print("No Not Contacted leads in those verticals — nothing to do.")
        return

    rendered = [render_lead(l, args.llm_pain, or_key) for l in leads]
    write_render_file(rendered)
    approved = review(rendered)
    if approved is None or not approved:
        print("Aborted — nothing sent.")
        return
    if args.self_test or args.dry_run:
        print(f"\n{'SELF-TEST' if args.self_test else 'DRY RUN'} — {len(approved)} approved, "
              f"no tasks created. Render: {RENDER_FILE}")
        return

    if not preflight_key_check():
        print("Aborted — nothing sent.")
        return

    cloud = NavaiaForgeClient(api_key=nav_env.env("BUSINESS_NF"), base_url=nav_env.base_url())
    tariq = resolve_agent(cloud, "Tariq")
    by_vertical: dict[str, list[dict]] = {}
    for r in approved:
        by_vertical.setdefault(r["sector"], []).append(r)

    watching = {}
    for vertical, group in by_vertical.items():
        t = cloud.tasks.create(
            nav_env.CLOUD_WORKFORCE_ID,
            f"SEND (script-approved) Touch-1 — {vertical} ({len(group)} leads)",
            description=build_send_task(vertical, group), agent_id=tariq, priority="high",
            metadata={"kind": "script_authority_send", "vertical": vertical,
                      "leads": len(group)},
        )
        watching[vertical] = t.id
        print(f"✓ {vertical}: send task {t.id} ({len(group)} leads)")

    print("\nWatching sends (Ctrl+C safe — tasks keep running in the cloud)…")
    deadline = time.time() + 1800
    while watching and time.time() < deadline:
        time.sleep(20)
        for vertical, tid in list(watching.items()):
            try:
                t = cloud.tasks.get(tid)
            except Exception as e:
                print(f"  (poll error {vertical}: {e} — retrying)")
                continue
            s = str(t.status).lower()
            if s in ("done", "failed", "cancelled", "waiting_blocked", "waiting_question"):
                print(f"\n===== {vertical}: {s.upper()} =====")
                report = t.result or ""
                print(report[:2500])
                if s == "done":
                    ok, fail = apply_crm_updates(report)
                    print(f"CRM updates: {ok} ok, {fail} failed")
                del watching[vertical]
    if watching:
        print(f"\nStill running after 30 min: {watching} — rerun later or check the dashboard.")


if __name__ == "__main__":
    main()
