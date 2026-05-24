"""
JustorAI — Production Ingestion Script (v2)
===========================================
Ingest enterprise-grade structured law data into the updated Supabase schema.
Supports:
- Acts/Statutes with Status and Amendment tracking.
- DLRs/Case Law with Ratio Decidendi.
- Law-Status-Aware Ranking (Active > Amended > Repealed).
"""

import os
import sys
import json
import urllib.request
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ─── Load services ────────────────────────────────────────────────────────────

try:
    from supabase import create_client, Client
    from openai import OpenAI
except ImportError:
    logger.error("Missing dependencies. Run: pip install supabase openai")
    sys.exit(1)

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
).strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing VITE_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    sys.exit(1)

logger.info("Connecting to Supabase...")
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in .env")
    sys.exit(1)

logger.info("Initializing Gemini client for embeddings (native REST API)...")
logger.info("Ready.\n")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def compute_status_rank(status_str: str) -> int:
    """Active=3, Amended=2, Repealed/Other=1."""
    s = str(status_str).lower()
    if s == "active": return 3
    if s == "amended": return 2
    if s in ["repealed", "omitted", "deleted"]: return 1
    return 1


def batch_embed(texts: List[str], retries: int = 7) -> List[List[float]]:
    import time
    import urllib.error
    """Generate 768-dim vectors for a batch of texts."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:batchEmbedContents?key={GEMINI_API_KEY}"
    
    requests = []
    for text in texts:
        clean_text = text.replace('\x00', '').replace('\u0000', '')
        requests.append({
            "model": "models/gemini-embedding-2",
            "outputDimensionality": 768,
            "content": {"parts": [{"text": clean_text}]}
        })
        
    payload = {"requests": requests}
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                return [emb["values"] for emb in resp_data["embeddings"]]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = (2 ** attempt) + 3 # Exponential backoff
                print(f"\n    [Rate Limit] Waiting {wait_time}s before batch retry...", end="", flush=True)
                time.sleep(wait_time)
            else:
                raise e
                
    raise Exception(f"Failed to batch embed after {retries} retries due to rate limits.")


def parse_enterprise_json(path: Path) -> List[Dict[str, Any]]:
    """Parse enterprise JSON schema files."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        logger.warning(f"File {path.name} is not a JSON list. Skipping.")
        return []

    processed = []
    for entry in data:
        if not isinstance(entry, dict): continue

        doc_type = entry.get("Document_Type", "Act") # Default to Act
        if "Act_Name" in entry: doc_type = "Act"
        if "Case_Title" in entry: doc_type = "DLR"

        if doc_type == "Act":
            processed.append({
                "document_type": "Act",
                "act_name": entry.get("Act_Name", ""),
                "section_number": str(entry.get("Section_Number", "")),
                "section_title": entry.get("Section_Title", ""),
                "status": entry.get("Status", "Active"),
                "jurisdiction": entry.get("Jurisdiction", "Bangladesh"),
                "content": entry.get("Content", ""),
                "repealed_clauses": entry.get("Repealed_Clauses", []),
                "amendment_notes": entry.get("Amendment_Notes", []),
                "status_rank": compute_status_rank(entry.get("Status", "Active"))
            })
        elif doc_type == "DLR" or "Case Law" in doc_type:
            processed.append({
                "document_type": "DLR",
                "case_title": entry.get("Case_Title", ""),
                "court_division": entry.get("Court_Division", ""),
                "year": str(entry.get("Year", "")),
                "subject_law": entry.get("Subject_Law", ""),
                "ratio_decidendi": entry.get("Ratio_Decidendi", ""),
                "judgment_content": entry.get("Judgment_Content", ""),
                "jurisdiction": "Bangladesh",
                "status_rank": 3 # DLRs are active knowledge
            })
    
    return processed


def ingest_v2(entries: List[Dict[str, Any]], filename: str, replace: bool = False) -> int:
    """Store entries into the expanded document_chunks table."""
    if not entries: return 0

    # Group by Document/Act Title
    groups: Dict[str, List[Dict]] = {}
    for e in entries:
        title = e.get("act_name") or e.get("case_title") or "Unknown"
        groups.setdefault(title, []).append(e)

    total_stored = 0

    for title, doc_entries in groups.items():
        logger.info(f"  Ingesting '{title}' ({len(doc_entries)} chunks)")

        # 1. Ensure Document ID
        # Delete if replace mode
        if replace:
            existing = db.table("documents").select("id").eq("title", title).execute()
            for old in existing.data:
                db.table("documents").delete().eq("id", old["id"]).execute()
        
        doc_resp = db.table("documents").insert({
            "title": title,
            "content": f"Structured {doc_entries[0]['document_type']} data for {title}.",
            "metadata": {"source": filename, "type": doc_entries[0]["document_type"]}
        }).execute()
        document_id = doc_resp.data[0]["id"]

        # 2. Batch Process Chunks (Up to 100 per API Call)
        BATCH_SIZE = 100
        total_batches = (len(doc_entries) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(doc_entries))
            batch_entries = doc_entries[start_idx:end_idx]
            
            # Prepare texts for embedding
            batch_texts = []
            for entry in batch_entries:
                if entry["document_type"] == "Act":
                    text = f"{entry['act_name']} Section {entry['section_number']}: {entry['section_title']} - {entry['content']}"
                else:
                    text = f"Case: {entry['case_title']} ({entry['year']}) Division: {entry['court_division']} Subject: {entry['subject_law']} Ratio: {entry['ratio_decidendi']}"
                batch_texts.append(text)
                
            # Get embeddings in ONE single API call!
            batch_vectors = batch_embed(batch_texts)
            
            # Prepare DB records
            records = []
            for j, entry in enumerate(batch_entries):
                record = {
                    "document_id": document_id,
                    "content": entry.get("content") or entry.get("judgment_content") or "",
                    "embedding": batch_vectors[j],
                    "chunk_index": start_idx + j,
                    "document_type": entry["document_type"],
                    "jurisdiction": entry.get("jurisdiction", "Bangladesh"),
                    "status_rank": entry.get("status_rank", 1),
                    
                    "act_name": entry.get("act_name"),
                    "section_number": entry.get("section_number"),
                    "section_title": entry.get("section_title"),
                    "status": entry.get("status"),
                    "repealed_clauses": entry.get("repealed_clauses"),
                    "amendment_notes": entry.get("amendment_notes"),
                    
                    "case_title": entry.get("case_title"),
                    "court_division": entry.get("court_division"),
                    "year": entry.get("year"),
                    "subject_law": entry.get("subject_law"),
                    "ratio_decidendi": entry.get("ratio_decidendi"),
                    "judgment_content": entry.get("judgment_content")
                }
                records.append(record)
                
            db.table("document_chunks").insert(records).execute()
            print(f"\r    Embedded and Stored {end_idx}/{len(doc_entries)}...", end="", flush=True)
        
        print(f"\r    Stored {len(doc_entries)} chunks for '{title}'.          ")
        total_stored += len(doc_entries)

    return total_stored


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="JustorAI Production Ingestion - v2 Structured Mode")
    parser.add_argument("--dir", default="knowledge", help="Directory containing enterprise JSON files")
    parser.add_argument("--replace", action="store_true", help="Overwrite existing entries with same title")
    args = parser.parse_args()

    knowledge_path = Path(args.dir)
    if not knowledge_path.is_dir():
        logger.error(f"Directory not found: {knowledge_path}")
        sys.exit(1)

    json_files = sorted(knowledge_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {knowledge_path}")

    for jf in json_files:
        logger.info(f"Processing {jf.name}...")
        try:
            entries = parse_enterprise_json(jf)
            if entries:
                ingest_v2(entries, jf.name, replace=args.replace)
        except Exception as e:
            logger.error(f"Error processing {jf.name}: {e}")

    logger.info("Ingestion Complete.")

if __name__ == "__main__":
    main()
