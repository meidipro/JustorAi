from __future__ import annotations

import asyncio
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Optional
from backend.legal_normalize import normalize_section, split_section_reference, normalize_act_alias

@dataclass
class ParsedLegalQuery:
    raw: str
    normalized: str
    section: str | None = None
    order: str | None = None
    rule: str | None = None
    article: str | None = None
    act_keyword: str | None = None
    case_number: str | None = None
    case_year: str | None = None
    dlr_vol: str | None = None
    dlr_page: str | None = None
    likely_type: str | None = None

SECTION_RE = re.compile(
    r"(?:section|sec\.?|§)\s*([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*)",
    re.I,
)

ORDER_RULE_RE = re.compile(
    r"(?:order|ord\.?)\s*([0-9IVXLCDM]+)\s*(?:rule|r\.?)\s*([0-9]+[A-Za-z]?)",
    re.I,
)

ARTICLE_RE = re.compile(
    r"(?:article|art\.?)\s*([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*)",
    re.I,
)

DLR_RE = re.compile(
    r"(\d+)\s*DLR\s*(?:\((?:AD|HCD)\))?\s*(\d+)",
    re.I,
)

CASE_NO_RE = re.compile(
    r"\b(?:wp|writ\s*petition|civil\s*appeal|criminal\s*appeal|ca|cra|cp)\s*(\d+)\s*(?:/|of)\s*(20\d{2}|19\d{2})\b",
    re.I,
)

def normalize_legal_query(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = value.strip()
    value = re.sub(r"\bsec(?:tion)?\.?\s*", "section ", value, flags=re.I)
    value = re.sub(r"\s+", " ", value)
    return value

def parse_legal_query(query: str) -> ParsedLegalQuery:
    norm = normalize_legal_query(query)
    res = ParsedLegalQuery(raw=query, normalized=norm)

    sec_m = SECTION_RE.search(norm)
    if sec_m:
        res.section = sec_m.group(1).upper()
        res.likely_type = "section"

    ord_m = ORDER_RULE_RE.search(norm)
    if ord_m:
        res.order = ord_m.group(1).upper()
        res.rule = ord_m.group(2).upper()
        res.section = f"ORDER_{res.order}_RULE_{res.rule}"
        res.likely_type = "section"

    art_m = ARTICLE_RE.search(norm)
    if art_m:
        res.article = art_m.group(1).upper()
        res.section = res.article
        res.likely_type = "section"

    dlr_m = DLR_RE.search(norm)
    if dlr_m:
        res.dlr_vol = dlr_m.group(1)
        res.dlr_page = dlr_m.group(2)
        res.likely_type = "case"

    case_m = CASE_NO_RE.search(norm)
    if case_m:
        res.case_number = case_m.group(1)
        res.case_year = case_m.group(2)
        res.likely_type = "case"

    # Detect common Act keywords
    act_keywords = [
        ("registration", "The Registration Act, 1908"),
        ("transfer of property", "The Transfer of Property Act, 1882"),
        ("tpa", "The Transfer of Property Act, 1882"),
        ("penal code", "The Penal Code, 1860"),
        ("crpc", "The Code of Criminal Procedure, 1898"),
        ("cpc", "The Code of Civil Procedure, 1908"),
        ("specific relief", "The Specific Relief Act, 1877"),
        ("contract act", "The Contract Act, 1872"),
        ("limitation act", "The Limitation Act, 1908"),
        ("constitution", "The Constitution of the People's Republic of Bangladesh"),
        ("labour act", "The Bangladesh Labour Act, 2006"),
        ("consumer", "Consumers' Right Protection Act, 2009"),
        ("family courts", "Family Courts Act, 2023"),
        ("income tax", "Income Tax Act, 2023"),
        ("cyber", "Cyber Security Act, 2026"),
    ]
    norm_lower = norm.lower()
    for kw, act_full in act_keywords:
        if kw in norm_lower:
            res.act_keyword = act_full
            break

    return res


class LegalSearchAggregator:
    def __init__(self, laws_client: Any, cases_client: Any):
        self.laws_client = laws_client
        self.cases_client = cases_client

    async def search(
        self,
        query: str,
        entity_type: str = "all",
        limit: int = 20,
    ) -> list[dict]:
        parsed = parse_legal_query(query)
        tasks = []

        # Route to appropriate Supabase project(s)
        if entity_type in {"all", "act", "laws", "section", "sections", "amendment", "amendments", "guide", "guides"}:
            tasks.append(self._search_project_a(query, parsed, entity_type, limit))

        if entity_type in {"all", "case", "cases", "dlr"}:
            tasks.append(self._search_project_b(query, parsed, limit))

        batches = await asyncio.gather(*tasks, return_exceptions=True)
        merged = []
        for b in batches:
            if isinstance(b, list):
                merged.extend(b)

        # Rank by match quality
        merged.sort(key=lambda x: float(x.get("score", 0)), reverse=True)

        # Deduplicate
        deduped = []
        seen = set()
        for item in merged:
            key = (item.get("entity_type"), item.get("canonical_key"))
            if key not in seen:
                seen.add(key)
                deduped.append(item)

        return deduped[:limit]

    async def _search_project_a(self, query: str, parsed: ParsedLegalQuery, entity_type: str, limit: int) -> list[dict]:
        if not self.laws_client:
            return []

        results = []
        q_clean = query.strip()

        # 1. Exact Section Lookup
        if parsed.section:
            root_sec, _ = split_section_reference(parsed.section)
            def q_exact_sec():
                tbl = self.laws_client.table("document_chunks").select(
                    "id, act_name, section_number, section_title, content, status, document_type"
                ).eq("section_number", parsed.section)
                if parsed.act_keyword:
                    tbl = tbl.ilike("act_name", f"%{parsed.act_keyword.split()[1]}%")
                return tbl.limit(10).execute()

            try:
                res_sec = await asyncio.to_thread(q_exact_sec)
                for row in res_sec.data or []:
                    results.append({
                        "entity_type": "section",
                        "entity_id": str(row.get("id")),
                        "canonical_key": f"section:{normalize_act_alias(row.get('act_name',''))}:{row.get('section_number')}",
                        "slug": f"{normalize_act_alias(row.get('act_name',''))}-section-{row.get('section_number')}".lower(),
                        "title_en": f"Section {row.get('section_number')} — {row.get('act_name')}",
                        "title_bn": None,
                        "subtitle_en": row.get("section_title"),
                        "citation": f"{row.get('act_name')}, Section {row.get('section_number')}",
                        "act_name": row.get("act_name"),
                        "section_label": row.get("section_number"),
                        "court": None,
                        "case_number": None,
                        "document_date": None,
                        "legal_status": row.get("status", "Active"),
                        "verification_status": "verified",
                        "source_url": "https://bdlaws.minlaw.gov.bd",
                        "source_document_url": "https://bdlaws.minlaw.gov.bd",
                        "score": 1.00,
                        "match_type": "exact_section"
                    })
            except Exception:
                pass

        # 2. Act Title / Keyword Search on documents table
        if entity_type in {"all", "act", "laws"}:
            def q_acts():
                return self.laws_client.table("documents").select(
                    "id, title, metadata"
                ).ilike("title", f"%{q_clean}%").limit(5).execute()

            try:
                res_acts = await asyncio.to_thread(q_acts)
                for row in res_acts.data or []:
                    title = row.get("title", "")
                    score = 0.98 if title.lower() == q_clean.lower() else 0.90
                    results.append({
                        "entity_type": "act",
                        "entity_id": str(row.get("id")),
                        "canonical_key": f"act:{normalize_act_alias(title)}",
                        "slug": normalize_act_alias(title),
                        "title_en": title,
                        "title_bn": None,
                        "subtitle_en": "Principal Bangladesh Legislation",
                        "citation": title,
                        "act_name": title,
                        "section_label": None,
                        "court": None,
                        "case_number": None,
                        "document_date": None,
                        "legal_status": "In Force",
                        "verification_status": "verified",
                        "source_url": "https://bdlaws.minlaw.gov.bd",
                        "source_document_url": "https://bdlaws.minlaw.gov.bd",
                        "score": score,
                        "match_type": "act_title"
                    })
            except Exception:
                pass

        # 3. Keyword search on document_chunks (Sections, Amendments & Citizen Guides)
        def q_chunks():
            return self.laws_client.table("document_chunks").select(
                "id, act_name, section_number, section_title, content, status, document_type"
            ).ilike("section_title", f"%{q_clean}%").limit(10).execute()

        try:
            res_chunks = await asyncio.to_thread(q_chunks)
            for row in res_chunks.data or []:
                doc_type = "guide" if row.get("document_type") == "Citizen Guide" else "section"
                results.append({
                    "entity_type": doc_type,
                    "entity_id": str(row.get("id")),
                    "canonical_key": f"{doc_type}:{normalize_act_alias(row.get('act_name',''))}:{row.get('section_number')}",
                    "slug": f"{normalize_act_alias(row.get('act_name',''))}-{row.get('section_number')}".lower(),
                    "title_en": f"{row.get('section_title') or row.get('section_number')} ({row.get('act_name')})",
                    "title_bn": None,
                    "subtitle_en": row.get("section_title"),
                    "citation": f"{row.get('act_name')}, {row.get('section_number')}",
                    "act_name": row.get("act_name"),
                    "section_label": row.get("section_number"),
                    "court": None,
                    "case_number": None,
                    "document_date": None,
                    "legal_status": row.get("status", "Active"),
                    "verification_status": "verified",
                    "source_url": "https://bdlaws.minlaw.gov.bd",
                    "source_document_url": "https://bdlaws.minlaw.gov.bd",
                    "score": 0.85,
                    "match_type": "title_keyword"
                })
        except Exception:
            pass

        return results

    async def _search_project_b(self, query: str, parsed: ParsedLegalQuery, limit: int) -> list[dict]:
        if not self.cases_client:
            return []

        results = []
        q_clean = query.strip()

        # 1. Exact Citation or Case Number
        def q_cases():
            req = self.cases_client.table("case_chunks").select(
                "id, case_id, case_title, citation, court_division, year, judgment_date, bench_judges, subject_area, governing_statutes, ratio_decidendi, pdf_source_url"
            )
            if parsed.dlr_vol:
                req = req.ilike("citation", f"%{parsed.dlr_vol}%DLR%{parsed.dlr_page or ''}%")
            else:
                req = req.or_(f"case_title.ilike.%{q_clean}%,citation.ilike.%{q_clean}%,subject_area.ilike.%{q_clean}%")
            return req.limit(10).execute()

        try:
            res_cases = await asyncio.to_thread(q_cases)
            for row in res_cases.data or []:
                citation = row.get("citation", "")
                title = row.get("case_title", "")
                
                # Match score
                if parsed.dlr_vol and str(parsed.dlr_vol) in citation:
                    score = 0.99
                    m_type = "exact_citation"
                elif q_clean.lower() in title.lower():
                    score = 0.95
                    m_type = "exact_case_title"
                else:
                    score = 0.85
                    m_type = "subject_search"

                results.append({
                    "entity_type": "case",
                    "entity_id": str(row.get("id")),
                    "canonical_key": f"case:{normalize_act_alias(title)}:{row.get('year')}",
                    "slug": f"case-{normalize_act_alias(title)}-{row.get('year')}".lower(),
                    "title_en": title,
                    "title_bn": None,
                    "subtitle_en": f"{row.get('court_division')} · {citation}",
                    "citation": citation,
                    "act_name": None,
                    "section_label": None,
                    "court": f"Supreme Court of Bangladesh ({row.get('court_division')})",
                    "case_number": row.get("case_id"),
                    "document_date": str(row.get("judgment_date")) if row.get("judgment_date") else None,
                    "legal_status": "Settled Precedent",
                    "verification_status": "verified",
                    "source_url": row.get("pdf_source_url") or "https://supremecourt.gov.bd",
                    "source_document_url": row.get("pdf_source_url"),
                    "score": score,
                    "match_type": m_type
                })
        except Exception:
            pass

        return results
