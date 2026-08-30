import os
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(SUPA_URL, SUPA_KEY)

try:
    res = db.rpc("exec_sql", {"sql": "DROP FUNCTION IF EXISTS match_acts_v2(vector, float, int, text, boolean, boolean, text);"}).execute()
    print("Dropped successfully via exec_sql:", res)
except Exception as e:
    print("exec_sql not available:", e)
