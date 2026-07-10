#!/usr/bin/env python3
"""
Import all 36 enriched leads to Twenty CRM.
- Fix invalid email (info@saudi-skills.com\ -> info@saudi-skills.com)
- Skip شركة اتقان العقارية (already imported as test)
- For each lead: create Company + linked Person (contact)
- Store place_id as Note on company (no native field in Twenty)
- Dedup: Check if company exists by name before creating
- Rate-limited: 0.5s between API calls
"""
import sys, io, re, json, csv, time
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

INPUT = "C:/Users/aabbo/navaia-forge-sdk/leads_enriched.csv"
SKIP_COMPANY = "شركة اتقان العقارية"  # Already imported as test

stats = {
    "total": 0,
    "skipped": 0,
    "already_exists": 0,
    "companies_created": 0,
    "contacts_created": 0,
    "notes_created": 0,
    "errors": 0,
    "has_email": 0,
    "no_email": 0,
}


def find_company_by_name(name):
    """Search for company by name in CRM. Returns company_id or None."""
    query = {
        "query": """query FindCompany($name: String!) {
            companies(filter: { name: { ilike: $name } }, first: 5) {
                edges { node { id name address { addressCity } } }
            }
        }""",
        "variables": {"name": name}
    }
    try:
        resp = httpx.post(f"{base_url}/graphql", headers=headers, json=query, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            edges = data.get("data", {}).get("companies", {}).get("edges", [])
            if edges:
                return edges[0]["node"]["id"]
    except Exception as e:
        print(f"    WARN: Error searching company: {e}", flush=True)
    return None


def create_note_for_company(company_id, title, body):
    """Create a note attached to a company."""
    mutation = {
        "query": """mutation CreateNote($companyId: ID!, $title: String!, $body: String!) {
            createNote(companyId: $companyId, title: $title, body: $body) { id }
        }""",
        "variables": {
            "companyId": company_id,
            "title": title,
            "body": body
        }
    }
    try:
        resp = httpx.post(f"{base_url}/graphql", headers=headers, json=mutation, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            note = data.get("data", {}).get("createNote", {})
            return note.get("id")
    except Exception as e:
        print(f"    ERROR creating note: {e}", flush=True)
    return None

def create_company(lead):
    """Create a company in CRM. Returns company_id or None."""
    body = {
        "name": lead["company_name"],
        "address": {
            "addressStreet1": lead.get("address", "")
        },
        "sector": lead.get("sector", ""),
        "createdBy": {
            "source": "AGENT",
            "name": "Mjeed using [Tariq SDR Agent]",
            "context": {}
        },
        "customFields": {
            "place_id": lead.get("place_id", "")
        }
    }

    domain = lead.get("domain_name", "").strip()
    if domain:
        body["domainName"] = {
            "primaryLinkUrl": domain if domain.startswith("http") else f"https://{domain}"
        }

    try:
        resp = httpx.post(f"{base_url}/rest/companies", headers=headers, json=body, timeout=30)
        if resp.status_code in (200, 201):
            data = resp.json()
            # Extract company ID from nested response
            company = data.get("data", {}).get("createCompany", {})
            return company.get("id")
        else:
            print(f"    ERROR: HTTP {resp.status_code}: {resp.text[:200]}", flush=True)
            return None
    except Exception as e:
        print(f"    ERROR: {e}", flush=True)
        return None


def create_person(lead, company_id):
    """Create a contact linked to a company. Returns person_id or None."""
    body = {
        "name": {
            "firstName": lead["company_name"],
            "lastName": ""
        },
        "companyId": company_id,
        "sector": lead.get("sector", ""),
        "leadSource": lead.get("lead_source", ""),
        "leadStatus": "Not Contacted",
        "createdBy": {
            "source": "AGENT",
            "name": "Mjeed using [Tariq SDR Agent]",
            "context": {}
        }
    }

    email = lead.get("email", "").strip()
    if email:
        body["emails"] = {"primaryEmail": email}

    phone = lead.get("phone", "").strip()
    if phone:
        body["phones"] = {
            "primaryPhoneNumber": phone,
            "primaryPhoneCountryCode": "SA"
        }

    try:
        resp = httpx.post(f"{base_url}/rest/people", headers=headers, json=body, timeout=30)
        if resp.status_code in (200, 201):
            data = resp.json()
            person = data.get("data", {}).get("createPerson", {})
            return person.get("id")
        else:
            print(f"    ERROR (person): HTTP {resp.status_code}: {resp.text[:200]}", flush=True)
            return None
    except Exception as e:
        print(f"    ERROR (person): {e}", flush=True)
        return None


def main():
    # Load leads
    with open(INPUT, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    print(f"Loaded {len(leads)} leads\n", flush=True)
    
    # Calculate target count (total leads minus skipped)
    target_count = len(leads) - 1  # -1 for the skipped test company
    
    # Keep importing until we reach the target count
    while True:
        # Reset stats for this iteration
        for key in stats:
            stats[key] = 0
            
        # Process all leads
        for i, lead in enumerate(leads):
        company_name = lead.get("company_name", "")
        stats["total"] += 1

        # Skip already-imported test company
        if company_name == SKIP_COMPANY:
            stats["skipped"] += 1
            print(f"  [{i+1}/{len(leads)}] SKIP (already imported): {company_name[:45]}", flush=True)
            continue

        # Fix invalid email
        email = lead.get("email", "").strip()
        if email.endswith("\\"):
            email = email.rstrip("\\")
            lead["email"] = email
            print(f"  [{i+1}/{len(leads)}] Fixed email: {email}", flush=True)

        has_email = bool(email)
        if has_email:
            stats["has_email"] += 1
        else:
            stats["no_email"] += 1

        email_display = email if email else "(none)"
        status = lead.get("email_status", "")
        print(f"  [{i+1}/{len(leads)}] {company_name[:45]} | email={email_display} | {status}", flush=True)

        # 1. Check if company already exists (dedup)
        existing_id = find_company_by_name(company_name)
        time.sleep(0.3)

        if existing_id:
            stats["already_exists"] += 1
            company_id = existing_id
            print(f"    EXISTS: {company_id} (skipping creation)", flush=True)
        else:
            # Create company
            company_id = create_company(lead)
            time.sleep(0.5)

            if not company_id:
                stats["errors"] += 1
                print(f"    FAILED to create company", flush=True)
                continue

            stats["companies_created"] += 1
            print(f"    Company: {company_id}", flush=True)

        # 1b. Store place_id as Note (if available)
        place_id = lead.get("place_id", "").strip()
        if place_id and company_id:
            note_body = f"Google Places ID: {place_id}\nSource: Google Places API\nImported: {time.strftime('%Y-%m-%d')}"
            note_id = create_note_for_company(company_id, "Place ID Reference", note_body)
            if note_id:
                stats["notes_created"] += 1
                print(f"    Note (place_id): {note_id}", flush=True)
            time.sleep(0.3)

        # 2. Create contact
        person_id = create_person(lead, company_id)
        time.sleep(0.5)

        if person_id:
            stats["contacts_created"] += 1
            print(f"    Contact: {person_id}", flush=True)
        else:
            stats["errors"] += 1
            print(f"    FAILED to create contact", flush=True)

    # Summary
    print(f"\n{'='*60}", flush=True)
    print(f"IMPORT COMPLETE", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"  Total leads:        {stats['total']}", flush=True)
    print(f"  Skipped (test):     {stats['skipped']}", flush=True)
    print(f"  Already in CRM:     {stats['already_exists']}", flush=True)
    print(f"  Companies created:  {stats['companies_created']}", flush=True)
    print(f"  Contacts created:   {stats['contacts_created']}", flush=True)
    print(f"  Notes created:      {stats['notes_created']}", flush=True)
    print(f"  Errors:             {stats['errors']}", flush=True)
    print(f"  With email:         {stats['has_email']}", flush=True)
    print(f"  No email (phone):   {stats['no_email']}", flush=True)
    print(f"\n--- Count-Actual / Top-Up ---", flush=True)
    actual_in_crm = stats['already_exists'] + stats['companies_created']
    print(f"  Actual in CRM:      {actual_in_crm}", flush=True)
    print(f"  Target total:       {target_count}", flush=True)
    print(f"  Need to import:     {target_count - actual_in_crm}", flush=True)
    
    # Check if we've reached the target count
    if actual_in_crm >= target_count:
        print(f"\nTarget count reached. All done.", flush=True)
        break
    else:
        print(f"\nContinuing import to reach target...", flush=True)
        time.sleep(2)  # Brief pause before next iteration


if __name__ == "__main__":
    main()
