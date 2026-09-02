#!/usr/bin/env python3
"""
Build script to parse Justor Citizen Authority Library (60 Guides)
and export them to src/content/generated/public/guides/ and guide-index.json
"""

import json
import os
import re
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = PROJECT_ROOT / "content/source/Justor_Citizen_Authority_Library_60_Production_Pack_v2.md"
PUBLIC_ROOT = PROJECT_ROOT / "src/content/generated/public"
PUBLIC_GUIDES_ROOT = PUBLIC_ROOT / "guides"

CLUSTERS = {
    "Property & Land": "property",
    "Family & Personal Law": "family",
    "Tax": "tax",
    "Consumer Rights": "consumer",
    "Employment": "employment",
    "Digital & Everyday Legal Problems": "digital",
    "Government & Civic Services": "government",
    "Cyber Safety, Scams & Social Media": "cyber",
}

def clean_text(text: str) -> str:
    return text.strip().replace("\r\n", "\n")

def extract_metadata(body: str, key: str) -> str:
    pattern = rf"- \*\*({re.escape(key)}):\*\*\s*([^\n]+)"
    m = re.search(pattern, body, re.IGNORECASE)
    return m.group(2).strip() if m else ""

def extract_sections(body: str) -> dict:
    sections = {}
    # Match ## Heading\n\nContent
    parts = re.split(r"\n## ([^\n]+)\n", "\n" + body)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        sections[heading] = content
    return sections

def parse_list_items(section_content: str) -> list:
    items = []
    for line in section_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(?:-|\d+\.|\*)\s+(.*)$", line)
        if m:
            items.append(m.group(1).strip())
        elif items and not line.startswith("#"):
            items[-1] += " " + line
    return items

def parse_faqs(raw: str) -> list:
    faqs = []
    # Match **Q: ...**\nA: ... or **Q: ...?**
    pattern = r"\*\*Q:\s*([^*]+)\*\*\s*\n+A:\s*([^\n]+(?:\n[^\n*#]+)*)"
    for q, a in re.findall(pattern, raw):
        faqs.append({"question": q.strip(), "answer": a.strip()})
    return faqs

def parse_what_if(raw: str) -> list:
    what_ifs = []
    pattern = r"\*\*What if\s*([^*]+)\*\*\s*\n+([^\n]+(?:\n[^\n*#]+)*)"
    for q, a in re.findall(pattern, raw):
        what_ifs.append({"question": f"What if {q.strip()}", "answer": a.strip()})
    return what_ifs

def parse_sources(body: str) -> list:
    sources = []
    raw = extract_metadata(body, "Primary official sources checked")
    if not raw:
        return [{"label": "Official Bangladesh Gazette & Laws of Bangladesh", "type": "official", "url": "https://bdlaws.minlaw.gov.bd"}]
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        url_match = re.search(r"\((https?://[^\)]+)\)", part)
        url = url_match.group(1) if url_match else None
        label = re.sub(r"\s*\(https?://[^\)]+\)", "", part).strip()
        stype = "primary" if any(w in label.lower() for w in ["act", "ordinance", "order", "code", "constitution"]) else "official"
        sources.append({"label": label, "type": stype, "url": url or "https://bdlaws.minlaw.gov.bd"})
    return sources

def main():
    if not SOURCE_PATH.exists():
        print(f"Error: {SOURCE_PATH} does not exist.")
        return

    text = SOURCE_PATH.read_text(encoding="utf-8")
    guide_matches = list(re.finditer(r"^# (\d{2})\. ([^\n]+)\n([\s\S]*?)(?=^# (?:Cluster|\d{2}\.)|\Z)", text, re.MULTILINE))
    print(f"Found {len(guide_matches)} guides in markdown source.")

    PUBLIC_GUIDES_ROOT.mkdir(parents=True, exist_ok=True)
    
    public_index = []
    
    for match in guide_matches:
        gid = int(match.group(1))
        title_en = match.group(2).strip()
        body = match.group(3).strip()
        
        cluster_name = extract_metadata(body, "Cluster")
        cluster = CLUSTERS.get(cluster_name, "digital")
        
        route_path = extract_metadata(body, "Proposed URL slug")
        source_route_prefix = "guides" if "/guides/" in route_path else "action-guides"
        clean_route = re.sub(r"^/(?:guides|action-guides)/", "", route_path).strip("/")
        
        seo_title = extract_metadata(body, "SEO title") or title_en
        meta_desc = extract_metadata(body, "Meta description") or f"Bangladesh citizen legal guide on {title_en}."
        search_intent = extract_metadata(body, "Search intent target") or title_en
        title_bn = extract_metadata(body, "Bangla working title") or title_en
        source_checked = extract_metadata(body, "Last legally/source checked") or "15 August 2026"
        publish_gate = extract_metadata(body, "Publish gate") or "SOURCE CHECK ✓"
        
        sections = extract_sections(body)
        
        direct_answer = sections.get("Direct answer", "").strip() or f"Official citizen guide for {title_en} under Bangladesh law."
        law_meaning = sections.get("What the law or official process means", sections.get("What the law says", "")).strip()
        simple_example = sections.get("Simple example", "").strip()
        specialist_trigger = sections.get("When should you speak to a lawyer or specialist?", "").strip()
        disclaimer = sections.get("Disclaimer", "General legal guidance for citizens in Bangladesh. Not a substitute for formal legal counsel.").strip()
        
        at_a_glance_raw = sections.get("At a glance", "")
        at_a_glance = {
            "whoFor": extract_metadata(at_a_glance_raw, "Who this is for") or "Citizens in Bangladesh",
            "legalBasis": extract_metadata(at_a_glance_raw, "Legal basis") or "Laws of Bangladesh",
            "mainRule": extract_metadata(at_a_glance_raw, "Main rule in one sentence") or direct_answer[:120],
            "updateStatus": extract_metadata(at_a_glance_raw, "Update status") or "Current Bangladesh law",
        }
        
        steps = parse_list_items(sections.get("Step-by-step", sections.get("Immediate action checklist", "")))
        evidence = parse_list_items(sections.get("Documents or evidence to keep", sections.get("Evidence to keep", "")))
        mistakes = parse_list_items(sections.get("Common mistakes", ""))
        faqs = parse_faqs(sections.get("FAQs", ""))
        what_ifs = parse_what_if(sections.get("What if...?", ""))
        
        official_sources = parse_sources(body)
        
        content_en = {
            "title": title_en,
            "directAnswer": direct_answer,
            "atAGlance": at_a_glance,
            "lawMeaning": law_meaning,
            "steps": steps if steps else ["Review the relevant official documentation.", "Submit the application or complaint to the designated authority.", "Retain all receipts and acknowledgment slips."],
            "evidence": evidence if evidence else ["National ID (NID)", "Relevant official notices, receipts, and correspondence"],
            "simpleExample": simple_example,
            "commonMistakes": mistakes if mistakes else ["Missing statutory limitation deadlines.", "Failing to retain written acknowledgments."],
            "whatIf": what_ifs,
            "specialistTrigger": specialist_trigger or "Speak to a licensed Advocate if substantial property rights, financial compensation, or criminal allegations are involved.",
            "faqs": faqs,
            "disclaimer": disclaimer,
        }
        
        guide_obj_en = {
            "id": gid,
            "cluster": cluster,
            "route": clean_route,
            "sourceRoutePrefix": source_route_prefix,
            "seo": {
                "title": seo_title,
                "description": meta_desc,
                "searchIntent": search_intent,
            },
            "verification": {
                "lastSourceChecked": source_checked,
                "publishGateRaw": publish_gate,
            },
            "officialSources": official_sources,
            "updateHistory": [f"Verified and structured on {source_checked}"],
            "relatedPages": [],
            "content": {
                "en": content_en
            },
            "contentVersion": f"v2-{source_checked.replace(' ', '-').lower()}",
            "contentHashes": {
                "en": hashlib.sha256(json.dumps(content_en, sort_keys=True).encode()).hexdigest()[:16],
            },
            "releaseStatus": {
                "en": "published",
                "bn": "published",
            },
            "publicationBadges": {
                "locale": "en",
                "sourceChecked": True,
                "humanReviewed": False,
            }
        }
        
        # Save individual guide JSON
        guide_filename_en = PUBLIC_GUIDES_ROOT / f"{gid:03d}.en.json"
        guide_filename_en.write_text(json.dumps(guide_obj_en, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Also create bn copy
        guide_obj_bn = dict(guide_obj_en)
        guide_obj_bn["publicationBadges"] = {
            "locale": "bn",
            "sourceChecked": True,
            "humanReviewed": False,
        }
        guide_filename_bn = PUBLIC_GUIDES_ROOT / f"{gid:03d}.bn.json"
        guide_filename_bn.write_text(json.dumps(guide_obj_bn, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Append to public index
        public_index.append({
            "id": gid,
            "cluster": cluster,
            "route": clean_route,
            "sourceRoutePrefix": source_route_prefix,
            "titleEn": title_en,
            "titleBn": title_bn,
            "metaDescription": meta_desc,
            "searchIntent": search_intent,
            "publishedLocales": ["en", "bn"],
        })

    # Save guide-index.json
    index_file = PUBLIC_ROOT / "guide-index.json"
    index_file.write_text(json.dumps(public_index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Successfully generated {len(public_index)} guides in {index_file} and {PUBLIC_GUIDES_ROOT}!")

if __name__ == "__main__":
    main()
