import sys, io, traceback, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from navaia_forge import NavaiaForgeClient

local_key = open('C:/Users/aabbo/navaia-forge-sdk/_local_api_key.txt').read().strip()
client = NavaiaForgeClient(api_key=local_key, base_url='http://localhost:8001')

wf_id = '8515d24a-6195-4a73-9cd3-37eb02f08693'

# Read the Twenty token from .env
import re
env_content = open('C:/Users/aabbo/navaia-forge-sdk/.env').read()
token_match = re.search(r'TWENTY_TOKEN=(.+)', env_content)
twenty_token = token_match.group(1).strip() if token_match else ''
print(f"Twenty token loaded: {twenty_token[:30]}...{twenty_token[-10:]}")

# Find the local Twenty CRM integration
integrations = client.integrations.list(workforce_id=wf_id)
twenty_int = None
for i in integrations:
    if i.plugin_name == 'twenty':
        twenty_int = i
        break

if not twenty_int:
    print("ERROR: No Twenty CRM integration found locally")
    sys.exit(1)

print(f"\nTwenty integration ID: {twenty_int.id}")
print(f"Current status: {twenty_int.status}")
print(f"Current config: {twenty_int.config_json}")

# Update with the real token
config = {
    "api_key": twenty_token,
    "base_url": "https://navaia-business.twenty.com"
}

try:
    updated = client.integrations.update(
        integration_id=twenty_int.id,
        config_json=config,
        status="active"
    )
    print(f"\nUpdated! Status: {updated.status}")
    print(f"Config: {json.dumps(updated.config_json, default=str)}")
except Exception as e:
    traceback.print_exc()
