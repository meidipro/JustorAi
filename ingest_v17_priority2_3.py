from backend.backend import supabase, _embed
import uuid

def ingest_chunk(act_name, sec_num, sec_title, content, chunk_idx=1, doc_type="Act"):
    # Check existing
    existing = supabase.table("document_chunks").select("id").ilike("act_name", f"%{act_name}%").ilike("section_number", f"{sec_num}").execute()
    if existing.data:
        print(f"Already exists: {act_name} Sec {sec_num} (ID: {existing.data[0]['id']})")
        return existing.data[0]['id']
    
    # Get document_id from another chunk of the same act
    doc_res = supabase.table("document_chunks").select("document_id, chunk_index").ilike("act_name", f"%{act_name}%").limit(1).execute()
    doc_id = doc_res.data[0]["document_id"] if doc_res.data and doc_res.data[0].get("document_id") else str(uuid.uuid4())
    
    # Generate embedding using _embed
    print(f"Generating embedding for {act_name} Sec {sec_num}...")
    emb = _embed(content) if content else None
    
    data = {
        "id": str(uuid.uuid4()),
        "document_id": doc_id,
        "chunk_index": chunk_idx,
        "act_name": act_name,
        "section_number": sec_num,
        "section_title": sec_title,
        "content": content,
        "status": "Active",
        "document_type": doc_type,
        "embedding": emb
    }
    res = supabase.table("document_chunks").insert(data).execute()
    print(f"Inserted {act_name} Sec {sec_num}: {res.data}")
    return res.data[0]['id'] if res.data else None

print("=== Ingesting Civil Courts Act Section 25 ===")
cca_s25 = (
    "Section 25 of The Civil Courts Act, 1887: Power to invest Assistant Judges and Senior Assistant Judges with Small Cause Court jurisdiction.\n"
    "The Government may, by notification in the official Gazette, confer, within such local limits as it thinks fit, upon any Assistant Judge or Senior Assistant Judge, "
    "the jurisdiction of a Judge of a Court of Small Causes under the Small Cause Courts Act, 1887, for the trial of suits, cognizable by such Courts, "
    "up to such value not exceeding twenty-five thousand taka as it thinks fit, and may withdraw any jurisdiction so conferred."
)
ingest_chunk("The Civil Courts Act, 1887", "25", "Power to invest Assistant Judges with Small Cause Court jurisdiction", cca_s25, chunk_idx=25)

print("\n=== Ingesting/Verifying CrPC Section 4(1), 7, 9 ===")
crpc_s4_1 = (
    "Section 4(1) of The Code of Criminal Procedure, 1898: Definitions.\n"
    "In this Code the following words and expressions have the following meanings, unless a different intention appears from the subject or context:\n"
    "(f) 'Cognizable offence' means an offence for which, and 'cognizable case' means a case in which a police-officer, within or without the presidency-towns, may, in accordance with the second schedule or under any other law for the time being in force, arrest without warrant;\n"
    "(n) 'Non-cognizable offence' means an offence for which, and 'non-cognizable case' means a case in which a police-officer, within or without a presidency-town, may not arrest without warrant;\n"
    "(a) 'Advocate' means an advocate entered in any roll under the provisions of the Bangladesh Legal Practitioners and Bar Council Order, 1972;\n"
    "(b) 'Bailable offence' means an offence shown as bailable in the second schedule, or which is made bailable by any other law for the time being in force; and 'non-bailable offence' means any other offence;\n"
    "(m) 'Judicial proceeding' includes any proceeding in the course of which evidence is or may be legally taken on oath."
)
ingest_chunk("The Code of Criminal Procedure, 1898", "4(1)", "Definitions - Cognizable and Non-cognizable offence", crpc_s4_1, chunk_idx=41)

print("\nDone Priority 2 & 3 ingests.")
