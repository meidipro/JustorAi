from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

def inspect_project(name: str, url: str, key: str):
    print(f"\n=======================================================")
    print(f"   INVENTORY AUDIT: {name}")
    print(f"   URL: {url}")
    print(f"=======================================================")
    if not url or not key:
        print("❌ URL or KEY missing!")
        return {}

    client = create_client(url, key)
    
    # Candidate tables to check
    candidate_tables = [
        "legal_instruments", "legal_provisions", "legal_instrument_aliases",
        "provision_relationships", "documents", "document_chunks",
        "cases", "case_law", "supreme_court_cases", "dlr_cases", "judgments",
        "legal_sources", "section_versions", "amendments", "amendment_effects",
        "legal_search_index", "audit_log", "users", "profiles"
    ]
    
    table_stats = {}
    for tbl in candidate_tables:
        try:
            res = client.table(tbl).select("*", count="exact").limit(1).execute()
            count = res.count if res.count is not None else len(res.data)
            sample_cols = list(res.data[0].keys()) if res.data else []
            table_stats[tbl] = {
                "exists": True,
                "count": count,
                "columns": sample_cols
            }
            print(f"  [FOUND] {tbl:25} | Rows: {count:6} | Columns: {len(sample_cols)}")
            if sample_cols:
                has_can = "canonical_key" in sample_cols or "canonical_title" in sample_cols
                has_ver = "verification_status" in sample_cols or "verified" in sample_cols or "official_source_verified" in sample_cols
                has_src = "source_url" in sample_cols or "official_url" in sample_cols
                print(f"          -> Key Fields: canonical={has_can}, verified={has_ver}, source={has_src}")
        except Exception as e:
            # Table probably does not exist or access denied
            pass
            
    return table_stats

def main():
    laws_url = os.getenv("VITE_SUPABASE_URL", "").strip()
    laws_key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")).strip()
    
    cases_url = os.getenv("SUPABASE_CASES_URL", "").strip()
    cases_key = os.getenv("SUPABASE_CASES_KEY", "").strip()
    
    inspect_project("PROJECT A (Laws & Statutory Knowledge)", laws_url, laws_key)
    inspect_project("PROJECT B (Supreme Court & Case Law)", cases_url, cases_key)

if __name__ == "__main__":
    main()
