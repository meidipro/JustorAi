# tools/review_staging.py
"""Interactive / Batch Human Review Tool for Supreme Court Staged Cases.
Allows Sanjib/Legal Reviewer to inspect staged records in sc_judgment_staging,
mark them as SANJIB_REVIEWED, and promote approved cases into production document_chunks.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

from supabase import create_client

SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
STAGING_TABLE = "sc_judgment_staging"

def list_staged_cases(status="UNREVIEWED"):
    res = supabase.table(STAGING_TABLE).select(
        "id, manifest_id, document_type, case_number, case_year, parties_raw, judgment_date, judges, acts_cited, sections_cited, review_status, page_number"
    ).eq("review_status", status).execute()
    
    data = res.data or []
    print(f"\n=== STAGED SUPREME COURT CASES ({len(data)} chunks with status: {status}) ===")
    
    grouped = {}
    for row in data:
        mid = row["manifest_id"]
        if mid not in grouped:
            grouped[mid] = []
        grouped[mid].append(row)
        
    for i, (mid, chunks) in enumerate(grouped.items(), 1):
        first = chunks[0]
        print(f"\n[{i:2d}] Manifest ID: {mid}")
        print(f"     Document Type: {first.get('document_type')} | Case: {first.get('case_number')} ({first.get('case_year')})")
        print(f"     Parties: {first.get('parties_raw')[:70]}...")
        print(f"     Judgment Date: {first.get('judgment_date')} | Judges: {first.get('judges')}")
        print(f"     Total Chunks: {len(chunks)} pages")
        
    return grouped

def review_case(manifest_id, new_status="SANJIB_REVIEWED"):
    supabase.table(STAGING_TABLE).update({
        "review_status": new_status
    }).eq("manifest_id", manifest_id).execute()
    print(f"✓ Manifest '{manifest_id}' updated to status: {new_status}")

def promote_reviewed_cases():
    res = supabase.table(STAGING_TABLE).select("*").eq("review_status", "SANJIB_REVIEWED").eq("promoted_to_production", False).execute()
    staged = res.data or []
    
    if not staged:
        print("\nNo un-promoted SANJIB_REVIEWED cases found in staging.")
        return
        
    print(f"\n=== PROMOTING {len(staged)} REVIEWED CHUNKS TO PRODUCTION (document_chunks) ===")
    
    promoted_count = 0
    for row in staged:
        prod_record = {
            "document_type": row["document_type"],
            "act_name": row.get("case_number") or row["manifest_id"],
            "section_number": str(row.get("page_number", "1")),
            "section_title": row.get("parties_raw") or "Supreme Court Judgment",
            "content": row["content"],
            "status": "Active",
            "jurisdiction": "Bangladesh",
            "embedding": row["embedding"]
        }
        
        try:
            supabase.table("document_chunks").insert(prod_record).execute()
            supabase.table(STAGING_TABLE).update({"promoted_to_production": True}).eq("id", row["id"]).execute()
            promoted_count += 1
        except Exception as e:
            print(f"Error promoting chunk {row['id']}: {e}")
            
    print(f"✓ Successfully promoted {promoted_count}/{len(staged)} chunks into production document_chunks!")

def main():
    parser = argparse.ArgumentParser(description="Human Review & Promotion Tool for Supreme Court Staged Cases")
    parser.add_argument("--list", action="store_true", help="List all staged cases awaiting review")
    parser.add_argument("--approve-all", action="store_true", help="Mark all staged cases as SANJIB_REVIEWED")
    parser.add_argument("--approve", type=str, help="Mark specific manifest_id as SANJIB_REVIEWED")
    parser.add_argument("--promote", action="store_true", help="Promote all SANJIB_REVIEWED cases to production document_chunks")
    args = parser.parse_args()

    if args.list:
        list_staged_cases("UNREVIEWED")
    elif args.approve:
        review_case(args.approve, "SANJIB_REVIEWED")
    elif args.approve_all:
        grouped = list_staged_cases("UNREVIEWED")
        for mid in grouped.keys():
            review_case(mid, "SANJIB_REVIEWED")
    elif args.promote:
        promote_reviewed_cases()
    else:
        grouped = list_staged_cases("UNREVIEWED")
        if not grouped:
            print("\nAll cases reviewed! Run 'python tools/review_staging.py --promote' to push reviewed cases to production.")

if __name__ == "__main__":
    main()
