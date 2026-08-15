import os
import sys
import json
from collections import Counter
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(SUPA_URL, SUPA_KEY)

# 1. Total counts
total_chunks = db.table('document_chunks').select('id', count='exact').execute().count
act_chunks = db.table('document_chunks').select('id', count='exact').eq('document_type', 'Act').execute().count
dlr_chunks = db.table('document_chunks').select('id', count='exact').eq('document_type', 'DLR').execute().count

# 2. Get distinct Acts and count by Act name in 1 query
res_acts = db.table('document_chunks').select('act_name').eq('document_type', 'Act').limit(50000).execute()
act_counts = Counter(r['act_name'] for r in (res_acts.data or []) if r.get('act_name'))

# 3. Get all DLR cases
res_dlr = db.table('document_chunks').select('id, case_title, court_division, year, subject_law, ratio_decidendi, act_name, section_number, created_at').eq('document_type', 'DLR').execute()
dlr_rows = res_dlr.data or []

# 4. Pipeline staged cases
staged_cases = []
if os.path.exists('pipeline/seed_25_cases.json'):
    with open('pipeline/seed_25_cases.json', 'r', encoding='utf-8') as f:
        staged_cases = json.load(f)

result = {
    "database_overview": {
        "total_document_chunks_in_supabase": total_chunks,
        "total_statutory_act_chunks": act_chunks,
        "total_unique_statutes": len(act_counts),
        "total_live_supreme_court_dlr_chunks": dlr_chunks,
        "total_staged_supreme_court_benchmark_cases": len(staged_cases)
    },
    "statutory_acts_stored": [
        {
            "act_name": act_name,
            "sections_ingested": count,
            "status": "Active / Amended",
            "jurisdiction": "Bangladesh"
        }
        for act_name, count in act_counts.most_common()
    ],
    "live_supreme_court_dlrs_stored": dlr_rows,
    "staged_landmark_cases_ready_for_promotion": [
        {
            "case_id": c.get("case_id"),
            "case_title": c.get("case_title"),
            "citation": c.get("citation"),
            "court_division": c.get("court_division"),
            "year": c.get("year"),
            "subject_area": c.get("subject_area"),
            "governing_statutes": [s.get("act_name") for s in c.get("governing_statutes", [])],
            "ratio_decidendi": c.get("ratio_decidendi")
        }
        for c in staged_cases
    ]
}

with open('supabase_database_details.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(json.dumps(result, indent=2, ensure_ascii=False))
