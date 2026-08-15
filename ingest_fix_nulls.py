import os, sys, json, time, pathlib, logging, urllib.request, urllib.error
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'backend'))
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
from ingest_all_bge import batch_embed, compute_status_rank, delete_existing, db

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def clean_val(v):
    if isinstance(v, str):
        return v.replace('\x00', '').replace('\u0000', '')
    if isinstance(v, list):
        return [clean_val(x) for x in v]
    if isinstance(v, dict):
        return {k: clean_val(val) for k, val in v.items()}
    return v

def ingest_file_clean(fpath):
    data = json.loads(pathlib.Path(fpath).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        return 0
    title = clean_val(data[0].get("Act_Name", "Unknown"))
    delete_existing(title)
    logger.info(f"Ingesting clean '{title}' ({len(data)} sections) from {fpath.name}...")
    doc_resp = db.table("documents").insert({
        "title": title,
        "content": f"Structured Act data for {title}.",
        "metadata": {"source": fpath.name, "type": "Act"}
    }).execute()
    document_id = doc_resp.data[0]["id"]
    BATCH_SIZE = 100
    total = 0
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i+BATCH_SIZE]
        texts = [
            f"{clean_val(e.get('Act_Name',''))} Section {clean_val(e.get('Section_Number',''))}: "
            f"{clean_val(e.get('Section_Title',''))} - {clean_val(e.get('Content',''))}"
            for e in batch
        ]
        vectors = batch_embed(texts)
        records = []
        for j, entry in enumerate(batch):
            records.append({
                "document_id": document_id,
                "content": clean_val(entry.get("Content", "")),
                "embedding": vectors[j],
                "chunk_index": i + j,
                "document_type": "Act",
                "jurisdiction": clean_val(entry.get("Jurisdiction", "Bangladesh")),
                "status_rank": compute_status_rank(entry.get("Status", "Active")),
                "act_name": clean_val(entry.get("Act_Name")),
                "section_number": str(clean_val(entry.get("Section_Number", ""))),
                "section_title": clean_val(entry.get("Section_Title")),
                "status": clean_val(entry.get("Status", "Active")),
                "repealed_clauses": clean_val(entry.get("Repealed_Clauses") or []),
                "amendment_notes": clean_val(entry.get("Amendment_Notes") or []),
            })
        db.table("document_chunks").insert(records).execute()
        total += len(batch)
        print(f"\r  Stored {total}/{len(data)}...", end="", flush=True)
    print(f"\r  Done: {total} chunks for '{title}'          ")
    return total

def main():
    targets = [
        pathlib.Path("knowledge/Stamp_Act_1899_structured_corrected.json"),
        pathlib.Path("knowledge/Transfer_of_Property_Act_1882_structured_corrected.json")
    ]
    total = 0
    for t in targets:
        n = ingest_file_clean(t)
        total += n
    print(f"\n=== Successfully ingested {total} chunks for the final 2 Acts ===")

if __name__ == "__main__":
    main()
