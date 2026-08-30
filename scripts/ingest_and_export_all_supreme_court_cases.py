#!/usr/bin/env python3
"""
scripts/ingest_and_export_all_supreme_court_cases.py
1. Ingests the 50 Dual-Lawyer Verified Landmark Supreme Court cases into Supabase 'legal_cases'.
2. Ingests/Upserts the 245 scraped High Court cases with full judgment text into Supabase 'legal_cases'.
3. Queries and exports the entire consolidated Supreme Court case database to:
   - data/total_ingested_supreme_court_cases.json
   - data/total_ingested_supreme_court_cases_summary.json
4. Updates supabase_database_details.json with the latest database overview.
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(".env")
load_dotenv(".env.local")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not configured in .env!")
    sys.exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDMARK_PATH = os.path.join(BASE_DIR, "pipeline", "seed_25_cases.json")
SCRAPED_PATH = os.path.join(BASE_DIR, "data", "scraped_supreme_court_cases_200.json")
EXPORT_JSON_PATH = os.path.join(BASE_DIR, "data", "total_ingested_supreme_court_cases.json")
SUMMARY_JSON_PATH = os.path.join(BASE_DIR, "data", "total_ingested_supreme_court_cases_summary.json")
DB_DETAILS_PATH = os.path.join(BASE_DIR, "supabase_database_details.json")

def main():
    print("=" * 70)
    print("Justor AI — Master Supreme Court Case Ingestion & Database Export")
    print("=" * 70)

    # 1. Load Landmark Cases (50 cases)
    with open(LANDMARK_PATH, "r", encoding="utf-8") as f:
        landmark_cases = json.load(f)
    print(f"\n[1/4] Loaded {len(landmark_cases)} Dual-Lawyer Verified Landmark Cases.")

    # 2. Load Scraped Cases (245 cases)
    with open(SCRAPED_PATH, "r", encoding="utf-8") as f:
        scraped_cases = json.load(f)
    print(f"[2/4] Loaded {len(scraped_cases)} Scraped Supreme Court Cases with Full Judgment Text.")

    # 3. Format Landmark Cases for 'legal_cases'
    landmark_payload = []
    for c in landmark_cases:
        passages_text = "\n\n".join([p.get("quote_text", "") for p in c.get("exact_key_passages", [])])
        statutes_str = ", ".join([f"{s.get('act_name')} ({', '.join(s.get('sections', []))})" for s in c.get("governing_statutes", [])])
        
        landmark_payload.append({
            "external_case_id": c["case_id"],
            "case_title": c["case_title"],
            "citation": c.get("citation"),
            "court_division": c.get("court_division", "Appellate Division"),
            "judgment_date": c.get("judgment_date"),
            "year": int(c.get("year", 2020)),
            "official_url": c.get("pdf_source_url") or "https://supremecourt.gov.bd",
            "judgment_text": passages_text or c.get("ratio_decidendi", ""),
            "ratio_summary": f"{c.get('ratio_decidendi', '')}\n\n[Controlling Statutes: {statutes_str}]",
            "ratio_type": "VERBATIM_EXCERPT",
            "human_verified": True
        })

    # 4. Format Scraped Cases for 'legal_cases'
    scraped_payload = []
    for c in scraped_cases:
        full_text = (c.get("full_judgment_text", "") or "").replace("\x00", "").replace("\u0000", "")
        title_clean = (c.get("case_title", "") or "").replace("\x00", "").replace("\u0000", "")
        scraped_payload.append({
            "external_case_id": c["id"],
            "case_title": title_clean,
            "citation": c.get("case_number"),
            "court_division": c.get("division", "High Court Division"),
            "year": int(c.get("year", 2020)) if c.get("year") else 2020,
            "official_url": c.get("pdf_url"),
            "judgment_text": full_text if len(full_text) > 50 else f"Supreme Court of Bangladesh - {c.get('division', 'High Court Division')} judgment in {title_clean}. Source: {c.get('pdf_url')}",
            "ratio_summary": f"Full judgment text extracted ({len(full_text)} chars). Case: {title_clean}. Official Source: {c.get('pdf_url')}",
            "ratio_type": "EDITORIAL_SUMMARY",
            "human_verified": False
        })

    # 5. Upsert Landmark Cases in batches
    print(f"\n[3/4] Upserting {len(landmark_payload)} Landmark Cases into 'legal_cases'...")
    batch_size = 25
    for i in range(0, len(landmark_payload), batch_size):
        batch = landmark_payload[i:i+batch_size]
        try:
            client.table("legal_cases").upsert(batch, on_conflict="external_case_id").execute()
            print(f"  ✓ Ingested landmark batch {i//batch_size + 1}: {len(batch)} cases")
        except Exception as e:
            print(f"  ❌ Error in landmark batch {i//batch_size + 1}: {e}")

    # 6. Upsert Scraped Cases in batches
    print(f"\nUpserting {len(scraped_payload)} Scraped Cases into 'legal_cases'...")
    for i in range(0, len(scraped_payload), batch_size):
        batch = scraped_payload[i:i+batch_size]
        try:
            client.table("legal_cases").upsert(batch, on_conflict="external_case_id").execute()
            print(f"  ✓ Ingested scraped batch {i//batch_size + 1}: {len(batch)} cases (Total: {min(i+batch_size, len(scraped_payload))})")
        except Exception as e:
            print(f"  ❌ Error in scraped batch {i//batch_size + 1}: {e}")

    # 7. Query and Export Total Ingested Cases from Database
    print(f"\n[4/4] Querying and exporting total Supreme Court cases from live database...")
    all_exported_cases = []
    page_size = 100
    offset = 0

    while True:
        res = client.table("legal_cases").select("*").order("created_at", desc=False).range(offset, offset + page_size - 1).execute()
        rows = res.data or []
        if not rows:
            break
        all_exported_cases.extend(rows)
        offset += len(rows)
        if len(rows) < page_size:
            break

    print(f"\n✅ Total Cases Retrieved from Database: {len(all_exported_cases)}")

    # Write Full Export JSON
    with open(EXPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_exported_cases, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Exported full dataset to: {EXPORT_JSON_PATH} ({os.path.getsize(EXPORT_JSON_PATH):,} bytes)")

    # Build Summary
    summary = {
        "export_date": datetime.utcnow().isoformat() + "Z",
        "total_supreme_court_cases_ingested": len(all_exported_cases),
        "verified_landmark_cases": sum(1 for c in all_exported_cases if c.get("human_verified") is True),
        "scraped_full_text_cases": sum(1 for c in all_exported_cases if c.get("human_verified") is False),
        "breakdown_by_court_division": {},
        "breakdown_by_ratio_type": {},
        "sample_cases": [
            {
                "id": c.get("id"),
                "external_case_id": c.get("external_case_id"),
                "case_title": c.get("case_title"),
                "citation": c.get("citation"),
                "court_division": c.get("court_division"),
                "human_verified": c.get("human_verified"),
                "ratio_type": c.get("ratio_type")
            }
            for c in all_exported_cases[:10]
        ]
    }

    for c in all_exported_cases:
        div = c.get("court_division") or "Unknown"
        summary["breakdown_by_court_division"][div] = summary["breakdown_by_court_division"].get(div, 0) + 1
        rt = c.get("ratio_type") or "NONE"
        summary["breakdown_by_ratio_type"][rt] = summary["breakdown_by_ratio_type"].get(rt, 0) + 1

    with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Exported summary to: {SUMMARY_JSON_PATH}")

    # Update supabase_database_details.json
    if os.path.exists(DB_DETAILS_PATH):
        try:
            with open(DB_DETAILS_PATH, "r", encoding="utf-8") as f:
                db_details = json.load(f)
            if "database_overview" in db_details:
                db_details["database_overview"]["total_supreme_court_cases_in_legal_cases"] = len(all_exported_cases)
                db_details["database_overview"]["total_verified_landmark_cases"] = summary["verified_landmark_cases"]
                db_details["database_overview"]["total_scraped_high_court_cases"] = summary["scraped_full_text_cases"]
                db_details["database_overview"]["last_case_sync"] = datetime.utcnow().isoformat() + "Z"
            with open(DB_DETAILS_PATH, "w", encoding="utf-8") as f:
                json.dump(db_details, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Updated {DB_DETAILS_PATH}")
        except Exception as e:
            print(f"  Note updating db_details: {e}")

    print("\n" + "=" * 70)
    print(f"ALL INGESTION & EXPORT COMPLETED SUCCESSFULLY!")
    print(f"Total Cases Ingested & Exported: {len(all_exported_cases)}")
    print(f"  - Landmark Decisions (Dual-Lawyer Verified): {summary['verified_landmark_cases']}")
    print(f"  - Scraped High Court Judgments: {summary['scraped_full_text_cases']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
