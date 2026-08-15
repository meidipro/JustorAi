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

def ingest_act(fpath, data):
    title = clean_val(data[0].get("Act_Name") or data[0].get("title", "Unknown Act"))
    delete_existing(title)
    logger.info(f"Ingesting Act '{title}' ({len(data)} items) from {fpath.name}...")
    
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
        print(f"\r  Stored {total}/{len(data)}...", end="", flush=True)
    print(f"\r  Done: {total} Act chunks for '{title}'          ")
    return total

def ingest_dlr(fpath, data):
    title = f"DLR Case Collection ({fpath.name})"
    delete_existing(title)
    logger.info(f"Ingesting DLR Collection ({len(data)} cases) from {fpath.name}...")
    
    doc_resp = db.table("documents").insert({
        "title": title,
        "content": f"Structured DLR Case Law Collection from {fpath.name}.",
        "metadata": {"source": fpath.name, "type": "DLR"}
    }).execute()
    document_id = doc_resp.data[0]["id"]
    
    BATCH_SIZE = 100
    total = 0
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i+BATCH_SIZE]
        texts = []
        for e in batch:
            c_title = clean_val(e.get("Case_Title", ""))
            court = clean_val(e.get("Court_Division", ""))
            yr = clean_val(str(e.get("Year", "")))
            subj = clean_val(e.get("Subject_Law", ""))
            ratio = clean_val(e.get("Ratio_Decidendi", ""))
            texts.append(f"Case: {c_title} ({court}, {yr}). Subject Law: {subj}. Held: {ratio}")
            
        vectors = batch_embed(texts)
        records = []
        for j, entry in enumerate(batch):
            ratio = clean_val(entry.get("Ratio_Decidendi", ""))
            content_display = ratio if ratio else clean_val(entry.get("Judgment_Content", ""))
            records.append({
                "document_id": document_id,
                "content": content_display,
                "embedding": vectors[j],
                "chunk_index": i + j,
                "document_type": "DLR",
                "jurisdiction": "Bangladesh",
                "status_rank": 3,
                "case_title": clean_val(entry.get("Case_Title", "")),
                "court_division": clean_val(entry.get("Court_Division", "")),
                "year": clean_val(str(entry.get("Year", ""))),
                "subject_law": clean_val(entry.get("Subject_Law", "")),
                "ratio_decidendi": ratio,
                "judgment_content": clean_val(entry.get("Judgment_Content", "")),
            })
        db.table("document_chunks").insert(records).execute()
        total += len(batch)
        print(f"\r  Stored {total}/{len(data)}...", end="", flush=True)
    print(f"\r  Done: {total} DLR chunks from {fpath.name}          ")
    return total

def main():
    target_dir = pathlib.Path("knowledge/new json")
    if not target_dir.exists():
        print(f"Directory {target_dir} does not exist!")
        return
        
    files = sorted(target_dir.glob("*.json"))
    print(f"Found {len(files)} JSON files in '{target_dir}'.\n")
    
    total_chunks = 0
    for fpath in files:
        data = json.loads(fpath.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not data:
            continue
        first = data[0]
        if first.get("document_type") == "DLR" or "Case_Title" in first:
            n = ingest_dlr(fpath, data)
        else:
            n = ingest_act(fpath, data)
        total_chunks += n
        
    print(f"\n=== Successfully ingested {total_chunks} total chunks from '{target_dir}' ===")

if __name__ == "__main__":
    main()
