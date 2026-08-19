from __future__ import annotations

import json
import re
from datetime import date
from typing import Awaitable, Callable
from .legal_models import LegalRoute

ROUTER_PROMPT = """
You are the legal routing layer for Justor AI.

Jurisdiction is Bangladesh.
Your job is NOT to answer the legal question.

Identify:
1. legal issue(s)
2. likely primary statute(s)
3. likely section(s)
4. supporting statutes
5. whether case law is necessary
6. temporal intent

Authority roles:
CONTROLLING
SUPPORTING
GENERAL
BACKGROUND

Temporal modes:
CURRENT
AS_OF_DATE
HISTORICAL
COMPARE_VERSIONS
AMENDMENT_HISTORY

Rules:
- Do not invent section numbers.
- Candidate sections are suggestions only.
- The database independently verifies them.
- Prefer specific provisions over general provisions.
- Consider cross-statute relationships.
- Do not use Indian law.

Return JSON only:

{
  "jurisdiction": "Bangladesh",
  "legal_domain": "...",
  "issues": [
    {"issue": "...", "confidence": 0.95}
  ],
  "authorities": [
    {
      "act": "...",
      "sections": ["..."],
      "role": "CONTROLLING",
      "reason": "..."
    }
  ],
  "needs_case_law": false,
  "temporal_mode": "CURRENT",
  "as_of_date": null
}
"""


def extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Model returned empty response")
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError(f"Model did not return JSON: {text[:100]}")
    candidate = match.group(0)
    
    # 1. Clean control characters
    candidate = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', candidate)
    
    # 2. Fix trailing commas (e.g. [1, 2,] -> [1, 2])
    candidate = re.sub(r',\s*([\]}])', r'\1', candidate)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        try:
            import ast
            return ast.literal_eval(candidate)
        except Exception:
            # 3. Robust Regex Key-Value Extractor Fallback
            domain_m = re.search(r'"legal_domain"\s*:\s*"([^"]+)"', text)
            domain = domain_m.group(1) if domain_m else "General Law"
            
            authorities = []
            acts_m = re.findall(r'"act"\s*:\s*"([^"]+)"', text)
            secs_m = re.findall(r'"sections"\s*:\s*\[([^\]]*)\]', text)
            for i, act in enumerate(acts_m):
                raw_secs = secs_m[i] if i < len(secs_m) else ""
                secs = [s.strip(' "\'') for s in raw_secs.split(',') if s.strip(' "\'')]
                authorities.append({
                    "act": act,
                    "sections": secs,
                    "role": "CONTROLLING" if i == 0 else "SUPPORTING",
                    "reason": "extracted from model output"
                })
            
            issues = []
            issues_m = re.findall(r'"issue"\s*:\s*"([^"]+)"', text)
            for iss in issues_m:
                issues.append({"issue": iss, "confidence": 0.9})
            
            if authorities or issues:
                return {
                    "jurisdiction": "Bangladesh",
                    "legal_domain": domain,
                    "issues": issues or [{"issue": "Legal query analysis", "confidence": 0.9}],
                    "authorities": authorities,
                    "needs_case_law": True,
                    "temporal_mode": "CURRENT",
                    "as_of_date": date.today().isoformat()
                }
            raise ValueError(f"Failed to parse JSON: {str(exc)}")


BANGLADESH_ACT_CATALOG = [
    {
        "patterns": [r"transfer of property act", r"\btpa\b", r"সম্পত্তি হস্তান্তর আইন"],
        "canonical": "The Transfer of Property Act, 1882",
        "domain": "Property Law"
    },
    {
        "patterns": [r"registration act", r"রেজিস্ট্রেশন আইন", r"নিবন্ধন আইন"],
        "canonical": "The Registration Act, 1908",
        "domain": "Property Law"
    },
    {
        "patterns": [r"specific relief act", r"\bsr act\b", r"সুনির্দিষ্ট প্রতিকার আইন"],
        "canonical": "The Specific Relief Act, 1877",
        "domain": "Specific Relief"
    },
    {
        "patterns": [r"code of criminal procedure", r"\bcrpc\b", r"\bcr\.p\.c\b", r"ফৌজদারী কার্যবিধি", r"ফৌজদারি কার্যবিধি"],
        "canonical": "The Code of Criminal Procedure, 1898",
        "domain": "Criminal Procedure"
    },
    {
        "patterns": [r"penal code", r"\bpc\b", r"দণ্ডবিধি", r"দন্ডবিধি"],
        "canonical": "The Penal Code, 1860",
        "domain": "Criminal Law"
    },
    {
        "patterns": [r"code of civil procedure", r"\bcpc\b", r"\bc\.p\.c\b", r"দেওয়ানী কার্যবিধি", r"দেওয়ানী কার্যবিধি"],
        "canonical": "The Code of Civil Procedure, 1908",
        "domain": "Civil Procedure"
    },
    {
        "patterns": [r"constitution", r"সংবিধান"],
        "canonical": "The Constitution of the People's Republic of Bangladesh",
        "domain": "Constitutional Law"
    },
    {
        "patterns": [r"negotiable instruments act", r"\bni act\b", r"হস্তান্তরযোগ্য দলিল আইন"],
        "canonical": "The Negotiable Instruments Act, 1881",
        "domain": "Commercial & Banking Law"
    },
    {
        "patterns": [r"contract act", r"চুক্তি আইন"],
        "canonical": "The Contract Act, 1872",
        "domain": "Contract Law"
    },
    {
        "patterns": [r"sale of goods act", r"পণ্য বিক্রয় আইন"],
        "canonical": "The Sale of Goods Act, 1930",
        "domain": "Commercial Law"
    },
    {
        "patterns": [r"state acquisition and tenancy act", r"\bsata\b", r"রাষ্ট্রীয় অধিগ্রহণ ও প্রজাস্বত্ব আইন"],
        "canonical": "State Acquisition and Tenancy Act, 1950",
        "domain": "Land Revenue Law"
    },
    {
        "patterns": [r"muslim family laws ordinance", r"\bmflo\b", r"মুসলিম পারিবারিক আইন অধ্যাদেশ"],
        "canonical": "The Muslim Family Laws Ordinance, 1961",
        "domain": "Family Law"
    },
    {
        "patterns": [r"dissolution of muslim marriages act", r"\bdmma\b", r"মুসলিম বিবাহ বিচ্ছেদ আইন"],
        "canonical": "The Dissolution of Muslim Marriages Act, 1939",
        "domain": "Family Law"
    },
    {
        "patterns": [r"family courts act", r"family courts ordinance", r"পারিবারিক আদালত আইন"],
        "canonical": "Family Courts Act, 2023",
        "domain": "Family Law"
    },
    {
        "patterns": [r"labour act", r"labor act", r"\bbla\b", r"বাংলাদেশ শ্রম আইন", r"শ্রম আইন"],
        "canonical": "The Bangladesh Labour Act, 2006",
        "domain": "Labour Law"
    },
    {
        "patterns": [r"consumers['\s]*right", r"consumer protection", r"ভোক্তা অধিকার সংরক্ষণ আইন"],
        "canonical": "Consumers' Right Protection Act, 2009",
        "domain": "Consumer Protection"
    },
    {
        "patterns": [r"income tax act", r"income tax ordinance", r"আয়কর আইন", r"আয়কর আইন"],
        "canonical": "Income Tax Act, 2023",
        "domain": "Taxation Law"
    },
    {
        "patterns": [r"artha rin adalat", r"money loan court", r"অর্থ ঋণ আদালত আইন"],
        "canonical": "Artha Rin Adalat Ain, 2003",
        "domain": "Commercial & Banking Law"
    },
    {
        "patterns": [r"limitation act", r"তামাদি আইন"],
        "canonical": "The Limitation Act, 1908",
        "domain": "Limitation Law"
    },
]


def fast_exact_route(query: str) -> Optional[LegalRoute]:
    from .legal_models import CandidateAuthority, LegalIssue
    from .legal_dictionary import expand_query_with_dictionary, normalize_bengali_text

    norm_q = normalize_bengali_text(query).lower()

    matched_acts = []
    detected_domain = "General Law"
    for cat in BANGLADESH_ACT_CATALOG:
        for pat in cat["patterns"]:
            if re.search(pat, norm_q, re.IGNORECASE):
                if cat["canonical"] not in matched_acts:
                    matched_acts.append(cat["canonical"])
                    detected_domain = cat["domain"]
                break

    explicit_sections = []
    for m in re.finditer(r'(?:sections?|sec\.?|ধারা|ধারাসমূহ)\s*([0-9A-Za-z\(\),\s\band\b]+)', norm_q, re.IGNORECASE):
        chunk = m.group(1)
        found_nums = re.findall(r'\b[0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*\b', chunk)
        for num in found_nums:
            if num not in explicit_sections and num not in {"1860", "1872", "1877", "1881", "1882", "1898", "1908", "1930", "1939", "1950", "1961", "2006", "2009", "2023"}:
                explicit_sections.append(num)
    if not explicit_sections:
        explicit_sections = re.findall(r'(?:section|sec\.?|ধারা)\s*([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*)', norm_q, re.IGNORECASE)

    explicit_articles = re.findall(r'(?:articles?|art\.?|অনুচ্ছেদ)\s*([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*)', norm_q, re.IGNORECASE)
    explicit_orders = re.findall(r'(?:orders?|আদেশ)\s*([0-9IVXLCDM]+)(?:\s*,?\s*(?:rules?|বিধি|নিয়ম|নিয়ম)\s*([0-9]+))?', norm_q, re.IGNORECASE)

    dict_match = expand_query_with_dictionary(query)
    act_sections_map = dict_match.get("act_to_sections", {})

    if matched_acts:
        authorities = []
        for i, act in enumerate(matched_acts):
            secs = []
            if "constitution" in act.lower():
                secs = [f"Article {a}" for a in explicit_articles] + explicit_articles
            elif "civil procedure" in act.lower() and explicit_orders:
                for ord_num, rule_num in explicit_orders:
                    if rule_num:
                        secs.append(f"Order {ord_num}, Rule {rule_num}")
                    secs.append(f"Order {ord_num}")
                    secs.append(ord_num)
            if not secs:
                secs = list(explicit_sections) or list(explicit_articles)
            
            for s in act_sections_map.get(act, []):
                if s not in secs:
                    secs.append(s)

            authorities.append(
                CandidateAuthority(
                    act=act,
                    sections=secs,
                    role="CONTROLLING" if i == 0 else "SUPPORTING",
                    reason="explicit Act in query"
                )
            )

        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain=detected_domain,
            issues=[LegalIssue(issue=f"{matched_acts[0]} statutory provisions", confidence=0.98)],
            authorities=authorities,
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    dict_match = expand_query_with_dictionary(query)
    if dict_match.get("candidate_acts"):
        candidate_acts = dict_match["candidate_acts"]
        candidate_secs = dict_match.get("candidate_sections", [])
        domain = dict_match.get("domains", ["General Law"])[0] if dict_match.get("domains") else "General Law"

        authorities = []
        act_sections_map = dict_match.get("act_to_sections", {})
        for i, act in enumerate(candidate_acts):
            authorities.append(
                CandidateAuthority(
                    act=act,
                    sections=act_sections_map.get(act, candidate_secs),
                    role="CONTROLLING" if i == 0 else "SUPPORTING",
                    reason="canonical dictionary candidate"
                )
            )

        issues_list = [
            LegalIssue(issue=f"{c} statutory provisions", confidence=0.95)
            for c in dict_match.get("concepts", ["Statutory legal provisions"])
        ]

        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain=domain,
            issues=issues_list or [LegalIssue(issue="Statutory legal provisions", confidence=0.95)],
            authorities=authorities,
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    if explicit_articles:
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Constitutional Law",
            issues=[LegalIssue(issue="Constitutional Article interpretation", confidence=0.95)],
            authorities=[
                CandidateAuthority(
                    act="The Constitution of the People's Republic of Bangladesh",
                    sections=[f"Article {explicit_articles[0]}", explicit_articles[0]],
                    role="CONTROLLING",
                    reason="explicit constitutional article"
                )
            ],
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    if explicit_orders:
        ord_num = explicit_orders[0][0]
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Civil Procedure",
            issues=[LegalIssue(issue="Civil Procedure Code Order provisions", confidence=0.95)],
            authorities=[
                CandidateAuthority(
                    act="The Code of Civil Procedure, 1908",
                    sections=[f"Order {ord_num}", ord_num],
                    role="CONTROLLING",
                    reason="explicit CPC order"
                )
            ],
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    return None


class LegalRouter:
    """Zero-shot LLM & Fast deterministic router for legal queries."""

    def __init__(
        self,
        llm_call: Optional[Callable[[list[dict]], Awaitable[str]]] = None,
        client: Optional[Any] = None,
        model: str = "openrouter/google/gemini-2.5-flash",
    ):
        self.llm_call = llm_call
        self.client = client
        self.model = model

    async def route(self, query: str) -> LegalRoute:
        fast_route = fast_exact_route(query)
        if fast_route:
            return fast_route

        if self.llm_call:
            raw = await self.llm_call([
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": query},
            ])
        elif self.client:
            user_message = f"Legal Question: {query}\nProvide routing analysis in JSON."
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ROUTER_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.0,
            )
            raw = response.choices[0].message.content
        else:
            raise RuntimeError("LegalRouter has no llm_call or client configured")

        parsed = extract_json(raw)
        route = LegalRoute.model_validate(parsed)
        if route.temporal_mode == "CURRENT" and route.as_of_date is None:
            route.as_of_date = date.today()
        return route
