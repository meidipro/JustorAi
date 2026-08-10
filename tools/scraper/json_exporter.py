import json
import re
import logging
from pathlib import Path
from .scrapling_config import OUTPUT_DIR

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Removes null bytes, normalizes space padding, and cleans HTML entity noise."""
    if not text:
        return ""
    # Strip null characters
    text = text.replace('\x00', '').replace('\u0000', '')
    # Normalize multiple spaces & non-breaking spaces
    text = re.sub(r'[\r\t\xa0]', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s+\n', '\n\n', text)
    return text.strip()

def sanitize_filename(name: str, fallback_id: str = "") -> str:
    """Converts act/case title into safe lower_snake_case filename with Unicode/Bengali support."""
    clean = clean_text(name).lower()
    # Support unicode word characters (including Bengali \u0980-\u09ff)
    slug = re.sub(r'[^\w\d]', '_', clean, flags=re.UNICODE)
    slug = re.sub(r'_+', '_', slug).strip('_')
    if not slug or slug.replace('_', '') == "":
        return f"act_{fallback_id}" if fallback_id else "unnamed_document"
    return f"act_{fallback_id}_{slug[:50]}" if fallback_id else slug[:60]

def export_act_to_json(act_name: str, sections: list, provenance_url: str, output_dir: Path = None, act_id: str = "") -> Path:
    """
    Validates and formats scraped sections into Justor AI Act JSON format.
    Saves to output_dir or knowledge/scraped directory.
    """
    if not output_dir:
        output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if not act_id:
        match = re.search(r'act-(?:details|print)-(\d+)\.html', provenance_url)
        if match:
            act_id = match.group(1)

    formatted_sections = []
    clean_act_name = clean_text(act_name)

    for sec in sections:
        sec_num = clean_text(str(sec.get("Section_Number", "")))
        sec_title = clean_text(sec.get("Section_Title", ""))
        content = clean_text(sec.get("Content", ""))
        status = clean_text(sec.get("Status", "Active"))
        amendments = [clean_text(a) for a in sec.get("Amendment_Notes", []) if clean_text(a)]
        repeals = [clean_text(r) for r in sec.get("Repealed_Clauses", []) if clean_text(r)]

        formatted_sections.append({
            "Act_Name": clean_act_name,
            "Section_Number": sec_num,
            "Section_Title": sec_title,
            "Status": status,
            "Jurisdiction": sec.get("Jurisdiction", "Bangladesh"),
            "Source_Reference": f"{clean_act_name} — Bangladesh Code",
            "Source_Provenance": f"{provenance_url}",
            "Content": content,
            "Repealed_Clauses": repeals,
            "Amendment_Notes": amendments
        })

    fname = f"{sanitize_filename(clean_act_name, fallback_id=act_id)}.json"
    file_path = output_dir / fname

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(formatted_sections, f, ensure_ascii=False, indent=2)

    logger.info(f"Successfully exported '{clean_act_name}' ({len(formatted_sections)} sections) -> {file_path}")
    return file_path

def export_caselaw_to_json(caselaw_data: dict, output_dir: Path = None) -> Path:
    """Formats scraped DLR / Case Law record into Justor AI standard JSON."""
    if not output_dir:
        output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    citation = clean_text(caselaw_data.get("Citation", "Unknown Citation"))
    record = {
        "Document_Type": "CaseLaw",
        "Citation": citation,
        "Court": clean_text(caselaw_data.get("Court", "Supreme Court of Bangladesh")),
        "Bench": clean_text(caselaw_data.get("Bench", "")),
        "Parties": clean_text(caselaw_data.get("Parties", "")),
        "Year": caselaw_data.get("Year", 2000),
        "Headnote": clean_text(caselaw_data.get("Headnote", "")),
        "Ratio_Decidendi": clean_text(caselaw_data.get("Ratio_Decidendi", "")),
        "Acts_Referenced": [clean_text(a) for a in caselaw_data.get("Acts_Referenced", []) if clean_text(a)],
        "Content": clean_text(caselaw_data.get("Content", "")),
        "Source_Provenance": caselaw_data.get("Source_Provenance", "DLR Case Law Repository")
    }

    fname = f"dlr_{sanitize_filename(citation)}.json"
    file_path = output_dir / fname

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([record], f, ensure_ascii=False, indent=2)

    logger.info(f"Successfully exported Case Law '{citation}' -> {file_path}")
    return file_path
