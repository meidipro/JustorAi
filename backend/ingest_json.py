"""
JustorAI — JSON Law Data Ingestion Script
==========================================
Ingest structured law data from JSON files directly into Supabase.
This is faster than PDF since no OCR/parsing is needed.

JSON FORMAT (two supported shapes):
────────────────────────────────────

Shape 1 — Flat list of entries (simplest):
[
  {
    "title": "Penal Code 1860",
    "section": "299",
    "heading": "Culpable Homicide",
    "content": "Whoever causes death by doing an act with the intention of causing death..."
  },
  ...
]

Shape 2 — Document with sections (organised):
{
  "title": "Bangladesh Penal Code 1860",
  "description": "The main criminal code of Bangladesh",
  "sections": [
    {
      "section": "299",
      "heading": "Culpable Homicide",
      "content": "..."
    },
    {
      "section": "300",
      "heading": "Murder",
      "content": "..."
    }
  ]
}

Usage:
    python backend/ingest_json.py --file "./laws/penal_code.json"
    python backend/ingest_json.py --dir  "./laws/"
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ─── Load services ────────────────────────────────────────────────────────────

from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
).strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing VITE_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    sys.exit(1)

logger.info("Connecting to Supabase...")
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Ready.\n")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def embed(text: str) -> List[float]:
    # Strip null bytes — PostgreSQL cannot store \u0000
    text = text.replace('\x00', '').replace('\u0000', '')
    return model.encode(text, normalize_embeddings=True).tolist()


def parse_json_file(path: Path) -> List[Dict[str, Any]]:
    """
    Parse a JSON law file into a flat list of entries, each with:
      - title, section, heading, content
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    entries: List[Dict[str, Any]] = []

    if isinstance(data, list):
        # Shape 1: flat list
        for item in data:
            if not isinstance(item, dict):
                continue
            entries.append({
                "title":   item.get("title", path.stem),
                "section": item.get("section", ""),
                "heading": item.get("heading", ""),
                "content": item.get("content", ""),
            })

    elif isinstance(data, dict):
        # Shape 2: document with sections array
        doc_title = data.get("title", path.stem)
        sections = data.get("sections", [])
        for item in sections:
            entries.append({
                "title":   doc_title,
                "section": item.get("section", ""),
                "heading": item.get("heading", ""),
                "content": item.get("content", ""),
            })

    # Filter out empty content
    entries = [e for e in entries if e["content"].strip()]
    return entries


def ingest_entries(entries: List[Dict[str, Any]], filename: str, replace: bool = False) -> int:
    """Embed and insert all entries into Supabase. Returns count stored."""

    if not entries:
        return 0

    # Group by document title — each unique title = one row in `documents`
    entries_by_title: Dict[str, List[Dict]] = {}
    for e in entries:
        entries_by_title.setdefault(e["title"], []).append(e)

    total_stored = 0

    for doc_title, doc_entries in entries_by_title.items():
        logger.info(f"  Document: '{doc_title}' — {len(doc_entries)} entries")

        # If replace mode, delete old document (cascades to chunks)
        if replace:
            existing = db.table("documents").select("id").eq("title", doc_title).execute()
            for old_doc in existing.data:
                db.table("documents").delete().eq("id", old_doc["id"]).execute()
                logger.info(f"    Deleted old document: {old_doc['id']}")

        # Insert document row
        preview = doc_entries[0]["content"][:500]
        doc_resp = db.table("documents").insert({
            "title": doc_title,
            "content": preview,
            "metadata": {"filename": filename, "source": "json", "entries": len(doc_entries)},
        }).execute()
        document_id = doc_resp.data[0]["id"]

        # Embed + batch insert chunks
        records = []
        for i, entry in enumerate(doc_entries):
            # Build rich text for embedding: combines section, heading, content
            parts = []
            if entry["section"]:
                parts.append(f"Section {entry['section']}")
            if entry["heading"]:
                parts.append(entry["heading"])
            parts.append(entry["content"])
            chunk_text = " — ".join(parts)

            vec = embed(chunk_text)
            records.append({
                "document_id": document_id,
                "content": chunk_text,
                "embedding": vec,
                "chunk_index": i,
                "metadata": {
                    "source": filename,
                    "section": entry["section"],
                    "heading": entry["heading"],
                    "chunk": i,
                },
            })

            print(f"\r    Embedding {i+1}/{len(doc_entries)}...", end="", flush=True)

            if len(records) >= 50:
                db.table("document_chunks").insert(records).execute()
                records = []

        if records:
            db.table("document_chunks").insert(records).execute()

        print(f"\r    Stored {len(doc_entries)} chunks for '{doc_title}'          ")
        total_stored += len(doc_entries)

    return total_stored


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest JSON law data into JustorAI knowledge base.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a single JSON file")
    group.add_argument("--dir",  help="Path to a directory of JSON files")
    parser.add_argument("--replace", action="store_true",
                        help="Delete existing document with same title before re-inserting")
    args = parser.parse_args()

    json_files: List[Path] = []
    if args.file:
        p = Path(args.file)
        if not p.is_file():
            print(f"ERROR: '{p}' is not a file.")
            sys.exit(1)
        json_files = [p]
    else:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"ERROR: '{d}' is not a directory.")
            sys.exit(1)
        json_files = sorted(d.glob("**/*.json"))

    if not json_files:
        print("No JSON files found.")
        sys.exit(0)

    print(f"Found {len(json_files)} JSON file(s).\n")

    total_success, total_failed = 0, 0
    for jf in json_files:
        print(f"-> {jf.name}")
        try:
            entries = parse_json_file(jf)
            if not entries:
                print(f"   WARNING: No entries found (check format).\n")
                total_failed += 1
                continue
            print(f"   Parsed {len(entries)} entries.")
            stored = ingest_entries(entries, jf.name, replace=args.replace)
            print(f"   Done: {stored} chunks stored.\n")
            total_success += 1
        except Exception as e:
            print(f"   FAILED: {e}\n")
            total_failed += 1

    print(f"Complete. {total_success} file(s) ingested, {total_failed} failed.")


if __name__ == "__main__":
    main()
