import os, uuid
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
from openai import OpenAI

url = os.environ.get("VITE_SUPABASE_URL", "").strip()
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
db = create_client(url, key)

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from backend import _embed

act_name = "The Code of Criminal Procedure, 1898"
section_number = "498"
section_title = "Power to direct admission to bail or reduction of bail (Anticipatory Bail / Agam Jamin)"
chunk_text = """Section 498 of The Code of Criminal Procedure, 1898 provides:
Power to direct admission to bail or reduction of bail:
The amount of every bond executed under this Chapter shall be fixed with due regard to the circumstances of the case, and shall not be excessive; and the High Court Division or Court of Session may, in any case, whether there be an appeal on conviction or not, direct that any person be admitted to bail, or that the bail required by a police-officer or Magistrate be reduced.

Anticipatory Bail (Agam Jamin):
In Bangladesh, Section 438 CrPC was omitted by the Code of Criminal Procedure (Amendment) Act, 2009. Anticipatory bail (pre-arrest bail) is exercised by the High Court Division and Court of Session under the inherent and discretionary jurisdiction of Section 498 of the Code of Criminal Procedure, 1898. Under Section 498 CrPC, a person apprehending arrest may be granted anticipatory bail for a limited period, directing surrender before the competent lower court."""

# Get embedding via _embed
embedding = _embed(chunk_text)

# Check or create document entry
doc_res = db.table("documents").select("id").eq("title", act_name).execute()
if doc_res.data:
    doc_id = doc_res.data[0]["id"]
else:
    new_doc = db.table("documents").insert({
        "title": act_name,
        "source_type": "STATUTE",
        "jurisdiction": "Bangladesh"
    }).execute()
    doc_id = new_doc.data[0]["id"]

# Remove existing chunk for s498 if any
db.table("document_chunks").delete().eq("act_name", act_name).eq("section_number", section_number).execute()

# Insert new rich chunk
payload = {
    "document_id": doc_id,
    "act_name": act_name,
    "section_number": section_number,
    "section_title": section_title,
    "content": chunk_text,
    "chunk_index": 0,
    "embedding": embedding,
    "status": "Active"
}

ins = db.table("document_chunks").insert(payload).execute()
print("Successfully ingested CrPC Section 498 into document_chunks!")
