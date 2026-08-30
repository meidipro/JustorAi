"""Ingest all new JSON files from knowledge/new/ into Supabase."""
import os, sys, json, time, pathlib, logging, urllib.request, urllib.error
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'backend'))
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
db = create_client(SUPA_URL, SUPA_KEY)

EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:batchEmbedContents?key={GEMINI_API_KEY}"

def batch_embed(texts, retries=7):
    requests_payload = [
        {
            "model": "models/gemini-embedding-2",
            "outputDimensionality": 768,
            "content": {"parts": [{"text": t.replace('\x00', '')}]}
        }
        for t in texts
    ]
    payload = json.dumps({"requests": requests_payload}).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(EMBED_URL, data=payload, method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                return [e["values"] for e in data["embeddings"]]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (2 ** attempt) + 3
                print(f"\n  [Rate Limit] Waiting {wait}s...", end="", flush=True)
                time.sleep(wait)
            else:
                raise
    raise Exception("Embedding failed after all retries")

def compute_status_rank(s):
    s = str(s).lower()
    if s == "active": return 3
    if s == "amended": return 3  # amended = still current law
    return 1

def ingest_file(fpath):
    data = json.loads(pathlib.Path(fpath).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        logger.warning(f"  {fpath}: empty or not a list, skipping")
        return 0

    title = data[0].get("Act_Name", "Unknown")
    logger.info(f"Ingesting '{title}' ({len(data)} sections)...")

    doc_resp = db.table("documents").insert({
        "title": title,
        "content": f"Structured Act data for {title}.",
        "metadata": {"source": pathlib.Path(fpath).name, "type": "Act"}
    }).execute()
    document_id = doc_resp.data[0]["id"]

    BATCH = 20
    total = 0
    for i in range(0, len(data), BATCH):
        batch = data[i:i+BATCH]
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
        print(f"\r  Stored {total}/{len(data)}...", end="", flush=True)
        time.sleep(10)

    print(f"\r  Done: {total} chunks for '{title}'          ")
    return total

# Ingest ALL files from knowledge/new/
knowledge_new = pathlib.Path("knowledge/new")
grand_total = 0
files = sorted(knowledge_new.glob("*.json"))
print(f"Found {len(files)} JSON files in knowledge/new/\n")

for fpath in files:
    try:
        n = ingest_file(fpath)
        grand_total += n
    except Exception as e:
        logger.error(f"FAILED {fpath.name}: {e}")

print(f"\n=== Done. Total chunks ingested: {grand_total} ===")
