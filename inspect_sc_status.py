import os
import sys
import json
import sqlite3
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(SUPA_URL, SUPA_KEY)

print("=== 1. SUPABASE LIVE DLR / CASE CHUNKS ===")
try:
    res = db.table('document_chunks').select('*').eq('document_type', 'DLR').execute()
    rows = res.data or []
    print(f"Total DLR chunks in live DB: {len(rows)}")
    for i, r in enumerate(rows):
        print(f"{i+1}. Title: {r.get('case_title') or r.get('title') or r.get('act_name')}")
        print(f"   Citation: {r.get('dlr_citation') or r.get('citation')}")
        print(f"   Act/Section: {r.get('act_name')} Sec {r.get('section_number')}")
        print(f"   Ratio: {str(r.get('ratio_decidendi') or r.get('content'))[:100]}...\n")
except Exception as e:
    print("Error querying Supabase:", e)

print("\n=== 2. TRACK B STAGING DATASET (pipeline/seed_25_cases.json) ===")
if os.path.exists('pipeline/seed_25_cases.json'):
    with open('pipeline/seed_25_cases.json', 'r', encoding='utf-8') as f:
        cases = json.load(f)
        print(f"Total staged cases in JSON dataset: {len(cases)}")
        topics = {}
        for c in cases:
            dom = c.get('legal_domain', 'Other')
            topics.setdefault(dom, []).append(c)
        for dom, c_list in topics.items():
            print(f"\n▶ Domain: {dom} ({len(c_list)} cases)")
            for c in c_list:
                print(f"  • [{c.get('case_id')}] {c.get('case_title')} ({c.get('citation')})")
                print(f"    Governing Statutes: {', '.join(c.get('statutory_sections_applied', []))}")
                print(f"    Key Principle: {c.get('ratio_decidendi')}\n")

print("\n=== 3. SUPREME COURT VAULT & MANIFEST ===")
if os.path.exists('sc_manifest.sqlite'):
    conn = sqlite3.connect('sc_manifest.sqlite')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    print(f"SQLite Tables: {tables}")
    for tbl in tables:
        c.execute(f"SELECT count(*) FROM {tbl}")
        print(f"  Table '{tbl}' total rows: {c.fetchone()[0]}")
    conn.close()
