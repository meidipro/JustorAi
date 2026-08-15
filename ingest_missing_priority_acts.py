import os
import sys
import json
import uuid
import urllib.request
import urllib.error
import dotenv
from supabase import create_client

dotenv.load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

if not OPENROUTER_API_KEY or not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing required environment variables.")
    sys.exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_embedding(text: str):
    url = "https://openrouter.ai/api/v1/embeddings"
    payload = json.dumps({
        "model": "baai/bge-m3",
        "input": [text.replace('\x00', '')]
    }).encode("utf-8")
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data["data"][0]["embedding"]

CIVIL_COURTS_DOC_ID = "160b8054-da65-4164-b1c1-20d7e9e74c2e"

CHUNKS_TO_INGEST = [
    # ─── THE CIVIL COURTS ACT, 1887 ──────────────────────────────────────────
    {
        "act_name": "The Civil Courts Act, 1887",
        "document_id": CIVIL_COURTS_DOC_ID,
        "section_number": "3",
        "content": """Section 3 of The Civil Courts Act, 1887: Classes of Civil Courts.
Besides the High Court Division, there shall be five classes of Civil Courts established under this Act, namely:
(1) The Court of the District Judge;
(2) The Court of the Additional District Judge;
(3) The Court of the Joint District Judge;
(4) The Court of the Senior Assistant Judge; and
(5) The Court of the Assistant Judge."""
    },
    {
        "act_name": "The Civil Courts Act, 1887",
        "document_id": CIVIL_COURTS_DOC_ID,
        "section_number": "11",
        "content": """Section 11 of The Civil Courts Act, 1887: Administrative control of Courts.
Subject to the general superintendence and control of the High Court Division, the District Judge shall have administrative control over all the Civil Courts under this Act within the local limits of his jurisdiction."""
    },
    {
        "act_name": "The Civil Courts Act, 1887",
        "document_id": CIVIL_COURTS_DOC_ID,
        "section_number": "14",
        "content": """Section 14 of The Civil Courts Act, 1887: Place of sitting of Civil Courts.
(1) The Government may, by notification in the official Gazette, fix and alter the place or places at which any Civil Court under this Act is to be held.
(2) All places at which any such Courts are now held shall be deemed to have been fixed under this section."""
    },
    {
        "act_name": "The Civil Courts Act, 1887",
        "document_id": CIVIL_COURTS_DOC_ID,
        "section_number": "19",
        "content": """Section 19 of The Civil Courts Act, 1887: Pecuniary jurisdiction of Senior Assistant Judges and Assistant Judges.
(1) Save as aforesaid, the jurisdiction of a Senior Assistant Judge extends to all original suits for the period up to the value of twenty-five lac Taka.
(2) Save as aforesaid, the jurisdiction of an Assistant Judge extends to all original suits for the period up to the value of fifteen lac Taka."""
    },
    {
        "act_name": "The Civil Courts Act, 1887",
        "document_id": CIVIL_COURTS_DOC_ID,
        "section_number": "21",
        "content": """Section 21 of The Civil Courts Act, 1887: Appellate jurisdiction of District Judges, Additional District Judges and Joint District Judges.
(1) Save as aforesaid, an appeal from a decree or order of a Joint District Judge shall lie—
(a) to the District Judge where the value of the original suit in which or in any proceeding arising out of which the decree or order was made did not exceed five crore Taka; and
(b) to the High Court Division in any other case.
(2) Save as aforesaid, an appeal from a decree or order of a Senior Assistant Judge or an Assistant Judge shall lie to the District Judge."""
    },

    # ─── THE COURT FEES ACT, 1870 ─────────────────────────────────────────────
    {
        "act_name": "The Court Fees Act, 1870",
        "section_number": "7",
        "content": """Section 7 of The Court Fees Act, 1870: Computation of fees payable in certain suits.
The amount of fee payable under this Act in the suits next hereinafter mentioned shall be computed as follows:
(iv) In suits for a declaratory decree and consequential relief—according to the amount at which the relief sought is valued in the plaint or memorandum of appeal.
(v) In suits for the possession of land, houses and gardens—according to the value of the subject-matter.
In suits under paragraphs v, vi, ix, and x (clause d), the value as determinable for computation of court fees and the value for purposes of jurisdiction under the Suits Valuation Act, 1887, Section 8, shall be the same."""
    },
    {
        "act_name": "The Court Fees Act, 1870",
        "section_number": "13",
        "content": """Section 13 of The Court Fees Act, 1870: Refund of fee paid on memorandum of appeal or plaint rejected or remanded.
If an appeal or plaint is rejected by the lower Court on any of the grounds mentioned in the Code of Civil Procedure, or if it is remanded for trial on the merits, the appellate Court shall order the refund to the appellant or plaintiff of the full amount of fee paid on the memorandum of appeal or plaint."""
    },
    {
        "act_name": "The Court Fees Act, 1870",
        "section_number": "Schedule I",
        "content": """Schedule I of The Court Fees Act, 1870: Ad Valorem Court Fees.
Ad valorem court fees are fees calculated as a proportionate percentage of the value of the subject-matter or monetary claim in dispute. Plaint, written statement pleading a set-off or counterclaim, or memorandum of appeal not otherwise provided for in this Act carry an ad valorem court fee graduated according to the value of the subject matter."""
    },
    {
        "act_name": "The Court Fees Act, 1870",
        "section_number": "Schedule II",
        "content": """Schedule II of The Court Fees Act, 1870: Fixed Court Fees.
Fixed court fees are predetermined, static statutory amounts payable on specific applications, petitions, or suits regardless of the claim's monetary valuation.
In a Partition Suit under the Partition Act, 1893:
- If the plaintiff is in joint physical possession of the property and merely seeks formal separation of shares, a fixed court fee is payable under Schedule II.
- If the plaintiff has been excluded or ousted from possession, an ad valorem court fee is payable on the market value of the share claimed."""
    },
    {
        "act_name": "The Court Fees Act, 1870",
        "section_number": "19",
        "content": """Section 19 of The Court Fees Act, 1870: Exemption of certain documents.
Nothing contained in this Act shall render the following documents chargeable with any fee:
Power-of-attorney to institute or defend a suit when executed by an officer, applications or petitions to public officers for public purposes, and statutory exemptions."""
    }
]

def main():
    print(f"Starting ingestion of {len(CHUNKS_TO_INGEST)} priority chunks...")
    court_fees_doc_id = CIVIL_COURTS_DOC_ID
    
    for idx, item in enumerate(CHUNKS_TO_INGEST, 1):
        act_name = item["act_name"]
        sec_num = item["section_number"]
        content = item["content"]
        doc_id = item.get("document_id", court_fees_doc_id)
        
        print(f"[{idx}/{len(CHUNKS_TO_INGEST)}] Embedding & upserting {act_name} Section {sec_num}...")
        emb = get_embedding(content)
        
        existing = sb.table("document_chunks").select("id").ilike("act_name", act_name).eq("section_number", sec_num).execute()
        if existing.data and len(existing.data) > 0:
            chunk_id = existing.data[0]["id"]
            sb.table("document_chunks").update({
                "content": content,
                "embedding": emb,
                "document_id": doc_id,
                "chunk_index": idx
            }).eq("id", chunk_id).execute()
            print(f"   -> Updated existing chunk ID {chunk_id}")
        else:
            sb.table("document_chunks").insert({
                "document_id": doc_id,
                "chunk_index": idx,
                "act_name": act_name,
                "section_number": sec_num,
                "content": content,
                "embedding": emb
            }).execute()
            print(f"   -> Inserted new chunk for {act_name} Sec {sec_num}")
            
    print("Priority ingestion complete!")

if __name__ == "__main__":
    main()
