import os
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(SUPA_URL, SUPA_KEY)

print("Testing match_acts_v2...")
try:
    res = db.rpc("match_acts_v2", {
        "query_embedding": [0.0]*1024,
        "match_count": 2,
        "match_threshold": 0.3,
        "query_section": None,
        "prefer_dead_law": False,
        "prefer_amended": False,
        "filter_act_name": None
    }).execute()
    print("match_acts_v2 SUCCESS! Rows:", len(res.data or []))
except Exception as e:
    print("match_acts_v2 ERROR:", e)

print("\nTesting match_dlrs_v2...")
try:
    res = db.rpc("match_dlrs_v2", {
        "query_embedding": [0.0]*1024,
        "match_count": 2,
        "match_threshold": 0.3
    }).execute()
    print("match_dlrs_v2 SUCCESS! Rows:", len(res.data or []))
except Exception as e:
    print("match_dlrs_v2 ERROR:", e)
