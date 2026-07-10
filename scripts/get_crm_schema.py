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

# 1. Get full field schema for people
print("=== PEOPLE OBJECT SCHEMA ===")
try:
    resp = httpx.get(f"{base_url}/rest/objects/people", headers=headers, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2, default=str)[:5000])
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# 2. Get full field schema for companies
print("\n\n=== COMPANIES OBJECT SCHEMA ===")
try:
    resp = httpx.get(f"{base_url}/rest/objects/companies", headers=headers, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2, default=str)[:5000])
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# 3. Try the metadata/describe endpoint
print("\n\n=== DESCRIBE PEOPLE ===")
try:
    resp = httpx.get(f"{base_url}/rest/objects/people/fields", headers=headers, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2, default=str)[:5000])
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n\n=== DESCRIBE COMPANIES ===")
try:
    resp = httpx.get(f"{base_url}/rest/objects/companies/fields", headers=headers, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2, default=str)[:5000])
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# 4. Get a single person record to see ALL fields
print("\n\n=== SINGLE PERSON (all fields) ===")
try:
    resp = httpx.get(f"{base_url}/rest/people", headers=headers, params={"limit": 1}, timeout=30)
    if resp.status_code == 200:
        people = resp.json().get("data", {}).get("people", [])
        if people:
            print(json.dumps(people[0], indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")

# 5. Get a single company record to see ALL fields
print("\n\n=== SINGLE COMPANY (all fields) ===")
try:
    resp = httpx.get(f"{base_url}/rest/companies", headers=headers, params={"limit": 1}, timeout=30)
    if resp.status_code == 200:
        companies = resp.json().get("data", {}).get("companies", [])
        if companies:
            print(json.dumps(companies[0], indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")
