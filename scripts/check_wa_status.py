"""Check Baian WhatsApp template approval status via REST API (bypasses SDK hanging issue)."""
import re, os, json, urllib.request, ssl, time, sys

sys.stdout = __import__("io").TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
m = re.search(r"^BUSINESS_NF=(.+)$", open(ENV_PATH).read(), re.M)
key = m.group(1).strip()

BASE = "https://fareegi.navaia.sa"
WF = "131bb52f-e5eb-44ad-8134-03dc6908b485"
TARIQ = "6ba49326-4ec0-4b3b-8651-9526ec96894e"

desc = (
    "READ-ONLY status check. Do NOT send any message, and do NOT create, edit, or "
    "delete anything. Introspect Baian's tools (do not hardcode) and LIST the WhatsApp "
    "templates. Report a table of every template: name, template id, category, language, "
    "and Meta approval status (PENDING / APPROVED / REJECTED)."
)

body = json.dumps({
    "workforce_id": WF,
    "title": "READ-ONLY: Baian template approval status",
    "description": desc,
    "agent_id": TARIQ,
    "priority": "standard",
    "metadata": {"readonly": True},
}).encode()

req = urllib.request.Request(BASE + "/api/v1/tasks", data=body, headers={
    "x-api-key": key, "Content-Type": "application/json",
})
resp = urllib.request.urlopen(req, timeout=30, context=ctx)
t = json.loads(resp.read())
tid = t["id"]
print(f"TASK CREATED: {tid} | status: {t['status']}")

deadline = time.time() + 200
last = None
while time.time() < deadline:
    req2 = urllib.request.Request(BASE + f"/api/v1/tasks/{tid}", headers={"x-api-key": key})
    resp2 = urllib.request.urlopen(req2, timeout=20, context=ctx)
    t = json.loads(resp2.read())
    if t["status"] != last:
        print(f"  status -> {t['status']}")
        last = t["status"]
    s = str(t["status"]).lower()
    if "waiting_plan" in s:
        try:
            req3 = urllib.request.Request(
                BASE + f"/api/v1/tasks/{tid}/approve",
                method="POST",
                headers={"x-api-key": key, "Content-Type": "application/json"},
                data=b"{}",
            )
            urllib.request.urlopen(req3, timeout=20, context=ctx)
            print("  approved plan")
        except Exception as e:
            print(f"  approve error: {e}")
    elif s in ("done", "failed", "cancelled", "waiting_blocked", "waiting_question"):
        break
    time.sleep(6)

req4 = urllib.request.Request(BASE + f"/api/v1/tasks/{tid}", headers={"x-api-key": key})
resp4 = urllib.request.urlopen(req4, timeout=20, context=ctx)
t = json.loads(resp4.read())
print(f"\n=== FINAL: {t['status']} ===")
print((t.get("result") or "")[:5000])
