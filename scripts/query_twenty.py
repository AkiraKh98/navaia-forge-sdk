import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx

env_content = open('C:/Users/aabbo/navaia-forge-sdk/.env').read()
token = re.search(r'TWENTY_TOKEN=(.+)', env_content).group(1).strip()
base_url = "https://crm.navaia.sa"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

print("=== TWENTY CRM: Existing People ===")
try:
    resp = httpx.get(f"{base_url}/rest/people", headers=headers, params={"limit": 50}, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        people = data.get("data", data if isinstance(data, list) else [])
        print(f"Count: {len(people)}")
        for p in people[:30]:
            name = p.get("name", {})
            first = name.get("firstName", "") if isinstance(name, dict) else ""
            last = name.get("lastName", "") if isinstance(name, dict) else ""
            full = f"{first} {last}".strip() or p.get("name", "N/A")
            email = p.get("email", "N/A")
            phone = p.get("phone", "N/A")
            print(f"  - {full} | email={email} | phone={phone}")
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== TWENTY CRM: Existing Companies ===")
try:
    resp = httpx.get(f"{base_url}/rest/companies", headers=headers, params={"limit": 50}, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        companies = data.get("data", data if isinstance(data, list) else [])
        print(f"Count: {len(companies)}")
        for c in companies[:30]:
            name = c.get("name", "N/A")
            domain = c.get("domainName", c.get("domain", "N/A"))
            print(f"  - {name} | domain={domain}")
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
