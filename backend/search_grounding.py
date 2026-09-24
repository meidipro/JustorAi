from __future__ import annotations

import os
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger("justor.search_grounding")

GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "justorai-508321").strip()
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1").strip()

PRIORITY_LEGAL_DOMAINS = [
    "bdlaws.minlaw.gov.bd",
    "supremecourt.gov.bd",
    "dpp.gov.bd",
    "land.gov.bd",
    "nbr.gov.bd",
    "dncrp.portal.gov.bd",
    "minlaw.gov.bd"
]


class GoogleSearchGroundingService:
    """
    Live web search grounding powered by Google Cloud Vertex AI (Gemini 2.5 Flash Search Grounding).
    Allows JustorAI to verify latest statutory circulars, recent gazette amendments, and court updates
    without hallucinations, strictly separating live web sources from primary statutory law.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_CLOUD_API_KEY

    def _get_vertex_endpoint(self, model_name: str = "gemini-2.5-flash") -> str:
        return (
            f"https://aiplatform.googleapis.com/v1beta1/projects/{GCP_PROJECT_ID}"
            f"/locations/{VERTEX_LOCATION}/publishers/google/models/{model_name}:generateContent"
            f"?key={self.api_key}"
        )

    async def query_live_legal_web(
        self,
        query: str,
        language: str = "en",
        user_role: str = "professional",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes Google Search grounded generation on Vertex AI (Perplexity-grade synthesis).
        Returns the synthesized answer with inline factual grounding, domain sources, and follow-up legal queries.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_API_KEY is not configured.",
                "sources": []
            }

        try:
            from backend.legal_normalize import is_bengali_requested
            is_bn = is_bengali_requested(query, language)
        except Exception:
            is_bn = language.lower().startswith("bn")

        lang_instruction = (
            "🔴 MANDATORY LANGUAGE REQUIREMENT: STRICT BENGALI (বাংলা) 🔴\n"
            "Write the entire answer in natural, professional, authoritative Bengali (বাংলায় লিখুন).\n"
            "All explanations, headings, steps, and bullet points MUST be written in Bengali.\n"
            "Retain official English Act names, SRO circular numbers, and dates where appropriate."
            if is_bn else
            "Write the answer in fluent, authoritative, professional English."
        )

        role_instruction = (
            "Focus on legal doctrine, pedagogical breakdowns, and case precedents for law students."
            if user_role in {"student", "Law Student"} else
            "Provide rigorous legal analysis: controlling statutory provisions, SRO/circular dates and numbers, gazette references, and administrative scope for advocates and judicial counsel."
        )

        followup_title = "### প্রাসঙ্গিক আইনি প্রশ্ন" if is_bn else "### Related Follow-Up Questions"
        followup_eg = "- [প্রশ্ন ১]\n- [প্রশ্ন ২]\n- [প্রশ্ন ৩]" if is_bn else "- [Follow-up question 1]\n- [Follow-up question 2]\n- [Follow-up question 3]"

        prompt = (
            f"User Legal Query: {query}\n\n"
            f"{lang_instruction}\n"
            f"{role_instruction}\n"
            "You are JustorAI's Live Legal Search Engine. Provide a comprehensive, authoritative, Perplexity-style legal synthesis.\n"
            "INSTRUCTIONS:\n"
            "1. Ground your answer strictly in live Bangladeshi legal gazettes, government notices (land.gov.bd, minlaw.gov.bd, bdlaws.minlaw.gov.bd, nbr.gov.bd, supremecourt.gov.bd), and authoritative news reporting.\n"
            "2. State concrete facts with exact dates, circular numbers, SRO numbers, and official fee amounts in BDT.\n"
            "3. Format your response cleanly using Markdown headings, bold text, and bullet points.\n"
            f"4. At the very end of your response, provide exactly 3 proactive, highly relevant follow-up legal questions in the following format:\n"
            f"{followup_title}\n"
            f"{followup_eg}"
        )

        url = self._get_vertex_endpoint("gemini-2.5-flash")
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "tools": [
                {"googleSearch": {}}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=body)
                if resp.status_code != 200:
                    logger.error("Search grounding failed (%s): %s", resp.status_code, resp.text[:200])
                    return {
                        "status": "error",
                        "message": f"Search grounding failed with status {resp.status_code}",
                        "sources": []
                    }

                data = resp.json()
                candidate = data.get("candidates", [{}])[0]
                grounding_metadata = candidate.get("groundingMetadata", {})
                
                parts = candidate.get("content", {}).get("parts", [])
                answer_text = "".join([p.get("text", "") for p in parts if "text" in p]).strip()

                queries_run = grounding_metadata.get("webSearchQueries", [])
                chunks = grounding_metadata.get("groundingChunks", [])
                
                sources = []
                for idx, chunk in enumerate(chunks):
                    web_info = chunk.get("web", {})
                    if web_info:
                        uri = web_info.get("uri", "")
                        raw_title = web_info.get("title", "")
                        domain = ""
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(uri).hostname or ""
                            if domain.startswith("www."):
                                domain = domain[4:]
                        except Exception:
                            domain = uri

                        display_title = raw_title.strip()
                        if "vertexaisearch" in domain.lower() or "vertexaisearch" in display_title.lower():
                            domain = "gov.bd"
                            display_title = "Official Bangladesh Legal Source"
                        elif display_title.startswith("http://") or display_title.startswith("https://") or len(display_title) < 2:
                            display_title = domain or f"Source {idx + 1}"

                        sources.append({
                            "id": idx + 1,
                            "title": display_title,
                            "domain": domain,
                            "url": uri,
                            "trust_tier": "WEB_GROUNDED_SEARCH"
                        })

                # Extract related questions from answer_text
                related_questions: List[str] = []
                clean_answer = answer_text
                if "### Related Follow-Up Questions" in answer_text:
                    parts_split = answer_text.split("### Related Follow-Up Questions", 1)
                    clean_answer = parts_split[0].strip()
                    fq_block = parts_split[1].strip()
                    for line in fq_block.split("\n"):
                        line = line.strip()
                        if line.startswith("-") or line.startswith("*"):
                            q = line.lstrip("-* ").strip()
                            if q and len(q) > 5:
                                related_questions.append(q)
                elif "সম্পর্কিত" in answer_text and ("###" in answer_text or "##" in answer_text):
                    import re
                    parts_split = re.split(r'###?\s*.*সম্পর্কিত.*', answer_text, 1)
                    clean_answer = parts_split[0].strip()
                    if len(parts_split) > 1:
                        for line in parts_split[1].split("\n"):
                            line = line.strip()
                            if line.startswith("-") or line.startswith("*"):
                                q = line.lstrip("-* ").strip()
                                if q and len(q) > 5:
                                    related_questions.append(q)

                return {
                    "status": "ok",
                    "answer": clean_answer,
                    "raw_answer": answer_text,
                    "search_queries": queries_run,
                    "sources": sources,
                    "source_count": len(sources),
                    "related_questions": related_questions[:3]
                }

        except Exception as exc:
            logger.error("Live web search grounding exception: %s", exc)
            return {
                "status": "error",
                "message": str(exc),
                "sources": []
            }


# Global service instance
legal_search_grounding = GoogleSearchGroundingService()
