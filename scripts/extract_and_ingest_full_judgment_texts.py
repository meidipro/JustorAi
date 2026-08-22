#!/usr/bin/env python3
"""
scripts/extract_and_ingest_full_judgment_texts.py
Downloads the official judgment PDFs from the Supreme Court of Bangladesh,
extracts the actual full judgment text using PyMuPDF (fitz),
and updates the Supabase 'legal_cases' and 'documents' tables with the full text.
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import requests
import urllib3
import fitz
from supabase import create_client

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

urllib3.disable_warnings()
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

db = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scraped_supreme_court_cases_200.json")

def create_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/pdf,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://supremecourt.gov.bd/web/?page=judgments.php&menu=00&div_id=2&type_id=5&lang="
    })
    s.get("https://supremecourt.gov.bd/web/?lang=", verify=False, timeout=20)
    s.get("https://supremecourt.gov.bd/web/?page=judgments.php&menu=00&div_id=2&type_id=5&lang=", verify=False, timeout=20)
    return s

def extract_pdf_text(session: requests.Session, pdf_url: str) -> str:
    try:
        r = session.get(pdf_url, verify=False, timeout=25)
        if r.status_code == 200 and r.content.startswith(b"%PDF"):
            doc = fitz.open(stream=r.content, filetype="pdf")
            text_pages = [page.get_text() for page in doc]
            full_text = "\n\n".join(text_pages).strip()
            return full_text
        else:
            return ""
    except Exception as e:
        print(f"    Error downloading {pdf_url}: {e}")
        return ""

def main(max_cases: int = 245):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    session = create_session()
    print(f"Extracting full judgment text for up to {max_cases} cases...")

    processed = 0
    updated_cases = []

    for i, c in enumerate(cases[:max_cases]):
        print(f"[{i+1}/{min(len(cases), max_cases)}] {c['case_title']} ({c['id']})...")
        pdf_text = extract_pdf_text(session, c["pdf_url"])
        
        if pdf_text:
            char_count = len(pdf_text)
            c["full_judgment_text"] = pdf_text
            c["char_count"] = char_count
            
            # Extract header info if possible
            first_500 = pdf_text[:500]
            bench_match = re.search(r"Present\s*:\s*([^\n]+(?:\n[^\n]+){1,3})", first_500, re.IGNORECASE)
            bench = bench_match.group(1).strip().replace("\n", " ") if bench_match else None
            
            # Update Supabase legal_cases
            try:
                db.table("legal_cases").update({
                    "judgment_text": pdf_text,
                    "ratio_summary": f"Full judgment text extracted ({char_count} chars). Bench: {bench or 'High Court Division'}"
                }).eq("external_case_id", c["id"]).execute()
                
                # Update Supabase documents
                db.table("documents").update({
                    "content": pdf_text
                }).eq("metadata->>external_id", c["id"]).execute()
                
                print(f"  ✓ Extracted {char_count} chars & updated Supabase")
                processed += 1
            except Exception as e:
                print(f"  ❌ Supabase update error: {e}")
        else:
            print(f"  ⚠️ Could not extract PDF text for {c['pdf_url']}")
            
        time.sleep(0.2)

    # Save enriched dataset locally as well
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Completed full-text extraction and Supabase update for {processed} judgments.")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 245
    main(count)
