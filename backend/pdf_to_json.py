"""
JustorAI — PDF to JSON Converter  (v2)
========================================
Converts law PDFs into structured JSON for RAG ingestion.

Key improvements over v1:
- Inline section detection: finds "154. Heading" anywhere in the text stream,
  not just at line-starts (fixes bdlaws.minlaw.gov.bd PDF format)
- Smart chunking: each section is split into <=MAX_CHUNK_CHARS chunks,
  so embedding quality stays high regardless of section length
- Better noise removal: strips bdlaws headers, page numbers, URLs

Usage:
    python backend/pdf_to_json.py --file "Criminal procedure 1898.pdf"
    python backend/pdf_to_json.py --dir "D:/Justor AI/LawPDFs/" --out "backend/law_data/"
    python backend/pdf_to_json.py --file "my_law.pdf" --preview
"""

import re
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import PyPDF2


# ─── Tunables ─────────────────────────────────────────────────────────────────
MAX_CHUNK_CHARS = 1200   # Hard cap per chunk (≈300 tokens) — optimal for MiniLM
OVERLAP_CHARS   = 150    # Characters of overlap between consecutive chunks


# ─── Noise patterns ───────────────────────────────────────────────────────────
NOISE_PATTERNS = [
    # bdlaws URLs
    re.compile(r'bdlaws\.minlaw\.gov\.bd\S*', re.IGNORECASE),
    # "19/02/2026 The Penal Code, 1860" style date+title headers
    re.compile(r'\d{2}/\d{2}/\d{4}\s+[^\n]{5,80}'),
    # Page numbers (standalone digits, possibly with whitespace)
    re.compile(r'(?<!\d)\s{0,4}\d{1,4}\s{0,4}(?!\d)', re.MULTILINE),
]

# ─── Inline section-split regex ───────────────────────────────────────────────
# Matches patterns like:  "154. Heading text"   "154A. Heading"   "Section 154."
# Works on the FULL concatenated text, not line-by-line.
INLINE_SECTION_RE = re.compile(
    r'(?<!\d)'                         # not preceded by a digit
    r'(\d{1,4}[A-Za-z]?)'             # section number (e.g. "154", "120A", "171B")
    r'\.'                              # literal dot
    r'[ \t]+'                          # at least one space/tab
    r'([A-Z][^\n.]{3,100}?)'          # Heading (starts uppercase, 3-100 chars)
    r'(?=\n|\s{2,}|\d+\.|[A-Z][a-z])', # lookahead: newline, double-space, or next section
    re.MULTILINE
)


def extract_text_from_pdf(path: Path) -> str:
    """Extract raw text from all pages of the PDF concatenated."""
    pages = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


def clean_text(text: str) -> str:
    """Strip null bytes, URLs, and common header/footer noise."""
    # Null bytes cause PostgreSQL errors
    text = text.replace('\x00', '').replace('\u0000', '')
    # Remove bdlaws.minlaw.gov.bd noise
    text = re.sub(r'bdlaws\.minlaw\.gov\.bd\S*', '', text, flags=re.IGNORECASE)
    # Remove "dd/mm/yyyy The Law Title" headers
    text = re.sub(r'\d{2}/\d{2}/\d{4}[^\n]{0,80}\n?', '', text)
    # Collapse excess whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{3,}', '  ', text)
    return text.strip()


def split_into_chunks(text: str, max_chars: int = MAX_CHUNK_CHARS,
                      overlap: int = OVERLAP_CHARS) -> List[str]:
    """
    Split a text block into overlapping chunks of at most max_chars.
    Tries to break at sentence boundaries ('. ', '? ', '! ').
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to break at a sentence boundary within the last 200 chars of the window
        boundary = -1
        for sep in ('. ', '.\n', '? ', '! ', '\n\n'):
            pos = text.rfind(sep, start + max_chars - 200, end)
            if pos != -1:
                boundary = pos + len(sep)
                break

        if boundary == -1:
            # Fall back to word boundary
            boundary = text.rfind(' ', start + max_chars - 100, end)
            if boundary == -1:
                boundary = end

        chunk = text[start:boundary].strip()
        if chunk:
            chunks.append(chunk)
        start = boundary - overlap  # overlap with a bit of previous context
        if start <= 0 and chunks:
            break

    return [c for c in chunks if c]


def parse_sections_inline(raw_text: str, doc_title: str) -> List[Dict]:
    """
    Split the raw PDF text into sections using inline regex detection.
    Each section is then split into sensibly sized chunks.

    Returns: list of {section, heading, content, chunk_index}
    """
    # Find all section-number positions in the text
    matches = list(INLINE_SECTION_RE.finditer(raw_text))

    if not matches:
        # Fall back to paragraph chunking
        return fallback_paragraph_split(raw_text)

    sections_raw: List[Tuple[str, str, str]] = []  # (num, heading, content)

    for i, m in enumerate(matches):
        sec_num = m.group(1)
        heading = m.group(2).strip().rstrip('.')

        # Content starts after the matched heading
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        content = raw_text[content_start:content_end].strip()

        # Include the heading itself in the content for context
        full_content = f"{sec_num}. {heading}\n{content}"
        sections_raw.append((sec_num, heading, full_content))

    # Also grab any introductory text before the first match
    intro = raw_text[:matches[0].start()].strip() if matches else raw_text
    if intro and len(intro) > 100:
        sections_raw.insert(0, ("0", "Introduction", intro))

    # Now produce final chunks — split large sections
    result = []
    for sec_num, heading, content in sections_raw:
        chunks = split_into_chunks(content)
        for ci, chunk in enumerate(chunks):
            result.append({
                "section": sec_num,
                "heading": heading,
                "content": chunk,
                "chunk_index": ci,
            })

    return result


def fallback_paragraph_split(text: str) -> List[Dict]:
    """Fallback: split by paragraph when no section structure is found."""
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
    result = []
    buffer = []
    buf_len = 0
    chunk_num = 1

    for para in paragraphs:
        if buf_len + len(para) > MAX_CHUNK_CHARS and buffer:
            result.append({
                "section": str(chunk_num),
                "heading": f"Part {chunk_num}",
                "content": "\n\n".join(buffer),
                "chunk_index": 0,
            })
            chunk_num += 1
            buffer = [para]
            buf_len = len(para)
        else:
            buffer.append(para)
            buf_len += len(para)

    if buffer:
        result.append({
            "section": str(chunk_num),
            "heading": f"Part {chunk_num}",
            "content": "\n\n".join(buffer),
            "chunk_index": 0,
        })

    return result


def pdf_to_json(pdf_path: Path, out_dir: Path, preview: bool = False) -> Optional[Path]:
    """Convert one PDF to a JSON file. Returns output path or None on skip."""
    print(f"\n-> {pdf_path.name}")

    raw = extract_text_from_pdf(pdf_path)
    if not raw.strip():
        print("   WARNING: No text extracted (scanned/image PDF?). Skipping.")
        return None

    raw = clean_text(raw)
    title = pdf_path.stem.replace("_", " ").replace("-", " ").title()
    sections = parse_sections_inline(raw, title)

    print(f"   Detected {len(sections)} chunks.")

    result = {
        "title": title,
        "source_file": pdf_path.name,
        "sections": sections,
    }

    if preview:
        for s in sections[:5]:
            print(f"   [{s['section']}:{s['chunk_index']}] {s['heading']}")
            print(f"       {s['content'][:120]}...")
        return None

    out_path = out_dir / (pdf_path.stem + ".json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"   Saved -> {out_path}")
    return out_path


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Convert law PDFs to structured JSON (v2).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a single PDF file")
    group.add_argument("--dir",  help="Path to a directory containing PDF files")
    parser.add_argument("--out", default="backend/law_data/",
                        help="Output directory for JSON files (default: backend/law_data/)")
    parser.add_argument("--preview", action="store_true",
                        help="Preview first 5 chunks without saving")
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not args.preview:
        out_dir.mkdir(parents=True, exist_ok=True)

    pdf_files: List[Path] = []
    if args.file:
        p = Path(args.file)
        if not p.is_file():
            print(f"ERROR: '{p}' is not a file.")
            sys.exit(1)
        pdf_files = [p]
    else:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"ERROR: '{d}' is not a directory.")
            sys.exit(1)
        pdf_files = sorted(d.glob("**/*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF(s). Converting to JSON...\n")

    success, failed = 0, 0
    for pdf in pdf_files:
        try:
            result = pdf_to_json(pdf, out_dir, preview=args.preview)
            if result or args.preview:
                success += 1
        except Exception as e:
            print(f"   FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    if not args.preview:
        print(f"\nDone. {success} JSON file(s) saved to '{out_dir}/', {failed} failed.")
        print(f"\nNext: re-ingest updated JSONs into Supabase:")
        print(f"  .venv\\Scripts\\python.exe backend/ingest_json.py --dir \"{out_dir}\"")


if __name__ == "__main__":
    main()
