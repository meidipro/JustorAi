import os
import sys
import json
import time
import pathlib
import logging
import sqlite3
import argparse
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Ensure backend path is in sys.path
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'backend'))
load_dotenv('.env')

from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("IngestScrappedLaws")

# Supabase and Embedding Config
SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

if not SUPA_URL or not SUPA_KEY:
    raise ValueError("VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")

db = create_client(SUPA_URL, SUPA_KEY)

EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
EMBED_MODEL = "baai/bge-m3"
BATCH_SIZE = 40
DB_TRACKER_PATH = pathlib.Path(__file__).parent / "ingestion_checkpoint.db"

def init_checkpoint_db():
    with sqlite3.connect(DB_TRACKER_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingested_files (
                filepath TEXT PRIMARY KEY,
                act_title TEXT,
                chunks_count INTEGER,
                ingested_at REAL
            )
        """)
        conn.commit()

def is_already_ingested(filepath: str) -> bool:
    fname = pathlib.Path(filepath).name
    with sqlite3.connect(DB_TRACKER_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM ingested_files WHERE filepath = ? OR filepath LIKE ?", (str(filepath), f"%{fname}"))
        return cursor.fetchone() is not None

def mark_ingested(filepath: str, act_title: str, chunks_count: int):
    with sqlite3.connect(DB_TRACKER_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO ingested_files (filepath, act_title, chunks_count, ingested_at)
            VALUES (?, ?, ?, ?)
        """, (str(filepath), act_title, chunks_count, time.time()))
        conn.commit()

def clean_val(v):
    if isinstance(v, str):
        return v.replace('\x00', '').replace('\u0000', '')
    if isinstance(v, list):
        return [clean_val(x) for x in v]
    if isinstance(v, dict):
        return {k: clean_val(val) for k, val in v.items()}
    return v

def batch_embed(texts, retries=10):
    payload = json.dumps({
        "model": EMBED_MODEL,
        "input": [t.replace('\x00', '') for t in texts]
    }).encode("utf-8")
    
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(EMBED_URL, data=payload, method="POST", headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                return [e["embedding"] for e in data["data"]]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = min((2 ** attempt) * 2 + 2, 60)
                logger.warning(f"[Rate Limit 429] Waiting {wait}s...")
                time.sleep(wait)
            else:
                body = e.read().decode('utf-8', errors='replace')
                raise Exception(f"HTTP {e.code}: {body[:200]}")
        except Exception as e:
            if attempt < retries - 1:
                wait = min((2 ** attempt) * 2 + 2, 60)
                logger.warning(f"[Error] {e}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Embedding failed after all retries")

def compute_status_rank(s):
    return 3 if str(s).lower() in ("active", "amended") else 1

def delete_existing(title):
    existing = db.table("documents").select("id").eq("title", title).execute()
    for doc in existing.data:
        db.table("document_chunks").delete().eq("document_id", doc["id"]).execute()
        db.table("documents").delete().eq("id", doc["id"]).execute()

def ingest_act(fpath: pathlib.Path, data: list):
    title = clean_val(data[0].get("Act_Name") or data[0].get("title") or fpath.stem)
    delete_existing(title)
    
    doc_resp = db.table("documents").insert({
        "title": title,
        "content": f"Structured Act data for {title}.",
        "metadata": {"source": fpath.name, "type": "Act"}
    }).execute()
    document_id = doc_resp.data[0]["id"]
    
    total = 0
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i+BATCH_SIZE]
        texts = []
        for e in batch:
            act_name = clean_val(e.get("Act_Name", title))
            sec_num = clean_val(str(e.get("Section_Number") or e.get("Article_Number") or ""))
            sec_title = clean_val(e.get("Section_Title") or e.get("Article_Title") or "")
            content = clean_val(e.get("Content", ""))
            texts.append(f"{act_name} Section/Article {sec_num}: {sec_title} - {content}")
            
        vectors = batch_embed(texts)
        records = []
        for j, entry in enumerate(batch):
            sec_num = clean_val(str(entry.get("Section_Number") or entry.get("Article_Number") or ""))
            sec_title = clean_val(entry.get("Section_Title") or entry.get("Article_Title") or "")
            records.append({
                "document_id": document_id,
                "content": clean_val(entry.get("Content", "")),
                "embedding": vectors[j],
                "chunk_index": i + j,
                "document_type": "Act",
                "jurisdiction": clean_val(entry.get("Jurisdiction", "Bangladesh")),
                "status_rank": compute_status_rank(entry.get("Status", "Active")),
                "act_name": clean_val(entry.get("Act_Name", title)),
                "section_number": sec_num,
                "section_title": sec_title,
                "status": clean_val(entry.get("Status", "Active")),
                "repealed_clauses": clean_val(entry.get("Repealed_Clauses") or []),
                "amendment_notes": clean_val(entry.get("Amendment_Notes") or []),
            })
        db.table("document_chunks").insert(records).execute()
        total += len(batch)

    mark_ingested(fpath, title, total)
    logger.info(f"Successfully ingested Act '{title}' ({total} chunks) from {fpath.name}")
    return total

def ingest_dlr(fpath: pathlib.Path, data: list):
    title = f"DLR Case Collection ({fpath.name})"
    delete_existing(title)
    
    doc_resp = db.table("documents").insert({
        "title": title,
        "content": f"Structured DLR Case Law Collection from {fpath.name}.",
        "metadata": {"source": fpath.name, "type": "DLR"}
    }).execute()
    document_id = doc_resp.data[0]["id"]
    
    total = 0
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i+BATCH_SIZE]
        texts = []
        for e in batch:
            c_title = clean_val(e.get("Case_Title") or e.get("Citation") or "")
            court = clean_val(e.get("Court_Division") or e.get("Court") or "")
            yr = clean_val(str(e.get("Year", "")))
            subj = clean_val(e.get("Subject_Law", ""))
            ratio = clean_val(e.get("Ratio_Decidendi", ""))
            texts.append(f"Case: {c_title} ({court}, {yr}). Subject Law: {subj}. Held: {ratio}")
            
        vectors = batch_embed(texts)
        records = []
        for j, entry in enumerate(batch):
            ratio = clean_val(entry.get("Ratio_Decidendi", ""))
            content_display = ratio if ratio else clean_val(entry.get("Content") or entry.get("Judgment_Content") or "")
            records.append({
                "document_id": document_id,
                "content": content_display,
                "embedding": vectors[j],
                "chunk_index": i + j,
                "document_type": "DLR",
                "jurisdiction": "Bangladesh",
                "status_rank": 3,
                "case_title": clean_val(entry.get("Case_Title") or entry.get("Citation") or ""),
                "court_division": clean_val(entry.get("Court_Division") or entry.get("Court") or ""),
                "year": clean_val(str(entry.get("Year", ""))),
                "subject_law": clean_val(entry.get("Subject_Law", "")),
                "ratio_decidendi": ratio,
                "judgment_content": clean_val(entry.get("Content") or entry.get("Judgment_Content") or ""),
            })
        db.table("document_chunks").insert(records).execute()
        total += len(batch)

    mark_ingested(fpath, title, total)
    logger.info(f"Successfully ingested DLR Collection '{title}' ({total} chunks) from {fpath.name}")
    return total

def main():
    parser = argparse.ArgumentParser(description="Ingest Scrapped Legal JSON Files into Supabase Vector DB")
    parser.add_argument("--dir", type=str, default="d:/Justor AI/JustorAi/scrapped laws/scrapped laws/Scrap BDLAW Json", help="Target directory containing JSON files")
    parser.add_argument("--limit", type=int, default=None, help="Limit total files to ingest")
    parser.add_argument("--force", action="store_true", help="Re-ingest files even if previously checkpointed")
    args = parser.parse_args()

    init_checkpoint_db()

    target_dir = pathlib.Path(args.dir)
    if not target_dir.exists():
        logger.error(f"Target directory {target_dir} does not exist!")
        return

    json_files = sorted(target_dir.glob("*.json"))
    logger.info(f"Found total {len(json_files)} JSON files in '{target_dir}'.")

    if args.limit:
        json_files = json_files[:args.limit]

    total_chunks = 0
    processed_files = 0
    skipped_files = 0

    for idx, fpath in enumerate(json_files, 1):
        if not args.force and is_already_ingested(fpath):
            skipped_files += 1
            continue

        try:
            raw_text = fpath.read_text(encoding="utf-8", errors="ignore")
            data = json.loads(raw_text)
            if not isinstance(data, list) or not data:
                continue

            first = data[0]
            if first.get("Document_Type") == "CaseLaw" or first.get("document_type") == "DLR" or "Case_Title" in first:
                n = ingest_dlr(fpath, data)
            else:
                n = ingest_act(fpath, data)

            total_chunks += n
            processed_files += 1
            logger.info(f"Progress: [{idx}/{len(json_files)}] Total Chunks: {total_chunks}")
        except Exception as e:
            logger.error(f"Failed to ingest file {fpath.name}: {e}")

    logger.info(f"=== INGESTION COMPLETED ===")
    logger.info(f"Processed: {processed_files} files | Skipped (Already Ingested): {skipped_files} | Total Chunks Created: {total_chunks}")

if __name__ == "__main__":
    main()
