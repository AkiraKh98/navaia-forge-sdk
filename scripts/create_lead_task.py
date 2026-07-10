import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from navaia_forge import NavaiaForgeClient

local_key = open('C:/Users/aabbo/navaia-forge-sdk/_local_api_key.txt').read().strip()
client = NavaiaForgeClient(api_key=local_key, base_url='http://localhost:8001')

wf_id = '8515d24a-6195-4a73-9cd3-37eb02f08693'

# Tariq (SDR) agent ID
tariq_id = '189c47b2-12ab-444d-8eb4-89e2003dc4c9'

# Read API keys from .env
env_content = open('C:/Users/aabbo/navaia-forge-sdk/.env').read()
places_key = re.search(r'PLACES_API=(.+)', env_content).group(1).strip()
twenty_token = re.search(r'TWENTY_TOKEN=(.+)', env_content).group(1).strip()

task_title = "Find 50 real targeted leads in Riyadh across 5 verticals and add to Twenty CRM"

task_description = """## OBJECTIVE
Find 50 REAL business leads in Riyadh region across 5 target verticals and add them to Twenty CRM. This is LEADS FINDING ONLY — do NOT send any emails or messages.

## TARGET VERTICALS (from Navaia co-founder strategy)

### Tier 1 (priority — find 10 leads each = 30 total):

1. **Contracting, Maintenance & Facilities Management** (المقاولات والصيانة وإدارة المرافق)
   - Search terms: "contracting company Riyadh", "maintenance company Riyadh", "facilities management Riyadh", "شركة مقاولات الرياض", "شركة صيانة الرياض", "إدارة مرافق الرياض"
   - Sector value: "Contracting & Facilities"

2. **Finance, Installment & Debt Collection** (التمويل والتقسيط ومكاتب التحصيل)
   - Search terms: "debt collection Riyadh", "تحصيل ديون الرياض", "شركة تقسيط الرياض", "finance company Riyadh"
   - Sector value: "Finance & Debt Collection"

3. **Private Specialty Clinics** (العيادات الخاصة) — dental, dermatology, cosmetic, physiotherapy ONLY. NOT general hospitals.
   - Search terms: "dental clinic Riyadh", "dermatology clinic Riyadh", "cosmetic clinic Riyadh", "physiotherapy clinic Riyadh", "عيادة أسنان الرياض", "عيادة جلدية الرياض", "عيادة تجميل الرياض", "عيادة علاج طبيعي الرياض"
   - Sector value: "Private Clinics"

### Tier 2 (find 10 leads each = 20 total):

4. **Real Estate & Property Management** (العقار وإدارة الأملاك)
   - Search terms: "real estate company Riyadh", "property management Riyadh", "شركة عقارات الرياض", "إدارة أملاك الرياض"
   - Sector value: "Real Estate"

5. **Training Institutes** (معاهد التدريب)
   - Search terms: "training institute Riyadh", "معهد تدريب الرياض", "training center Riyadh"
   - Sector value: "Training Institutes"

## DATA SOURCE — Google Places API (PRIMARY)

Use the Google Places API Text Search (New) endpoint:
- URL: `https://places.googleapis.com/v1/places:searchText`
- Method: POST
- Headers:
  - `Content-Type: application/json`
  - `X-Goog-Api-Key: {PLACES_API_KEY}`
  - `X-Goog-FieldMask: places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.websiteUri,places.id,places.types,nextPageToken`
- API Key: `{places_key}`
- Body format:
```json
{{
  "textQuery": "<search term>",
  "locationBias": {{
    "circle": {{
      "center": {{ "latitude": 24.7136, "longitude": 46.6753 }},
      "radius": 50000
    }}
  }},
  "pageSize": 20,
  "pageToken": "<nextPageToken from previous response if available>"
}}
```
- Response: `{{ "places": [...], "nextPageToken": "..." }}`
- Use `nextPageToken` to get more results (up to 60 per search term).
- Run multiple search terms per vertical to get enough leads.

## DATA SOURCE — Overpass/OpenStreetMap (BACKUP, free, no key)

If Google Places doesn't return enough results for a vertical:
- URL: `https://overpass-api.de/api/interpreter`
- Method: POST
- Headers: `User-Agent: NavaiaForge/1.0 (business development research)`
- Body: `data=<Overpass QL query>`
- Example for clinics in Riyadh:
```
[out:json][timeout:60];
(node["amenity"~"clinic|dentist|doctors"]["name"~"."](24.3,46.3,25.1,47.0);
 way["amenity"~"clinic|dentist|doctors"]["name"~"."](24.3,46.3,25.1,47.0););
out 30;
```

## TWENTY CRM — Create Records

Base URL: `https://crm.navaia.sa`
Auth header: `Authorization: Bearer {twenty_token}`

### Step 1: Create Company

POST `https://crm.navaia.sa/rest/companies`
Headers: `Authorization: Bearer {twenty_token}`, `Content-Type: application/json`
Body:
```json
{{
  "name": "<company name from Places>",
  "domainName": {{ "primaryLinkUrl": "<website from Places, or empty>" }},
  "address": {{
    "addressStreet1": "<street from formattedAddress>",
    "addressCity": "Riyadh",
    "addressCountry": "Saudi Arabia"
  }},
  "sector": "<one of: Contracting & Facilities|Finance & Debt Collection|Private Clinics|Real Estate|Training Institutes>",
  "createdBy": {{ "source": "AGENT", "name": "Mjeed", "context": {{}} }}
}}
```
Response: `{{ "data": {{ "createCompany": {{ "id": "<company_uuid>" }} }} }}`
Extract the company ID from `data.createCompany.id`.

### Step 2: Create Person (linked to company)

POST `https://crm.navaia.sa/rest/people`
Headers: `Authorization: Bearer {twenty_token}`, `Content-Type: application/json`
Body:
```json
{{
  "name": {{ "firstName": "<first name>", "lastName": "<last name>" }},
  "emails": {{ "primaryEmail": "<email if known, or empty>" }},
  "phones": {{
    "primaryPhoneNumber": "<phone number from Places>",
    "primaryPhoneCountryCode": "SA"
  }},
  "jobTitle": "<job title if known, or empty>",
  "sector": "<same sector as company>",
  "companyId": "<company_uuid from step 1>",
  "leadStatus": "Not Contacted",
  "leadSource": "Google-Places",
  "createdBy": {{ "source": "AGENT", "name": "Mjeed", "context": {{}} }}
}}
```
Response: `{{ "data": {{ "createPerson": {{ "id": "<person_uuid>" }} }} }}`

## CRITICAL RULES

1. **REAL DATA ONLY** — Only use data returned by Google Places API or Overpass. NEVER invent or guess any information. If a field is unknown, leave it empty.

2. **NO DUPLICATES** — Before creating a company, search the CRM first:
   GET `https://crm.navaia.sa/rest/companies?limit=100&search=<company name>`
   If a company with the same name already exists, skip it.

3. **Every lead MUST have at least a phone number** (from Places `internationalPhoneNumber`). If a place has no phone, skip it — it's not a valid lead.

4. **Riyadh only** — All leads must be in Riyadh region. The Google Places `locationBias` is set to Riyadh (24.7136, 46.6753, 50km radius). Verify the `formattedAddress` contains "Riyadh".

5. **createdBy** — Always set to `{{ "source": "AGENT", "name": "Mjeed", "context": {{}} }}`.

6. **Person name** — Google Places returns company names, not person names. For the person record:
   - If the company name looks like a person's name, split it into firstName/lastName.
   - If it's a company name (e.g., "Al Olaya Medical Center"), use the company name as firstName and leave lastName empty.
   - Do NOT invent a contact person name.

7. **No outreach** — Do NOT send any emails, WhatsApp messages, or any communication. This is lead finding and CRM entry only.

8. **Sector mapping** — Use EXACTLY these sector values:
   - "Contracting & Facilities"
   - "Finance & Debt Collection"
   - "Private Clinics"
   - "Real Estate"
   - "Training Institutes"

## EXECUTION PLAN

1. For each of the 5 verticals, run Google Places Text Search with 2-3 search terms.
2. Collect all unique places with phone numbers.
3. For each place, check if it already exists in Twenty CRM (search by name).
4. If new, create a Company record, then create a Person record linked to it.
5. Track progress: how many leads added per vertical.
6. Report final summary: total leads added, broken down by vertical.

## API KEYS

- Google Places API Key: `__PLACES_KEY__`
- Twenty CRM Token: `__TWENTY_TOKEN__`
"""

task_description = task_description.replace("__PLACES_KEY__", places_key)
task_description = task_description.replace("__TWENTY_TOKEN__", twenty_token)

print(f"Task title: {task_title}")
print(f"Task description length: {len(task_description)} chars")
print(f"\nCreating task...")

try:
    task = client.tasks.create(
        workforce_id=wf_id,
        title=task_title,
        description=task_description,
        agent_id=tariq_id,
        priority="high",
    )
    print(f"\nTask created successfully!")
    print(f"Task ID: {task.id}")
    print(f"Status: {task.status}")
except Exception as e:
    import traceback
    traceback.print_exc()
