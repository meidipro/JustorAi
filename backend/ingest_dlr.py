"""
JustorAI — Dhaka Law Reports (DLR) Ingestion Script
=====================================================
Parses DLR Part 1.md into individual case entries and ingests them
into Supabase under a single 'Dhaka Law Reports (DLR) Part 1' document.

Each case becomes one chunk with metadata: division, date, parties, laws cited.

Usage:
    .venv\\Scripts\\python.exe backend/ingest_dlr.py --file "DLR Part 1.md"
    .venv\\Scripts\\python.exe backend/ingest_dlr.py --file "DLR Part 1.md" --url http://localhost:10000
"""

import re
import os
import sys
import json
import uuid
import argparse
from pathlib import Path
from typing import List, Dict, Any

# ─── Load env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
    load_dotenv(Path(__file__).parent.parent / ".env.local")
except ImportError:
    pass

try:
    from supabase import create_client, Client
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: .venv\\Scripts\\pip install supabase sentence-transformers")
    sys.exit(1)

# ─── Config ───────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
).strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    sys.exit(1)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DOCUMENT_TITLE = "Dhaka Law Reports (DLR) Part 1"

# ─── Embedding ────────────────────────────────────────────────────────────────
print("INFO: Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
print("INFO: Ready.\n")


def embed(text: str) -> List[float]:
    """Embed text, stripping null bytes that PostgreSQL cannot store."""
    text = text.replace('\x00', '').replace('\u0000', '')
    return model.encode(text, normalize_embeddings=True).tolist()


# ─── DLR Parser ───────────────────────────────────────────────────────────────

# Matches bold division headers like **APPELLATE DIVISION(Civil)** or **APPELLATE DIVISION (Criminal)**
CASE_DIVIDER = re.compile(
    r'(?=\*\*APPELLATE DIVISION[\s(])',
    re.IGNORECASE
)

# Extract division type: Civil, Criminal, etc.
DIVISION_RE = re.compile(
    r'\*\*APPELLATE DIVISION\s*\(?(\w+)?\)?',
    re.IGNORECASE
)

# Extract judgment date
DATE_RE = re.compile(
    r'Judgment\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4})',
    re.IGNORECASE
)

# Extract parties (Petitioner/Appellant vs Respondent)
PARTIES_RE = re.compile(
    r'([\w\s,.()\[\]]+?)\s*(?:\.{2,}|…+)?\s*(?:Petitioner|Appellant)s?\s*(?:vs?\.?\s*|VS\s*)\s*([\w\s,.()\[\]]+?)\s*(?:\.{2,}|…+)?\s*(?:Respondent|State)',
    re.IGNORECASE
)

# Extract law sections cited
LAWS_RE = re.compile(
    r'(?:Code|Act|Ordinance|Constitution|Order|Section)\s+[^\n]{3,80}',
    re.IGNORECASE
)


def clean(text: str) -> str:
    """Strip null bytes and normalise whitespace."""
    text = text.replace('\x00', '').replace('\u0000', '')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_case(raw: str, idx: int) -> Dict[str, Any]:
    """Parse a single DLR case block into structured metadata + text."""
    raw = clean(raw)

    # Division
    div_match = DIVISION_RE.search(raw[:200])
    division = div_match.group(1).strip() if (div_match and div_match.group(1)) else "General"

    # Date
    date_match = DATE_RE.search(raw[:500])
    date = date_match.group(1).strip() if date_match else ""

    # Parties (first occurrence)
    parties_match = PARTIES_RE.search(raw[:600])
    if parties_match:
        petitioner = parties_match.group(1).strip()[:120]
        respondent = parties_match.group(2).strip()[:120]
    else:
        petitioner = ""
        respondent = ""

    # Laws cited (collect first 5 unique matches)
    laws = list(dict.fromkeys(
        m.strip()[:100] for m in LAWS_RE.findall(raw[:1000])
    ))[:5]

    # Build a short title from first meaningful line
    lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith('**')]
    short_title = lines[0][:120] if lines else f"Case {idx + 1}"

    return {
        "chunk_index": idx,
        "content": raw,
        "metadata": {
            "source": DOCUMENT_TITLE,
            "division": f"Appellate Division ({division})",
            "date": date,
            "petitioner": petitioner,
            "respondent": respondent,
            "laws_cited": laws,
            "case_number": idx + 1,
            "title": short_title,
        }
    }


def parse_dlr_md(path: Path) -> List[Dict[str, Any]]:
    """Split DLR markdown file into individual case entries."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = clean(text)

    # Split on each **APPELLATE DIVISION... header
    raw_cases = CASE_DIVIDER.split(text)

    # Filter out empty/tiny fragments
    cases = []
    for i, block in enumerate(raw_cases):
        block = block.strip()
        if len(block) < 100:  # Skip tiny fragments
            continue
        cases.append(parse_case(block, len(cases)))

    return cases


# ─── Supabase Ingest ──────────────────────────────────────────────────────────

def ingest_dlr(md_path: Path):
    """Parse DLR markdown and store in Supabase."""
    print(f"Parsing: {md_path.name}")
    cases = parse_dlr_md(md_path)
    print(f"  Found {len(cases)} case entries.\n")

    if not cases:
        print("ERROR: No cases parsed. Check the file format.")
        sys.exit(1)

    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Create or reuse the top-level document
    print(f"Creating document: '{DOCUMENT_TITLE}'")
    doc_res = sb.table("documents").insert({
        "title": DOCUMENT_TITLE,
        "content": f"Dhaka Law Reports (DLR) Part 1 — {len(cases)} case entries",
        "metadata": {
            "type": "case_law",
            "reporter": "Dhaka Law Reports",
            "part": "Part 1",
            "jurisdiction": "Bangladesh",
            "courts": ["Appellate Division", "High Court Division"],
            "total_cases": len(cases),
        }
    }).execute()

    doc_id = doc_res.data[0]["id"]
    print(f"  Document ID: {doc_id}\n")

    ok = 0
    fail = 0

    for case in cases:
        idx = case["chunk_index"]
        meta = case["metadata"]
        content = case["content"]

        label = f"Case {idx + 1}: {meta['division']} — {meta['date'] or 'n/d'}"
        print(f"  [{idx + 1}/{len(cases)}] Embedding {label[:80]}...")

        try:
            vector = embed(content)

            sb.table("document_chunks").insert({
                "document_id": doc_id,
                "chunk_index": idx,
                "content": content,
                "embedding": vector,
                "metadata": meta,
            }).execute()

            ok += 1
        except Exception as e:
            print(f"  ERROR on case {idx + 1}: {e}")
            fail += 1

    print(f"\nDone. {ok} cases stored, {fail} failed.")
    if fail == 0:
        print(f"✅  '{DOCUMENT_TITLE}' is live in Supabase with {ok} case chunks!")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest DLR markdown into Supabase")
    parser.add_argument(
        "--file", "-f",
        default="DLR Part 1.md",
        help="Path to the DLR markdown file (default: 'DLR Part 1.md')"
    )
    args = parser.parse_args()

    md_path = Path(args.file)
    if not md_path.is_absolute():
        # Resolve relative to the project root (two levels up from backend/)
        md_path = Path(__file__).parent.parent / md_path

    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}")
        sys.exit(1)

    ingest_dlr(md_path)


if __name__ == "__main__":
    main()
