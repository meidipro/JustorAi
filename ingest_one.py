"""
Conservative one-at-a-time ingestion with heavy rate limit protection.
Run this once per file to stay under Gemini embedding quota.
Usage: python ingest_one.py <filename_in_knowledge_new>
"""
import os, sys, json, time, pathlib, logging, urllib.request, urllib.error
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'backend'))
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
db = create_client(SUPA_URL, SUPA_KEY)

EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
EMBED_MODEL = "baai/bge-m3"

BATCH_SIZE = 100     # OpenRouter handles larger batches fine
BATCH_DELAY = 1      # Minimal delay needed

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
                print(f"\n  [Rate Limit 429] Waiting {wait}s...", end="", flush=True)
                time.sleep(wait)
            else:
                body = e.read().decode('utf-8', errors='replace')
                raise Exception(f"HTTP {e.code}: {body[:200]}")
        except Exception as e:
            if attempt < retries - 1:
                wait = min((2 ** attempt) * 2 + 2, 60)
                print(f"\n  [Error] {e}. Waiting {wait}s...", end="", flush=True)
                time.sleep(wait)
            else:
                raise
    raise Exception("Embedding failed after all retries")

def compute_status_rank(s):
    return 3 if str(s).lower() in ("active", "amended") else 1

def delete_existing(title):
    existing = db.table("documents").select("id").eq("title", title).execute()
    for doc in existing.data:
        db.table("documents").delete().eq("id", doc["id"]).execute()
        logger.info(f"  Deleted existing: {title}")

def ingest_file(fpath):
    data = json.loads(pathlib.Path(fpath).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        logger.warning("Empty or not a list, skipping")
        return 0

    title = data[0].get("Act_Name", "Unknown")
    delete_existing(title)

    logger.info(f"Ingesting '{title}' ({len(data)} sections)...")
    doc_resp = db.table("documents").insert({
        "title": title,
        "content": f"Structured Act data for {title}.",
        "metadata": {"source": pathlib.Path(fpath).name, "type": "Act"}
    }).execute()
    document_id = doc_resp.data[0]["id"]

    total = 0
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i+BATCH_SIZE]
        texts = [
            f"{e.get('Act_Name','')} Section {e.get('Section_Number','')}: "
            f"{e.get('Section_Title','')} - {e.get('Content','')}"
            for e in batch
        ]
        vectors = batch_embed(texts)
        records = []
        for j, entry in enumerate(batch):
            records.append({
                "document_id": document_id,
                "content": entry.get("Content", ""),
                "embedding": vectors[j],
                "chunk_index": i + j,
                "document_type": "Act",
                "jurisdiction": entry.get("Jurisdiction", "Bangladesh"),
                "status_rank": compute_status_rank(entry.get("Status", "Active")),
                "act_name": entry.get("Act_Name"),
                "section_number": str(entry.get("Section_Number", "")),
                "section_title": entry.get("Section_Title"),
                "status": entry.get("Status", "Active"),
                "repealed_clauses": entry.get("Repealed_Clauses") or [],
                "amendment_notes": entry.get("Amendment_Notes") or [],
            })
        db.table("document_chunks").insert(records).execute()
        total += len(batch)
        pct = total * 100 // len(data)
        print(f"\r  [{pct:3d}%] Stored {total}/{len(data)}...", end="", flush=True)
        if i + BATCH_SIZE < len(data):
            time.sleep(BATCH_DELAY)

    print(f"\r  [100%] Done: {total} chunks for '{title}'          ")
    return total

# Determine file to process
if len(sys.argv) < 2:
    print("Usage: python ingest_one.py <filename>")
    print("Available files:")
    for f in sorted(pathlib.Path("knowledge/new").glob("*.json")):
        print(f"  {f.name}")
    sys.exit(1)

fname = sys.argv[1]
fpath = pathlib.Path("knowledge/new") / fname
if not fpath.exists():
    logger.error(f"File not found: {fpath}")
    sys.exit(1)

try:
    n = ingest_file(fpath)
    print(f"\n=== Successfully ingested {n} chunks from {fname} ===")
except Exception as e:
    logger.error(f"FAILED: {e}")
    sys.exit(1)
