from __future__ import annotations

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
from backend.backend import _embed

SUPABASE_CASES_URL = os.getenv("SUPABASE_CASES_URL", "").strip()
SUPABASE_CASES_KEY = os.getenv("SUPABASE_CASES_KEY", "").strip()

if not SUPABASE_CASES_URL or not SUPABASE_CASES_KEY:
    print("❌ ERROR: SUPABASE_CASES_URL and SUPABASE_CASES_KEY must be set in .env")
    sys.exit(1)

client = create_client(SUPABASE_CASES_URL, SUPABASE_CASES_KEY)

def main():
    seed_path = "pipeline/seed_25_cases.json"
    with open(seed_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Syncing {len(cases)} Landmark Supreme Court Cases into Project B...")
    success = 0
    for case in cases:
        case_id = case.get("case_id")
        title = case.get("case_title")
        content_to_embed = f"{title} {case.get('ratio_decidendi','')} {case.get('subject_area','')}"
        vec = _embed(content_to_embed)

        payload = {
            "case_id": case_id,
            "case_title": title,
            "citation": case.get("citation") or case.get("dlr_citation"),
            "court_division": case.get("court_division"),
            "year": int(case.get("year", 2020)),
            "judgment_date": case.get("judgment_date"),
            "bench_judges": case.get("bench_judges"),
            "subject_area": case.get("subject_area"),
            "governing_statutes": case.get("governing_statutes"),
            "ratio_decidendi": case.get("ratio_decidendi"),
            "exact_key_passages": case.get("exact_key_passages"),
            "judgment_content": case.get("judgment_content"),
            "pdf_source_url": case.get("pdf_source_url"),
            "embedding": vec
        }

        # Check if exists by case_id
        res = client.table("case_chunks").select("id").eq("case_id", case_id).execute()
        if res.data:
            rec_id = res.data[0]["id"]
            client.table("case_chunks").update(payload).eq("id", rec_id).execute()
            print(f"  [UPDATED] {case_id} -> {title[:40]}")
        else:
            client.table("case_chunks").insert(payload).execute()
            print(f"  [INSERTED] {case_id} -> {title[:40]}")
        success += 1

    print(f"\nSuccessfully synced {success}/{len(cases)} cases into Project B.")

if __name__ == "__main__":
    main()
