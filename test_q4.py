import os
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
import httpx

url = os.environ.get("VITE_SUPABASE_URL", "").strip()
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(url, key)

# Search specifically for Penal Code 500
res = db.table("document_chunks").select("act_name, section_number, section_title").eq("act_name", "The Penal Code, 1860").ilike("section_number", "%500%").execute()
print("Direct table query for Penal Code 500:", res.data)
