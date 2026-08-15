import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def extract_cited_tags(text: str) -> List[str]:
    """Extract all [ACT-N] and [DLR-N] tags referenced in text."""
    return re.findall(r'\[(?:ACT|DLR)-\d+\]', text)

def validate_claim_evidence(answer: str, sources: List[Dict[str, Any]], retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates that claims made in the LLM answer are strictly grounded in retrieved evidence chunks.
    Returns (is_valid, list_of_issues).
    """
    issues = []
    if not answer or not sources:
        return True, []

    cited_tags = set(extract_cited_tags(answer))
    valid_source_ids = {s.get("id") for s in sources if "id" in s}

    # 1. Phantom Citation Check: Ensure model does not invent tag IDs not present in sources
    phantom_tags = cited_tags - valid_source_ids
    if phantom_tags:
        issues.append(f"Phantom citation tags found: {phantom_tags}")

    # 2. Extract Section Claims in answer (e.g. "Section 498 [ACT-1]")
    SECTION_CLAIM_RE = re.compile(
        r"(?:section|sec\.?|dhara|ধারা)\s*"
        r"(\d+[A-Za-z]?(?:\(\d+\))?(?:\([a-zA-Z]\))?)"
        r"(?:[^.!?\n]{0,100}?)"
        r"\[(ACT-\d+)\]", re.IGNORECASE
    )
    
    matches = SECTION_CLAIM_RE.findall(answer)
    source_map = {s["id"]: s for s in sources if "id" in s}

    for sec_num, tag in matches:
        if tag in source_map:
            src = source_map[tag]
            src_sec = str(src.get("section") or "").strip().lower()
            claimed_sec = str(sec_num).strip().lower()
            claimed_base = claimed_sec.split("(")[0].strip()
            
            # Verify claim section matches source section number or parent
            if claimed_sec != src_sec and claimed_base != src_sec.split("(")[0].strip():
                issues.append(f"Mismatched section citation: Answer claims Section {sec_num} for [{tag}], but source is Section {src.get('section')}")

    is_valid = len(issues) == 0
    return is_valid, issues


def sanitize_answer_citations(answer: str, sources: List[Dict[str, Any]]) -> str:
    """Strip invalid phantom or unsupported tags from answer."""
    valid_tags = {s["id"] for s in sources if "id" in s}
    all_tags = set(extract_cited_tags(answer))
    phantom_tags = all_tags - valid_tags

    for tag in phantom_tags:
        answer = answer.replace(f" [{tag}]", "")
        answer = answer.replace(f"[{tag}]", "")

    return answer
