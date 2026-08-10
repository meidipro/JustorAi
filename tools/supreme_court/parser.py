# tools/supreme_court/parser.py
import re
import json
import sqlite3
import sys
from pathlib import Path
from .config import CHECKPOINT_DB, PDF_VAULT

sys.stdout.reconfigure(encoding='utf-8')


PATTERNS = {
    "judgment_date": [
        r"(?:Judgment|Decided|Delivered|Date of Judgment)[:\s]+(\d{1,2}(?:st|nd|rd|th)?\s+\w+,?\s+\d{4})",
        r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})",
    ],
    "case_number": [
        r"((?:Civil|Criminal|Writ|Company)\s+(?:Appeal|Petition|Revision|Reference|Miscellaneous)\s+No\.?\s*\d+\s+of\s+\d{4})",
        r"(No\.\s*\d+\s+of\s+\d{4})",
    ],
    "judges": [
        r"(?:Before|Bench|Coram)[:\s]*\n(.+?)(?:\n|$)",
        r"Mr\. Justice ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
        r"Justice ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
    ],
    "acts_cited": [
        r"((?:Code of Criminal Procedure|Code of Civil Procedure|Penal Code|"
        r"Evidence Act|Transfer of Property Act|State Acquisition|"
        r"Non-Agricultural Tenancy Act|Muslim Family Laws Ordinance|"
        r"Contract Act|Limitation Act|Land Reforms Act|Specific Relief Act|"
        r"Registration Act|Constitution)[^,\.]{0,30}(?:,\s*\d{4})?)",
    ],
    "sections_cited": [
        r"[Ss]ection\s+(\d+[A-Za-z]?(?:\(\d+\))?(?:\([a-z]\))?)",
        r"[Aa]rticle\s+(\d+[A-Za-z]?)",
        r"[Oo]rder\s+([\dA-Z]+),\s*[Rr]ule\s+(\d+)",
    ],
}

def extract_first_match(text: str, patterns: list) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def extract_all_matches(text: str, patterns: list) -> list:
    results = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            results.add(match.group(1).strip())
    return sorted(results)

def parse_metadata(manifest_id: str) -> dict:
    """Extract deterministic fields from first 3 pages of extracted text."""
    extract_path = PDF_VAULT / f"{manifest_id}_extracted.json"
    if not extract_path.exists():
        return {"status": "EXTRACTION_FILE_NOT_FOUND"}

    with open(extract_path, encoding="utf-8") as f:
        extracted = json.load(f)

    if extracted.get("status") != "EXTRACTED":
        return {"status": "EXTRACTION_FAILED"}

    first_pages_text = " ".join(
        p["selected_text"]
        for p in extracted["pages"][:3]
    )

    full_text = extracted.get("full_text", "")

    parsed = {
        "manifest_id":     manifest_id,
        "judgment_date":   extract_first_match(first_pages_text, PATTERNS["judgment_date"]),
        "case_number_pdf": extract_first_match(first_pages_text, PATTERNS["case_number"]),
        "judges":          extract_all_matches(first_pages_text, PATTERNS["judges"]),
        "acts_cited":      extract_all_matches(full_text, PATTERNS["acts_cited"]),
        "sections_cited":  extract_all_matches(full_text, PATTERNS["sections_cited"]),
        "page_count":      extracted["page_count"],
        "ocr_pages":       extracted["ocr_pages"],
        "parse_status":    "AUTO_PARSED",
        "review_status":   "UNREVIEWED",
        "confidence_note": "Deterministic extraction only — no AI used."
    }

    parsed_path = PDF_VAULT / f"{manifest_id}_parsed.json"
    with open(parsed_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print(f"  ✓ Parsed: {manifest_id} — date:{parsed['judgment_date']} judges:{len(parsed['judges'])}")
    return parsed

def run_parsing():
    """Phase 4: Parse all extracted PDFs."""
    conn = sqlite3.connect(CHECKPOINT_DB)
    pending = conn.execute("""
        SELECT manifest_id FROM sc_manifest
        WHERE extraction_status = 'EXTRACTED'
    """).fetchall()

    print(f"=== Parsing {len(pending)} cases ===")
    for (manifest_id,) in pending:
        result = parse_metadata(manifest_id)
        if result.get("judgment_date"):
            conn.execute(
                "UPDATE sc_manifest SET judgment_date=?, judges=? WHERE manifest_id=?",
                (result["judgment_date"], str(result["judges"]), manifest_id)
            )
        conn.commit()

    conn.close()
    print("\n=== PARSING COMPLETE ===")

if __name__ == "__main__":
    run_parsing()
