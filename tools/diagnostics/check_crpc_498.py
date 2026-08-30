import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.environ.get("SUPABASE_URL", "https://zjgmjkcvmiaqvbqucpxo.supabase.co")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
db = create_client(url, key)

res = db.table("document_chunks").select("*").ilike("act_name", "%Criminal Procedure%").eq("section_number", "498").execute()
print(f"CrPC s498 count in DB: {len(res.data or [])}")
for r in (res.data or []):
    print("  Title:", r.get("section_title"))
    print("  Text excerpt:", str(r.get("chunk_text", ""))[:200])
