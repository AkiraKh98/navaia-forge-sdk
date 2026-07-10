import asyncio
from sqlalchemy import text
from app.deps import async_session_factory

async def update_task_for_csv():
    async with async_session_factory() as db:
        # Get current task description
        r = await db.execute(text(
            "SELECT title, description FROM tasks WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868'"
        ))
        t = r.fetchone()
        print(f"Current title: {t[0]}")

        # Build new description: JDI, write to CSV instead of CRM
        new_description = """JDI — Execute immediately, no planning needed. Your plan was already approved.

IMPORTANT CHANGE: The Twenty CRM at crm.navaia.sa is currently DOWN. Do NOT attempt to call the CRM API. Instead, write all leads directly to a CSV file.

## Task: Find 50 real targeted leads in Riyadh across 5 verticals

### Objective
Find 50 REAL business leads in Riyadh, Saudi Arabia across 5 verticals (10 per vertical). Each lead must have a phone number. Write results to a CSV file at /app/workspace/leads.csv

### Verticals and Search Terms

**Tier 1 (30 leads total, 10 each):**

1. Contracting/Maintenance/Facilities Management
   - Search terms: "contracting company Riyadh", "maintenance company Riyadh", "facilities management Riyadh", "شركة مقاولات الرياض", "شركة صيانة الرياض"
   - CRM sector value: Contracting & Facilities

2. Finance/Installment/Debt Collection
   - Search terms: "debt collection Riyadh", "تحصيل ديون الرياض", "شركة تقسيط الرياض", "finance company Riyadh"
   - CRM sector value: Finance & Debt Collection

3. Private Clinics (dental, dermatology, cosmetic, physiotherapy)
   - Search terms: "dental clinic Riyadh", "dermatology clinic Riyadh", "cosmetic clinic Riyadh", "physiotherapy clinic Riyadh", "عيادة أسنان الرياض", "عيادة جلدية الرياض", "عيادة تجميل الرياض"
   - CRM sector value: Private Clinics

**Tier 2 (20 leads total, 10 each):**

4. Real Estate/Property Management
   - Search terms: "real estate company Riyadh", "property management Riyadh", "شركة عقارات الرياض", "إدارة أملاك الرياض"
   - CRM sector value: Real Estate

5. Training Institutes
   - Search terms: "training institute Riyadh", "معهد تدريب الرياض", "training center Riyadh"
   - CRM sector value: Training Institutes

### Data Source
Use Google Places API (Text Search). The API key is in environment variable PLACES_API.
- Endpoint: POST https://places.googleapis.com/v1/places:searchText
- Header: X-Goog-Api-Key: <PLACES_API>
- Header: X-Goog-FieldMask: places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.websiteUri,places.id,places.types,nextPageToken
- Body: {"textQuery": "<search term>", "locationBias": {"circle": {"center": {"latitude": 24.7136, "longitude": 46.6753}, "radius": 50000}}, "pageSize": 20}
- Use nextPageToken for pagination (up to 3 pages per term)

### Filtering Rules
- Keep only places where formattedAddress contains "Riyadh"
- Discard any place without internationalPhoneNumber (MUST have phone)
- Remove duplicates (same place ID or identical name)
- Do NOT invent or fabricate any data — only use real data from Google Places API

### CSV Output Format
Write to file: /app/workspace/leads.csv

CSV columns (matching Twenty CRM schema):
- company_name: Business name from Google Places
- domain_name: Website URL if available (empty string if not)
- address: formattedAddress from Google Places
- phone: internationalPhoneNumber
- sector: One of: Contracting & Facilities, Finance & Debt Collection, Private Clinics, Real Estate, Training Institutes
- vertical_tier: Tier 1 or Tier 2
- created_by: Mjeed using [Tariq SDR Agent]
- lead_source: Google-Places
- place_id: Google Places ID (for dedup tracking)

### Execution Steps
1. For each vertical, search Google Places with the search terms above
2. Filter results (Riyadh address + has phone + deduplicate)
3. Collect 10 leads per vertical (50 total)
4. Write ALL leads to /app/workspace/leads.csv as a proper CSV file with header row
5. Output a summary: total leads, count per vertical, file location

### Important
- Use ONLY real data from Google Places API
- Every lead MUST have a phone number
- Write the CSV file to /app/workspace/leads.csv
- End with [DONE] signal when complete
"""

        await db.execute(text(
            "UPDATE tasks SET status = 'PENDING', description = :desc, "
            "started_at = NULL, completed_at = NULL, error = NULL, result = NULL "
            "WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868'"
        ), {"desc": new_description})
        await db.commit()
        print("Task updated: now writes leads to CSV instead of CRM")
        print("Task set to PENDING")

asyncio.run(update_task_for_csv())
