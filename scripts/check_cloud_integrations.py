import sys, io, traceback, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from navaia_forge import NavaiaForgeClient

# Cloud client — key read from env / .env, never hardcoded
import os as _os, re as _re


def _secret(_name):
    _v = _os.environ.get(_name)
    if _v:
        return _v
    _env = open(_os.path.join(_os.path.dirname(__file__), "..", ".env")).read()
    _m = _re.search(rf"^{_name}=(.+)$", _env, _re.M)
    return _m.group(1).strip() if _m else None


cloud_key = _secret("BUSINESS_NF")
cloud = NavaiaForgeClient(api_key=cloud_key, base_url='https://fareegi.navaia.sa')

cloud_wf = '131bb52f-e5eb-44ad-8134-03dc6908b485'

print("=== CLOUD INTEGRATIONS ===")
try:
    integrations = cloud.integrations.list(workforce_id=cloud_wf)
    for i in integrations:
        print(f"\n--- {i.display_name} ({i.plugin_name}) ---")
        print(json.dumps(i.model_dump(), indent=2, default=str))
except Exception as e:
    traceback.print_exc()
