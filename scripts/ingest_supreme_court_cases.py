#!/usr/bin/env python3
"""
scripts/ingest_supreme_court_cases.py
Ingests the 245 scraped Supreme Court of Bangladesh cases into Supabase:
- Table: legal_cases
- Table: documents
"""

import os
import sys
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not configured!")
    sys.exit(1)

db = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scraped_supreme_court_cases_200.json")

def main():
    if not os.path.exists(DATA_PATH):
        print(f"❌ File not found: {DATA_PATH}")
        sys.exit(1)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Starting ingestion of {len(cases)} Supreme Court cases into Supabase...")

    # 1. Ingest into legal_cases in batches of 50
    legal_cases_payload = []
    for c in cases:
        legal_cases_payload.append({
            "external_case_id": c["id"],
            "case_title": c["case_title"],
            "citation": c.get("case_number"),
            "court_division": c.get("division", "High Court Division"),
            "year": c.get("year"),
            "official_url": c.get("pdf_url"),
            "judgment_text": f"Supreme Court of Bangladesh - {c.get('division', 'High Court Division')} judgment in {c['case_title']}. Official Source: {c.get('pdf_url')}",
            "ratio_summary": f"{c.get('case_type', 'Matter')} filed/disposed under {c.get('division', 'High Court Division')} jurisdiction. Official PDF record available.",
            "ratio_type": "EDITORIAL_SUMMARY",
            "human_verified": False
        })

    print(f"Upserting {len(legal_cases_payload)} records into 'legal_cases'...")
    batch_size = 50
    inserted_cases = 0
    for i in range(0, len(legal_cases_payload), batch_size):
        batch = legal_cases_payload[i:i+batch_size]
        try:
            r = db.table("legal_cases").upsert(batch, on_conflict="external_case_id").execute()
            inserted_cases += len(batch)
            print(f"  ✓ Ingested legal_cases batch {i//batch_size + 1}: {len(batch)} items (Total: {inserted_cases})")
        except Exception as e:
            print(f"  ❌ Error inserting legal_cases batch {i//batch_size + 1}: {e}")

    # 2. Ingest into documents table in batches
    docs_payload = []
    for c in cases:
        content_text = (
            f"Supreme Court of Bangladesh ({c.get('division', 'High Court Division')})\n"
            f"Case: {c['case_title']}\n"
            f"Type: {c.get('case_type')}\n"
            f"Case Number: {c.get('case_number')}\n"
            f"Year: {c.get('year')}\n"
            f"Official Record URL: {c.get('pdf_url')}\n"
            f"Translation Portal URL: {c.get('translation_url')}\n"
            f"Source: supremecourt.gov.bd"
        )
        docs_payload.append({
            "title": c["case_title"],
            "content": content_text,
            "metadata": {
                "source": "supremecourt.gov.bd",
                "external_id": c["id"],
                "case_type": c.get("case_type"),
                "case_number": c.get("case_number"),
                "year": c.get("year"),
                "division": c.get("division"),
                "pdf_url": c.get("pdf_url"),
                "translation_url": c.get("translation_url"),
                "filename": c.get("filename")
            }
        })

    print(f"\nInserting {len(docs_payload)} records into 'documents'...")
    inserted_docs = 0
    for i in range(0, len(docs_payload), batch_size):
        batch = docs_payload[i:i+batch_size]
        try:
            r = db.table("documents").insert(batch).execute()
            inserted_docs += len(batch)
            print(f"  ✓ Ingested documents batch {i//batch_size + 1}: {len(batch)} items (Total: {inserted_docs})")
        except Exception as e:
            print(f"  ❌ Error inserting documents batch {i//batch_size + 1}: {e}")

    print(f"\n✅ INGESTION COMPLETE: {inserted_cases} cases in 'legal_cases' and {inserted_docs} entries in 'documents'.")

if __name__ == "__main__":
    main()
