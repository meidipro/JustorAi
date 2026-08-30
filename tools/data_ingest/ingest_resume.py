"""Resume ingestion: delete partial CrPC entry and re-ingest all failed files."""
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

# Files that failed — need to (re-)ingest
RESUME_FILES = [
    "code_of_criminal_procedure_1898_structured.json",  # partial - will delete first
    "contract_act_1872_sections.json",
    "evidence_act_1872_sections.json",
    "hindu_law_inheritance_amendment_1929_sections.json",
    "hindu_married_womens_right_1946_sections.json",
    "ICT_Act_2006_Bangladesh.json",
    "limitation_act_1908_sections.json",
    "NI_act_1881_sections.json",
    "pdr_1913_sections.json",
]

def batch_embed(texts, retries=7):
    requests_payload = [
        {"model": "models/gemini-embedding-2", "outputDimensionality": 768,
         "content": {"parts": [{"text": t.replace('\x00', '')}]}}
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
        except Exception as e:
            if attempt < retries - 1:
                wait = (2 ** attempt) + 5
                print(f"\n  [Net Error] {e}. Waiting {wait}s...", end="", flush=True)
                time.sleep(wait)
            else:
                raise
    raise Exception("Embedding failed after all retries")

def compute_status_rank(s):
    s = str(s).lower()
    return 3 if s in ("active", "amended") else 1

def delete_existing(title):
    """Delete any existing document (and its chunks via cascade) with this title."""
    existing = db.table("documents").select("id").eq("title", title).execute()
    for doc in existing.data:
        db.table("documents").delete().eq("id", doc["id"]).execute()
        logger.info(f"  Deleted existing document: {title}")

def ingest_file(fpath):
    data = json.loads(pathlib.Path(fpath).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        logger.warning(f"  {fpath}: empty, skipping")
        return 0

    title = data[0].get("Act_Name", "Unknown")
    
    # Always clean up any partial/old version first
    delete_existing(title)
    
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

knowledge_new = pathlib.Path("knowledge/new")
grand_total = 0
print(f"Resuming {len(RESUME_FILES)} files...\n")

for fname in RESUME_FILES:
    fpath = knowledge_new / fname
    if not fpath.exists():
        logger.warning(f"NOT FOUND: {fname}")
        continue
    try:
        n = ingest_file(fpath)
        grand_total += n
    except Exception as e:
        logger.error(f"FAILED {fname}: {e}")

print(f"\n=== Done. Total chunks ingested this run: {grand_total} ===")
