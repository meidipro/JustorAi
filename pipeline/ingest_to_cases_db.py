import os
import sys
import json
import time
import urllib.request
import urllib.error
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

# 1. Connect to the NEW Cases Project
CASES_URL = os.environ.get("SUPABASE_CASES_URL", "").strip()
CASES_KEY = os.environ.get("SUPABASE_CASES_KEY", "").strip()
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

if not CASES_URL or not CASES_KEY:
    print("❌ ERROR: SUPABASE_CASES_URL and SUPABASE_CASES_KEY must be set in .env")
    sys.exit(1)

if not OPENROUTER_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY must be set in .env")
    sys.exit(1)

db_cases = create_client(CASES_URL, CASES_KEY)

def get_bge_embedding(text: str):
    """Generate 1024-dim BGE-M3 embedding."""
    url = "https://openrouter.ai/api/v1/embeddings"
    payload = json.dumps({
        "model": "baai/bge-m3",
        "input": [text.replace('\x00', '')]
    }).encode("utf-8")
    headers = {
        'Authorization': f'Bearer {OPENROUTER_KEY}',
        'Content-Type': 'application/json'
    }
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                return data["data"][0]["embedding"]
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                raise e

def ingest_cases():
    seed_file = os.path.join(os.path.dirname(__file__), 'seed_25_cases.json')
    if not os.path.exists(seed_file):
        seed_file = 'pipeline/seed_25_cases.json'
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    print(f"🚀 Starting ingestion of {len(cases)} landmark Supreme Court & DLR cases into NEW project...")
    
    for i, c in enumerate(cases):
        case_id = c.get('case_id')
        case_title = c.get('case_title')
        citation = c.get('citation')
        ratio = c.get('ratio_decidendi', '')
        
        # Construct rich text representation for embedding
        statutes_str = ", ".join([f"{s.get('act_name')} Sec {', '.join(s.get('sections', []))}" for s in c.get('governing_statutes', [])])
        embed_text = f"Case: {case_title}. Citation: {citation}. Court: {c.get('court_division')}. Subject: {c.get('subject_area')}. Governing Statutes: {statutes_str}. Ratio Decidendi: {ratio}"
        
        print(f"[{i+1}/{len(cases)}] Embedding & Ingesting: {citation} — {case_title[:40]}...")
        vec = get_bge_embedding(embed_text)
        
        record = {
            "case_id": case_id,
            "case_title": case_title,
            "citation": citation,
            "court_division": c.get("court_division"),
            "year": c.get("year"),
            "judgment_date": c.get("judgment_date"),
            "bench_judges": c.get("bench_judges", []),
            "subject_area": c.get("subject_area"),
            "governing_statutes": c.get("governing_statutes", []),
            "ratio_decidendi": ratio,
            "exact_key_passages": c.get("exact_key_passages", []),
            "judgment_content": c.get("facts_summary", "") + "\n\n" + ratio,
            "pdf_source_url": c.get("pdf_source_url"),
            "embedding": vec
        }
        
        db_cases.table("case_chunks").upsert(record, on_conflict="case_id").execute()
        time.sleep(0.3)

    print("\n✅ All 25 landmark Supreme Court & DLR cases successfully ingested into the NEW project!")

if __name__ == "__main__":
    ingest_cases()
