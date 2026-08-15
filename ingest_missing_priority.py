import os, json, uuid
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
from openai import OpenAI

url = os.environ.get("VITE_SUPABASE_URL", "").strip()
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(url, key)

or_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=or_key)

with open("missing_priority_sections.json", "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    act = item['act_name']
    # Check if doc exists in documents table
    doc_res = db.table("documents").select("id").eq("title", act).execute()
    if doc_res.data:
        doc_id = doc_res.data[0]["id"]
    else:
        # Insert document record
        doc_ins = db.table("documents").insert({
            "title": act
        }).execute()
        doc_id = doc_ins.data[0]["id"]

    text = f"{item['act_name']} Section {item['section_number']}: {item['section_title']}\n{item['content']}"
    resp = client.embeddings.create(
        model="baai/bge-m3",
        input=text,
        encoding_format="float"
    )
    vec = resp.data[0].embedding
    assert len(vec) == 1024

    existing = db.table("document_chunks").select("id").eq("act_name", item['act_name']).eq("section_number", item['section_number']).execute()
    row = {
        "document_id": doc_id,
        "document_type": item["document_type"],
        "act_name": item["act_name"],
        "section_number": item["section_number"],
        "section_title": item["section_title"],
        "status": item["status"],
        "jurisdiction": item["jurisdiction"],
        "content": item["content"],
        "chunk_index": 1,
        "embedding": vec
    }
    if existing.data:
        db.table("document_chunks").update(row).eq("id", existing.data[0]["id"]).execute()
        print(f"Updated: {act} Sec {item['section_number']}")
    else:
        db.table("document_chunks").insert(row).execute()
        print(f"Inserted: {act} Sec {item['section_number']}")
