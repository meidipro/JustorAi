# tools/supreme_court/ingest.py
import json
import sqlite3
import sys
import time
import httpx
from pathlib import Path
from supabase import create_client
from .config import (
    CHECKPOINT_DB, PDF_VAULT, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY,
    OPENROUTER_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIM
)

sys.stdout.reconfigure(encoding='utf-8')


supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
STAGING_TABLE = "sc_judgment_staging"  # separate from production document_chunks

def create_staging_table_instructions():
    """Returns SQL statement to create the staging table in Supabase."""
    return f"""
    CREATE TABLE IF NOT EXISTS {STAGING_TABLE} (
        id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        manifest_id text NOT NULL,
        document_type text NOT NULL DEFAULT 'SC_JUDGMENT_HCD',
        case_id text,
        division text,
        case_number text,
        case_year text,
        parties_raw text,
        judgment_date text,
        uploaded_date text,
        judges text[],
        acts_cited text[],
        sections_cited text[],
        content text NOT NULL,
        page_number integer,
        official_pdf_url text,
        source_url text,
        review_status text DEFAULT 'UNREVIEWED',
        embedding vector({EMBEDDING_DIM}),
        embedding_model text DEFAULT '{EMBEDDING_MODEL}',
        embedding_dimension integer DEFAULT {EMBEDDING_DIM},
        promoted_to_production boolean DEFAULT false,
        created_at timestamptz DEFAULT now()
    );
    """

def get_embedding(text: str) -> list[float]:
    """Get BGE-M3 1024-dim embedding via OpenRouter."""
    text = text[:12000]

    response = httpx.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": EMBEDDING_MODEL,
            "input": [text]
        },
        timeout=30.0
    )

    data = response.json()
    return data["data"][0]["embedding"]

def chunk_case_for_rag(
    manifest: dict,
    parsed: dict,
    extracted: dict
) -> list[dict]:
    """Split a judgment into page-level chunks for RAG."""
    chunks = []
    pages = extracted.get("pages", [])

    div_code = "HCD" if "High Court" in manifest.get("division", "") else "AD"
    doc_type = f"SC_JUDGMENT_{div_code}"

    for page in pages[:10]:  # cap at 10 pages for pilot
        text = page["selected_text"].strip()
        if len(text) < 100:
            continue

        chunk = {
            "manifest_id":    manifest["manifest_id"],
            "document_type":  doc_type,
            "case_id":        manifest["manifest_id"],
            "division":       manifest["division"],
            "case_number":    manifest["case_number"],
            "case_year":      manifest["case_year"],
            "parties_raw":    manifest["parties_raw"],
            "judgment_date":  parsed.get("judgment_date"),
            "uploaded_date":  manifest["uploaded_date"],
            "judges":         parsed.get("judges", []),
            "acts_cited":     parsed.get("acts_cited", []),
            "sections_cited": parsed.get("sections_cited", []),
            "content":        text,
            "page_number":    page["page_number"],
            "official_pdf_url": manifest["pdf_url"],
            "source_url":     manifest["pdf_url"],
            "review_status":  "UNREVIEWED",
        }
        chunks.append(chunk)

    return chunks

def ingest_case(manifest_id: str, conn) -> int:
    """Embed and ingest one case into staging. Returns chunk count."""
    row = conn.execute(
        "SELECT * FROM sc_manifest WHERE manifest_id=?",
        (manifest_id,)
    ).fetchone()
    if not row:
        print(f"  Not found in manifest: {manifest_id}")
        return 0

    col_names = [d[1] for d in conn.execute(
        "PRAGMA table_info(sc_manifest)"
    ).fetchall()]
    manifest = dict(zip(col_names, row))


    parsed_path = PDF_VAULT / f"{manifest_id}_parsed.json"
    extracted_path = PDF_VAULT / f"{manifest_id}_extracted.json"

    if not parsed_path.exists() or not extracted_path.exists():
        print(f"  Missing extracted files for: {manifest_id}")
        return 0

    with open(parsed_path, encoding="utf-8") as f:
        parsed = json.load(f)
    with open(extracted_path, encoding="utf-8") as f:
        extracted = json.load(f)

    chunks = chunk_case_for_rag(manifest, parsed, extracted)
    if not chunks:
        print(f"  No valid chunks generated: {manifest_id}")
        return 0

    inserted = 0
    for chunk in chunks:
        time.sleep(0.5)

        try:
            embedding = get_embedding(chunk["content"])
        except Exception as e:
            print(f"  Embedding error page {chunk['page_number']}: {e}")
            continue

        try:
            supabase.table(STAGING_TABLE).insert({
                **chunk,
                "embedding": embedding
            }).execute()
            inserted += 1
            print(f"    ✓ Page {chunk['page_number']} embedded and staged")
        except Exception as e:
            print(f"  Insert error: {e}")

    conn.execute(
        "UPDATE sc_manifest SET ingest_status='STAGED' WHERE manifest_id=?",
        (manifest_id,)
    )
    conn.commit()
    return inserted

def run_ingestion():
    """Phase 5: Embed and ingest parsed cases into staging."""
    conn = sqlite3.connect(CHECKPOINT_DB)

    pending = conn.execute("""
        SELECT manifest_id FROM sc_manifest
        WHERE extraction_status = 'EXTRACTED'
        AND ingest_status = 'PENDING'
    """).fetchall()

    print(f"=== Ingesting {len(pending)} cases into staging ===")
    total_chunks = 0

    for (manifest_id,) in pending:
        print(f"\n  {manifest_id}")
        count = ingest_case(manifest_id, conn)
        total_chunks += count

    conn.close()
    print(f"\n=== INGESTION COMPLETE: {total_chunks} chunks in staging ===")

if __name__ == "__main__":
    run_ingestion()
