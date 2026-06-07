import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Check if pilot_query_log exists
    try:
        res = supabase.table("pilot_query_log").select("*").limit(1).execute()
        print("pilot_query_log exists! Sample data:", res.data)
    except Exception as e:
        print("pilot_query_log table does not exist or failed:", e)
        
    # 2. Check if new match_acts_v2 (with filter_act_name) is supported
    try:
        res = supabase.rpc("match_acts_v2", {
            "query_embedding": [0.0]*768,
            "match_count": 1,
            "match_threshold": 0.0,
            "query_section": "1",
            "filter_act_name": "The Land Reforms Act, 2023"
        }).execute()
        print("match_acts_v2 with filter_act_name supported! Results:", res.data)
    except Exception as e:
        print("match_acts_v2 with filter_act_name failed (signature mismatch):", e)
else:
    print("Supabase credentials missing.")
