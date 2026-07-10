import csv, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('C:/Users/aabbo/navaia-forge-sdk/leads_clean.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total clean leads: {len(rows)}\n")

# Email status distribution
statuses = Counter(r.get('email_status', '') for r in rows)
print("=== EMAIL STATUS DISTRIBUTION ===")
for status, count in statuses.most_common():
    print(f"  {status or '(empty)'}: {count}")

# Cross-tab: email present vs status
has_email = sum(1 for r in rows if r.get('email', '').strip())
no_email = len(rows) - has_email
print(f"\n=== EMAIL PRESENCE ===")
print(f"  Has email:    {has_email}")
print(f"  No email:     {no_email}")

# Has phone
has_phone = sum(1 for r in rows if r.get('phone', '').strip())
print(f"\n=== PHONE PRESENCE ===")
print(f"  Has phone:    {has_phone}")
print(f"  No phone:     {len(rows) - has_phone}")

# Sector distribution
sectors = Counter(r.get('sector', '') for r in rows)
print(f"\n=== SECTOR DISTRIBUTION ===")
for sector, count in sectors.most_common():
    print(f"  {sector or '(empty)'}: {count}")

# Tier distribution
tiers = Counter(r.get('vertical_tier', '') for r in rows)
print(f"\n=== TIER DISTRIBUTION ===")
for tier, count in tiers.most_common():
    print(f"  {tier or '(empty)'}: {count}")

# Show each lead's email situation
print(f"\n=== LEAD-BY-LEAD EMAIL STATUS ===")
for i, r in enumerate(rows, 1):
    name = r.get('company_name', '')[:40]
    email = r.get('email', '').strip()
    status = r.get('email_status', '').strip()
    phone = r.get('phone', '').strip()
    tier = r.get('vertical_tier', '').strip()
    email_display = email if email else '(none)'
    phone_display = 'Y' if phone else 'N'
    print(f"  {i:2d}. {name:<42} | email={email_display:<30} | status={status:<20} | phone={phone_display} | {tier}")
