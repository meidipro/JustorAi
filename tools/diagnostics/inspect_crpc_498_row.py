import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
db = create_client(url, key)

res = db.table("document_chunks").select("*").ilike("act_name", "%Criminal Procedure%").eq("section_number", "498").execute()
for r in (res.data or []):
    for k, v in r.items():
        if k != 'embedding':
            print(f"  {k}: {repr(v)[:150]}")
