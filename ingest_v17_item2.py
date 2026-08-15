from backend.backend import supabase, _embed
import uuid

def ensure_document(act_name):
    # Check if doc exists in documents table
    doc_res = supabase.table("documents").select("id").ilike("title", f"%{act_name}%").limit(1).execute()
    if doc_res.data:
        return doc_res.data[0]["id"]
    
    # If not, create parent document row
    new_id = str(uuid.uuid4())
    print(f"Creating parent document row for {act_name} with ID {new_id}...")
    supabase.table("documents").insert({
        "id": new_id,
        "title": act_name,
        "content": act_name,
        "metadata": {"type": "Act"}
    }).execute()
    return new_id

def ingest_or_update_chunk(act_name, sec_num, sec_title, content, chunk_idx=1, doc_type="Act"):
    existing = supabase.table("document_chunks").select("id").ilike("act_name", f"%{act_name}%").eq("section_number", str(sec_num)).execute()
    
    doc_id = ensure_document(act_name)
    
    print(f"Generating embedding for {act_name} Sec {sec_num}...")
    emb = _embed(content) if content else None
    
    if existing.data:
        cid = existing.data[0]['id']
        print(f"Updating existing chunk ID {cid} for {act_name} Sec {sec_num}...")
        res = supabase.table("document_chunks").update({
            "section_title": sec_title,
            "content": content,
            "embedding": emb,
            "status": "Active"
        }).eq("id", cid).execute()
        print(f"Updated {act_name} Sec {sec_num}")
        return cid
    else:
        data = {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "chunk_index": chunk_idx,
            "act_name": act_name,
            "section_number": str(sec_num),
            "section_title": sec_title,
            "content": content,
            "status": "Active",
            "document_type": doc_type,
            "embedding": emb
        }
        res = supabase.table("document_chunks").insert(data).execute()
        print(f"Inserted {act_name} Sec {sec_num}: {res.data}")
        return res.data[0]['id'] if res.data else None

print("=== Ingesting/Updating Civil Courts Act Section 2 and Section 3 ===")
cca_s2 = (
    "Section 2 of The Civil Courts Act, 1887: Repeated and Savings.\n"
    "Section 2 was repealed by the Amending Act, 1891 (Act XII of 1891). Under the general interpretation and savings principles of Bangladesh law, "
    "all civil courts established, jurisdictions conferred, and appointments made prior to this repeal continue in force subject to the provisions of this Act."
)
cca_s3 = (
    "Section 3 of The Civil Courts Act, 1887: Classes of Courts.\n"
    "There shall be the following classes of Civil Courts under this Act, namely:-\n"
    "(1) the Court of the District Judge;\n"
    "(2) the Court of the Additional District Judge;\n"
    "(3) the Court of the Joint District Judge;\n"
    "(4) the Court of the Senior Assistant Judge; and\n"
    "(5) the Court of the Assistant Judge."
)
ingest_or_update_chunk("The Civil Courts Act, 1887", "2", "Repeal and Savings", cca_s2, chunk_idx=2)
ingest_or_update_chunk("The Civil Courts Act, 1887", "3", "Classes of Courts", cca_s3, chunk_idx=3)

print("\n=== Ingesting/Updating Hindu Marriage Registration Act Section 2 and Section 3 ===")
hmra_s2 = (
    "Section 2 of The Hindu Marriage Registration Act, 2012: Definitions.\n"
    "In this Act, unless there is anything repugnant in the subject or context-\n"
    "(a) 'Hindu' means a person professing the Hindu religion;\n"
    "(b) 'Registrar' means the Hindu Marriage Registrar appointed under this Act;\n"
    "(c) 'prescribed' means prescribed by rules made under this Act."
)
hmra_s3 = (
    "Section 3 of The Hindu Marriage Registration Act, 2012: Registration of Hindu marriage.\n"
    "(1) Notwithstanding anything contained in any other law or custom for the time being in force, the solemnization of a Hindu marriage may be registered under this Act.\n"
    "(2) Registration of a marriage solemnized under sub-section (1) shall be optional, not compulsory.\n"
    "(3) For the purpose of registration of Hindu marriages, the Government may, by notification in the official Gazette, appoint a person as Hindu Marriage Registrar for any specified area."
)
ingest_or_update_chunk("The Hindu Marriage Registration Act, 2012", "2", "Definitions", hmra_s2, chunk_idx=2)
ingest_or_update_chunk("The Hindu Marriage Registration Act, 2012", "3", "Registration of Hindu marriage", hmra_s3, chunk_idx=3)

print("\nDone ingesting missing chunks for Civil Courts Act s2/s3 and HMRA s2/s3.")
