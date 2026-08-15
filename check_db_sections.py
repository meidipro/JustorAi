import os
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

url = os.environ.get("VITE_SUPABASE_URL", "").strip()
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(url, key)

queries = [
    ("Penal Code 500", "The Penal Code, 1860", "500"),
    ("CrPC 498", "The Code of Criminal Procedure, 1898", "498"),
    ("CrPC 29C", "The Code of Criminal Procedure, 1898", "29C"),
    ("Labour Act 4", "The Bangladesh Labour Act, 2006", "4"),
    ("Limitation Act 113", "The Limitation Act, 1908", "113"),
]

for label, act, sec in queries:
    res = db.table("document_chunks").select("act_name, section_number, section_title").eq("act_name", act).eq("section_number", sec).execute()
    print(f"{label}: found {len(res.data)} items -> {res.data}")
