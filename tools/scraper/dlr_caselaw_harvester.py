import re
import os
import json
import logging
from pathlib import Path
from .json_exporter import export_caselaw_to_json, clean_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DLRCaseLawHarvester")

class DLRCaseLawHarvester:
    """
    Harvester and Intelligent Parser for Dhaka Law Reports (DLR), Supreme Court judgments,
    headnotes, ratio decidendi, and statute cross-references.
    """

    def __init__(self):
        # Regex patterns for DLR & Bangladesh Case Law citations
        self.citation_pattern = re.compile(
            r'(\d{1,3})\s+(DLR|BLD|BLC|ADC|ALR)\s*\((AD|HCD)\)?\s*(\d{1,4})',
            re.IGNORECASE
        )
        # Flexible patterns for Statute / Act Cross-References
        self.act_ref_patterns = [
            # E.g. "Section 498 of the Code of Criminal Procedure, 1898"
            re.compile(r'(?:section|sec\.|article|art\.)\s*(\d+[a-z]?)\s+(?:of\s+the\s+)?([A-Z][a-zA-Z\s,\(\)\d]+(?:Act|Code|Ordinance|Order)(?:,\s*\d{4})?)', re.IGNORECASE),
            # E.g. "Criminal Procedure Code 1898 Section 498" or "Penal Code, 1860 Section 302"
            re.compile(r'([A-Z][a-zA-Z\s,\(\)\d]+(?:Act|Code|Ordinance|Order)(?:\s*,?\s*\d{4})?)\s+(?:section|sec\.|article|art\.)\s*(\d+[a-z]?)', re.IGNORECASE)
        ]

    def clean_party_names(self, party_str: str) -> str:
        """Strips out court header noise from extracted party names."""
        lines = party_str.splitlines()
        clean_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if any(h in line_str.upper() for h in ['SUPREME COURT', 'APPELLATE DIVISION', 'HIGH COURT', 'DECIDED ON', 'DLR', 'BEFORE']):
                continue
            clean_lines.append(line_str)
        result = " ".join(clean_lines).strip()
        result = re.sub(r'[\.\_]{2,}', '', result)
        return re.sub(r'\s+', ' ', result).strip()

    def parse_case_text(self, raw_text: str, source_url_or_file: str = "DLR Repository") -> dict:
        """
        Extracts structured judicial parameters from raw precedent / DLR text:
        - Citation
        - Court & Division
        - Bench / Judges
        - Parties (Appellant vs Respondent)
        - Headnote
        - Ratio Decidendi
        - Enactments / Sections referenced
        """
        cleaned = clean_text(raw_text)

        # Extract Citation
        cit_match = self.citation_pattern.search(cleaned)
        if cit_match:
            vol, reporter, div, page = cit_match.groups()
            citation_str = f"{vol} {reporter.upper()} ({div.upper()}) {page}"
            division_str = "Appellate Division" if div.upper() == "AD" else "High Court Division"
            court_str = f"Supreme Court of Bangladesh ({division_str})"
        else:
            citation_str = "Unreported Judgment"
            court_str = "Supreme Court of Bangladesh"

        # Extract Parties (e.g., "Abdul Latif ...... Appellant VS The State ...... Respondent")
        parties_match = re.search(r'([A-Za-z\s\.,_\-]+?)\s+(?:VERSUS|vs\.?|V/S)\s+([A-Za-z\s\.,_\-]+)', cleaned, re.IGNORECASE)
        if parties_match:
            p1 = self.clean_party_names(parties_match.group(1))
            p2 = self.clean_party_names(parties_match.group(2))
            parties_str = f"{p1} vs. {p2}"
        else:
            parties_str = "State vs. Accused"

        # Extract Year from Citation or Text
        year_match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', cleaned)
        year_val = int(year_match.group(1)) if year_match else 2000

        # Extract Headnote (text before "Judgment" or first 1500 chars)
        judgment_split = re.split(r'\b(?:JUDGMENT|ORDER|DECISION)\b', cleaned, maxsplit=1, flags=re.IGNORECASE)
        headnote_text = judgment_split[0] if len(judgment_split) > 1 else cleaned[:1500]
        judgment_body = judgment_split[1] if len(judgment_split) > 1 else cleaned

        # Extract Ratio Decidendi / Main Ruling
        ratio_match = re.search(r'(?:held|we hold that|in view of the above|it is settled that)\s+([^\n\.]+\.)', cleaned, re.IGNORECASE)
        ratio_str = ratio_match.group(0).strip() if ratio_match else headnote_text[:400]

        # Extract Statute / Act Cross-References
        acts_found = []
        # Pattern 1: Section X of Act Y
        for match in self.act_ref_patterns[0].finditer(cleaned):
            sec_no, act_name = match.groups()
            cleaned_act = clean_text(act_name)
            if len(cleaned_act) > 4 and not cleaned_act.lower().startswith('of '):
                ref_item = f"{cleaned_act} (Section {sec_no})"
                if ref_item not in acts_found:
                    acts_found.append(ref_item)
        
        # Pattern 2: Act Y Section X
        for match in self.act_ref_patterns[1].finditer(cleaned):
            act_name, sec_no = match.groups()
            cleaned_act = clean_text(act_name)
            if len(cleaned_act) > 4 and not cleaned_act.lower().startswith('of '):
                ref_item = f"{cleaned_act} (Section {sec_no})"
                if ref_item not in acts_found:
                    acts_found.append(ref_item)

        return {
            "Citation": citation_str,
            "Court": court_str,
            "Bench": "Bench of Hon'ble Judges",
            "Parties": parties_str,
            "Year": year_val,
            "Headnote": headnote_text.strip(),
            "Ratio_Decidendi": ratio_str,
            "Acts_Referenced": acts_found,
            "Content": judgment_body.strip(),
            "Source_Provenance": f"{source_url_or_file}"
        }

    def process_file_or_text(self, text_or_path: str, source_info: str = "DLR Input") -> Path:
        """
        Parses case text or text file and writes to Justor AI JSON format.
        """
        if os.path.exists(text_or_path):
            with open(text_or_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            source_info = text_or_path
        else:
            content = text_or_path

        parsed = self.parse_case_text(content, source_info)
        out_path = export_caselaw_to_json(parsed)
        return out_path

def main():
    harvester = DLRCaseLawHarvester()
    sample_dlr = """
    52 DLR (AD) 112
    SUPREME COURT OF BANGLADESH
    APPELLATE DIVISION
    Abdul Latif ...... Appellant VS The State ...... Respondent
    Decided on 15 May 2000.
    
    HEADNOTE:
    Criminal Procedure Code 1898 Section 498 - Bail in non-bailable offences.
    Held: When there is no specific allegation against the accused in the FIR and co-accused on similar footing has been granted bail, the High Court Division erred in refusing bail under Section 498 of the Code of Criminal Procedure, 1898.
    
    JUDGMENT:
    This appeal by special leave is directed against the order of the High Court Division refusing bail to the appellant.
    We hold that the appellant is entitled to bail. Appeal allowed.
    """
    out_file = harvester.process_file_or_text(sample_dlr, "Sample DLR 52 (AD) 112")
    print(f"Sample DLR processing complete: {out_file}")

if __name__ == "__main__":
    main()
