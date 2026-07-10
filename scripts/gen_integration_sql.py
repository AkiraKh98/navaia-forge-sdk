import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Read credentials from .env
env_content = open('C:/Users/aabbo/navaia-forge-sdk/.env').read()

def env(key):
    m = re.search(rf'^{key}=(.+)$', env_content, re.MULTILINE)
    return m.group(1).strip() if m else ''

twenty_token = env('TWENTY_TOKEN')
zoho_mail = env('ZOHO_MAIL')
zoho_pass = env('ZOHO_PASS')
snov_id = env('SNOV_USER_ID')
snov_secret = env('SNOV_USER_SECRET')

print(f"Twenty token: {twenty_token[:25]}...{twenty_token[-8:]}")
print(f"Zoho mail: {zoho_mail}")
print(f"Zoho pass: {'*' * len(zoho_pass)}")
print(f"Snov ID: {snov_id}")
print(f"Snov secret: {snov_secret[:8]}...")

# Build SQL to update all three integrations directly in the DB
# The integrations table has columns: id, workforce_id, plugin_name, display_name, config_json, status, last_error, created_at, updated_at
# config_json is JSON, status is VARCHAR

updates = {
    'twenty': {
        'api_key': twenty_token,
        'base_url': 'https://navaia-business.twenty.com'
    },
    'zoho': {
        'smtp_user': zoho_mail,
        'smtp_password': zoho_pass,
        'smtp_host': 'smtp.zoho.com'
    },
    'snov': {
        'client_id': snov_id,
        'client_secret': snov_secret
    }
}

for plugin, cfg in updates.items():
    cfg_json = json.dumps(cfg).replace("'", "''")
    sql = f"UPDATE integrations SET config_json = '{cfg_json}'::json, status = 'ACTIVE', last_error = NULL, updated_at = NOW() WHERE plugin_name = '{plugin}';"
    print(f"\n--- {plugin} ---")
    print(sql)
