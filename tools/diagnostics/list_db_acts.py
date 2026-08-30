import os, sys
sys.path.insert(0, 'backend')
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

# Try all possible env var names
url = os.environ.get("VITE_SUPABASE_URL", "").strip()
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

print(f"URL found: {'YES' if url else 'NO'} | Key found: {'YES' if key else 'NO'}")
if not url or not key:
    # Print all env vars that mention supabase
    for k, v in os.environ.items():
        if 'supabase' in k.lower() or 'SUPA' in k:
            print(f"  {k} = {v[:30]}...")
    sys.exit(1)

db = create_client(url, key)

resp = db.table("document_chunks").select("act_name").eq("document_type", "Act").execute()
acts = sorted(set(r['act_name'] for r in resp.data if r.get('act_name')))
print(f"\nTotal unique acts in DB: {len(acts)}")
for a in acts:
    print(f"  - {a}")
