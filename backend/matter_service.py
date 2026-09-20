from __future__ import annotations

import os
import io
import re
import json
import base64
import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env.local"))

logger = logging.getLogger("justor.matter")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "justorai-508321").strip()
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1").strip()


def _clean_json_text(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extracts JSON dictionary from raw model text."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback regex for outermost { ... }
        m = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None


class JustorMatterService:
    """
    Justor Matter Intelligence Service (Chamber OS)
    Empowers legal practitioners with workflow automation:
    1. Lawyer Dictaphone: Voice/text notes -> structured matter notes.
    2. Consultation Audio: Ingest audio -> transcript + legal summary + missing questions.
    3. Legal Document & Judgment Summarization: 60-second case breakdown with Ratio Decidendi.
    4. Matter Chronology & Timeline: Automated date-ordered timeline with statutory limitation alerts.
    5. One-Click Hearing Preparation Pack: Court-ready hearing objectives, evidence checklist & witness questions.
    6. Matter Consistency Checker & Evidence Matrix: Cross-document contradiction audit & proof gaps.
    7. Source-Linked Legal Memo Generator: Formal advocate IRAC legal memorandum with statutory authorities.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key
        self._llm_handler = None

    def set_llm_handler(self, handler):
        """Allows injecting Justor's full multi-model fallback cascade from backend.py."""
        self._llm_handler = handler

    @property
    def api_key(self) -> str:
        if self._explicit_key:
            return self._explicit_key
        return (
            os.getenv("GEMINI_API_KEY", "").strip()
            or os.getenv("GOOGLE_CLOUD_API_KEY", "").strip()
            or os.getenv("GOOGLE_API_KEY", "").strip()
        )

    def _get_api_urls(self, model_name: str = "gemini-2.5-flash") -> list[str]:
        """Returns primary Google AI Studio endpoint."""
        urls = []
        if self.api_key:
            urls.append(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                f"?key={self.api_key}"
            )
        return urls

    async def _call_gemini_json(self, contents: list, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Invokes Gemini 2.5 Flash with JSON schema response and fallback cascade."""
        urls = self._get_api_urls("gemini-2.5-flash")

        # Prepare direct payload for Gemini
        body: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 6000,
                "responseMimeType": "application/json",
            }
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        # Try direct Gemini endpoint
        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    resp = await client.post(url, json=body)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                            parsed = _clean_json_text(text)
                            if parsed:
                                return parsed
                    else:
                        logger.warning(f"Gemini API returned {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"Error calling Gemini endpoint ({url[:40]}...): {e}")
                continue

        # Fallback to injected multi-model LLM handler (Groq/OpenRouter/DashScope)
        if self._llm_handler:
            try:
                prompt_text = ""
                for c in contents:
                    for p in c.get("parts", []):
                        if "text" in p:
                            prompt_text += p["text"] + "\n"
                
                json_enforcing_prompt = (
                    (system_prompt or "") + "\n\n"
                    "CRITICAL: You MUST respond ONLY in valid, strictly parsable JSON. Do not include introductory text or Markdown code blocks."
                )
                res = await self._llm_handler(prompt_text, json_enforcing_prompt)
                parsed = _clean_json_text(res)
                if parsed:
                    return parsed
            except Exception as ex:
                logger.warning(f"Injected fallback LLM handler failed in matter_service: {ex}")

        return None

    def _extract_matter_dossier(self, matter: Dict[str, Any]) -> str:
        """Serializes an entire legal matter into a cohesive factual dossier."""
        lines: List[str] = []
        lines.append(f"MATTER TITLE: {matter.get('title', 'Untitled Matter')}")
        if matter.get("caseNumber"): lines.append(f"CASE NUMBER: {matter.get('caseNumber')}")
        if matter.get("court"): lines.append(f"COURT: {matter.get('court')}")
        lines.append(f"CLIENT: {matter.get('clientName', 'Unknown Client')}")
        lines.append(f"MATTER TYPE: {matter.get('matterType', 'General Legal Matter')}")
        if matter.get("summary"): lines.append(f"SUMMARY: {matter.get('summary')}")

        # Notes
        notes = matter.get("notes", [])
        if isinstance(notes, list) and notes:
            lines.append("\n=== ADVOCATE NOTES & DICTATION ===")
            for idx, n in enumerate(notes, 1):
                if not isinstance(n, dict):
                    continue
                data = n.get("data") if isinstance(n.get("data"), dict) else n
                lines.append(f"Note #{idx} ({n.get('createdAt', '')}):")
                if n.get("text"): lines.append(f"  Note text: {n.get('text')}")
                if data.get("client_name"): lines.append(f"  Client: {data['client_name']}")
                if data.get("opponent_name"): lines.append(f"  Opponent: {data['opponent_name']}")
                if data.get("claim_amount"): lines.append(f"  Claim Amount: {data['claim_amount']}")
                if data.get("property_details"): lines.append(f"  Property: {data['property_details']}")
                if data.get("dispute_summary"): lines.append(f"  Summary: {data['dispute_summary']}")
                if data.get("statutory_provisions") and isinstance(data["statutory_provisions"], list):
                    lines.append(f"  Statutes: {', '.join(str(x) for x in data['statutory_provisions'])}")
                if data.get("next_actions") and isinstance(data["next_actions"], list):
                    lines.append(f"  Actions: {', '.join(str(x) for x in data['next_actions'])}")

        # Consultations
        consultations = matter.get("consultations", [])
        if isinstance(consultations, list) and consultations:
            lines.append("\n=== CLIENT CONSULTATION AUDIO TRANSCRIPTS ===")
            for idx, c in enumerate(consultations, 1):
                if not isinstance(c, dict):
                    continue
                data = c.get("data") if isinstance(c.get("data"), dict) else c
                lines.append(f"Consultation #{idx} ({c.get('filename', '')}):")
                if data.get("consultation_summary"): lines.append(f"  Summary: {data['consultation_summary']}")
                if data.get("client_facts") and isinstance(data["client_facts"], list):
                    lines.append(f"  Client Facts: {' | '.join(str(x) for x in data['client_facts'])}")
                if data.get("documents_mentioned") and isinstance(data["documents_mentioned"], list):
                    lines.append(f"  Documents Mentioned: {', '.join(str(x) for x in data['documents_mentioned'])}")
                if data.get("red_flags_and_risks") and isinstance(data["red_flags_and_risks"], list):
                    lines.append(f"  Red Flags: {', '.join(str(x) for x in data['red_flags_and_risks'])}")
                if data.get("transcript"): lines.append(f"  Transcript Snippet: {str(data['transcript'])[:600]}...")

        # Document Summaries
        summaries = matter.get("summaries", [])
        if isinstance(summaries, list) and summaries:
            lines.append("\n=== LEGAL DOCUMENTS & JUDGMENTS IN FILE ===")
            for idx, s in enumerate(summaries, 1):
                if not isinstance(s, dict):
                    continue
                data = s.get("data") if isinstance(s.get("data"), dict) else s
                lines.append(f"Document #{idx} ({s.get('filename', '')}):")
                if data.get("case_title"): lines.append(f"  Title: {data['case_title']}")
                if data.get("court"): lines.append(f"  Court/Bench: {data['court']} {data.get('bench', '')}")
                if data.get("facts_brief"): lines.append(f"  Facts: {data['facts_brief']}")
                if data.get("legal_issues") and isinstance(data["legal_issues"], list):
                    lines.append(f"  Issues: {' | '.join(str(x) for x in data['legal_issues'])}")
                if data.get("ratio_decidendi"): lines.append(f"  Ratio Decidendi: {data['ratio_decidendi']}")
                if data.get("operative_order"): lines.append(f"  Operative Order: {data['operative_order']}")

        # Chronology
        chronology = matter.get("chronology")
        timeline: List[Dict[str, Any]] = []
        alerts: List[Dict[str, Any]] = []
        if isinstance(chronology, dict):
            timeline = chronology.get("timeline", []) if isinstance(chronology.get("timeline"), list) else []
            alerts = chronology.get("limitation_alerts", []) if isinstance(chronology.get("limitation_alerts"), list) else []
        elif isinstance(chronology, list):
            timeline = chronology

        if timeline:
            lines.append("\n=== MATTER CHRONOLOGY & TIMELINE ===")
            for event in timeline:
                if isinstance(event, dict):
                    d_str = event.get("date_str") or event.get("date") or "Date"
                    title = event.get("title") or event.get("event") or ""
                    desc = event.get("description") or event.get("significance") or ""
                    imp = event.get("importance", "standard")
                    lines.append(f"  [{d_str}] {title}: {desc} (Importance: {imp})")

        if alerts:
            lines.append("\n=== STATUTORY LIMITATION ALERTS ===")
            for alert in alerts:
                if isinstance(alert, dict):
                    lines.append(f"  - {alert.get('provision', '')}: {str(alert.get('status', '')).upper()} -> {alert.get('warning', '')}")

        return "\n".join(lines)

    async def parse_voice_dictation(
        self,
        text: str,
        language: str = "bn"
    ) -> Dict[str, Any]:
        """Parses raw dictated notes into a structured matter note card."""
        is_bn = language.lower().startswith("bn")
        system_instruction = (
            "You are Justor AI's Senior Chamber Practice Assistant for Bangladesh Advocates.\n"
            "You parse an advocate's raw spoken notes or dictation into a clean, structured matter file.\n"
            "Identify:\n"
            "- Client name and opposing party\n"
            "- Legal dispute type (e.g. NI Act Cheque Dishonour, Specific Relief Title/Eviction, Section 498 CrPC Bail, Family MFLO)\n"
            "- Disputed amount (BDT / Taka) or property description (Mouza, Khatian, Dag)\n"
            "- Crucial dates mentioned\n"
            "- Controlling Bangladesh statutes and sections\n"
            "- Crucial questions the advocate still needs to ask the client\n"
            "- Immediate actionable next steps\n"
            + ("Output all explanatory text in natural Bengali (বাংলা)." if is_bn else "Output in clear legal English.")
        )

        prompt = f"Advocate's dictated note:\n\"\"\"\n{text}\n\"\"\"\n\nReturn structured JSON with keys: client_name, opponent_name, matter_type, dispute_summary, claim_amount, property_details, key_dates (array of objects with date, event, note), statutory_provisions (array of string names of acts and sections), missing_questions (array of string questions to ask client), next_actions (array of string action points)."

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        result = await self._call_gemini_json(contents, system_instruction)

        if not result:
            return {
                "status": "error",
                "message": "Failed to parse dictation.",
                "data": {
                    "client_name": "Unknown",
                    "dispute_summary": text,
                    "statutory_provisions": []
                }
            }

        return {
            "status": "ok",
            "data": result
        }

    async def summarize_consultation_audio(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/mp3",
        filename: str = "consultation.mp3",
        language: str = "bn"
    ) -> Dict[str, Any]:
        """Multimodal audio ingestion for client consultations."""
        is_bn = language.lower().startswith("bn")
        b64_data = base64.b64encode(audio_bytes).decode("utf-8")

        system_instruction = (
            "You are Justor AI's Multimodal Consultation Analyst for Bangladesh Legal Chambers.\n"
            "Analyze the client consultation audio recording (in Bengali, English, or mixed).\n"
            "Produce an exhaustive legal breakdown formatted strictly as JSON with keys:\n"
            "- matter_title: concise title of the dispute\n"
            "- transcript: verbatim spoken transcript\n"
            "- consultation_summary: 2-3 paragraph executive summary\n"
            "- client_facts: array of material facts alleged by client\n"
            "- documents_mentioned: array of deeds, khatians, receipts, notices, cheques, memos mentioned\n"
            "- crucial_dates: array of objects {date, event}\n"
            "- statutory_provisions: controlling Bangladesh acts and sections\n"
            "- red_flags_and_risks: weaknesses in client's case or potential procedural bars\n"
            "- questions_to_ask_client: key missing facts to elicit\n"
            + ("Write summary and notes in natural legal Bengali (বাংলা)." if is_bn else "Write in clear legal English.")
        )

        prompt = f"Analyze client consultation recording: {filename}."

        contents = [{
            "role": "user",
            "parts": [
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": b64_data
                    }
                },
                {"text": prompt}
            ]
        }]

        result = await self._call_gemini_json(contents, system_instruction)
        if not result:
            return {
                "status": "error",
                "message": "Failed to analyze consultation audio.",
                "data": {}
            }

        return {
            "status": "ok",
            "data": result
        }

    async def summarize_legal_document(
        self,
        text_content: str,
        filename: str = "document.pdf",
        language: str = "bn"
    ) -> Dict[str, Any]:
        """Case in 60 Seconds: judgment/petition summarization with Ratio Decidendi."""
        is_bn = language.lower().startswith("bn")
        system_instruction = (
            "You are Justor AI's Supreme Court & District Court Judgment Analyst for Bangladesh.\n"
            "Break down the judgment, order, or petition into a 'Case in 60 Seconds' executive briefing.\n"
            "Return JSON with:\n"
            "- case_title: Parties involved\n"
            "- court: Court jurisdiction\n"
            "- bench: Presiding judge(s)\n"
            "- case_number: e.g. Criminal Revision No. 123 of 2024\n"
            "- decision_date: Date delivered\n"
            "- facts_brief: Material facts in 3-4 sentences\n"
            "- legal_issues: Array of core points of law\n"
            "- petitioner_arguments: Array of key arguments\n"
            "- respondent_arguments: Array of counter arguments\n"
            "- statutes_cited: Acts and sections cited\n"
            "- precedents_cited: Reported decisions (DLR / BLD / BLC)\n"
            "- ratio_decidendi: The authoritative principle of law established\n"
            "- operative_order: The final decree or direction\n"
            "- study_mode_firac: Object with {facts, issue, rule, analysis, conclusion}\n"
            + ("Output all explanatory text in legal Bengali (বাংলা)." if is_bn else "Output in legal English.")
        )

        prompt = f"Document ({filename}):\n\"\"\"\n{text_content[:25000]}\n\"\"\""
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        result = await self._call_gemini_json(contents, system_instruction)

        if not result:
            return {
                "status": "error",
                "message": "Failed to summarize legal document.",
                "data": {}
            }

        return {
            "status": "ok",
            "data": result
        }

    async def extract_matter_chronology(
        self,
        events_text: str,
        language: str = "bn"
    ) -> Dict[str, Any]:
        """Extracts date-ordered timeline and highlights statutory limitation risks."""
        is_bn = language.lower().startswith("bn")
        prompt = (
            "You are Justor AI's Legal Chronology & Limitation Specialist for Bangladesh Law.\n"
            "Extract all chronological events, dates, agreements, notices, and occurrences from this matter text:\n"
            f"\"\"\"\n{events_text}\n\"\"\"\n\n"
            "MANDATORY STATUTORY AUTHORITIES & TIME LIMITS TO ENFORCE:\n"
            "1. Negotiable Instruments Act, 1881 (Section 138 timeline & 2026 Amendment):\n"
            "   - Bank Memo: Cheque must be presented within 6 months of issue date.\n"
            "   - Statutory Notice: Legal notice in writing must be served within 30 days of receiving the dishonour memo (s.138(1)(b)).\n"
            "   - 15-Day Payment Window & PREMATURE FILING BAR (s.138(1)(c)): The drawer has 15 full days from receipt of notice to pay. "
            "CAUSE OF ACTION ARISES ONLY ON DAY 16. A complaint filed before the 15-day period expires is legally premature, void ab initio, and liable to be quashed under s.561A CrPC. You MUST flag any premature filing as a fatal defect!\n"
            "   - Complaint Deadline: Complaint must be filed within 30 days after the 15-day notice window expires (s.141(b)).\n"
            "   - 2026 NI Act Amendment (Tk 5 Lakh Threshold & ADR): For cheque claims up to BDT 5,00,000 (Tk 5 lakh), mandatory ADR/mediation and summary recovery procedure applies. Flag whether claim is above/below Tk 5 lakh.\n"
            "2. Code of Civil Procedure, 1908 (Order XXXIX Rules 1, 2, 3 - Injunctions):\n"
            "   - Assess the 3-part test for temporary injunction: (a) Prima facie case, (b) Balance of convenience/inconvenience, (c) Irreparable loss/injury.\n"
            "   - Order XXXIX Rule 3: Ex-parte ad-interim injunction requires showing immediate irreparable harm, otherwise prior notice is mandatory.\n"
            "3. Specific Relief Act, 1877 (Section 9 Dispossession):\n"
            "   - Summary suit for recovery of possession must be filed within 6 MONTHS from the date of dispossession without consent. Title is not investigated.\n"
            "4. The Limitation Act, 1908:\n"
            "   - Article 113/115: 3 years for suit for specific performance or breach of contract.\n"
            "   - Article 142/144: 12 years for suit for possession based on title or adverse possession.\n\n"
            "Tasks:\n"
            "1. Identify every date or time milestone mentioned (even relative ones like 'two weeks later').\n"
            "2. Order all events chronologically from earliest to most recent.\n"
            "3. Tag each event's importance: 'critical' (e.g. cheque dishonour, notice served, premature filing, suit filing, dispossession) or 'standard'.\n"
            "4. Calculate exact statutory limitation windows and identify any STATUTORY LIMITATION RISKS or DEFECTS (especially premature NI Act filings or s.9 expiry).\n\n"
            "Return valid JSON with keys:\n"
            "{\n"
            '  "matter_title": "string",\n'
            '  "timeline": [\n'
            '    {\n'
            '      "date_str": "string (e.g. 12 August 2024)",\n'
            '      "standard_date": "YYYY-MM-DD or null",\n'
            '      "title": "string event title",\n'
            '      "description": "string detailed fact",\n'
            '      "importance": "critical | standard",\n'
            '      "source_reference": "string or null"\n'
            '    }\n'
            '  ],\n'
            '  "limitation_alerts": [\n'
            '    {\n'
            '      "provision": "Act and Section / Order name",\n'
            '      "rule": "Statutory time limit or legal test",\n'
            '      "status": "expired | urgent | active | compliant | premature_defect",\n'
            '      "warning": "Detailed risk advice (including 2026 amendment threshold & premature bar if applicable)"\n'
            '    }\n'
            '  ],\n'
            '  "summary": "2-3 sentence overview of timeline and statutory standing"\n'
            "}"
        )

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        result = await self._call_gemini_json(contents)

        if not result:
            return {
                "status": "error",
                "message": "Failed to extract matter chronology.",
                "data": {}
            }

        return {
            "status": "ok",
            "data": result
        }

    # ════════════════════════════════════════════════════════════════════════════
    # NEW CHAMBER SUITE 2.0 CAPABILITIES
    # ════════════════════════════════════════════════════════════════════════════

    async def generate_hearing_pack(
        self,
        matter: Dict[str, Any],
        hearing_type: str = "general",
        language: str = "bn"
    ) -> Dict[str, Any]:
        """
        One-Click Hearing Preparation Pack:
        Synthesizes the entire matter file into an executive court brief for tomorrow's hearing.
        Includes tactical objectives, proof checklist, opposing argument anticipations, and cross-examination questions.
        """
        is_bn = language.lower().startswith("bn")
        dossier = self._extract_matter_dossier(matter)

        system_instruction = (
            "You are Justor AI's Senior Court Trial Strategist for Bangladesh Advocates.\n"
            "Prepare an exhaustive, courtroom-ready 'Hearing Preparation Pack' based strictly on the provided matter file.\n"
            f"Hearing Type Focus: {hearing_type.upper()} (e.g., BAIL, CHARGE_HEARING, DEPOSITION_CROSS, INJUNCTION, FINAL_ARGUMENT).\n\n"
            "Generate JSON with the following structure:\n"
            "{\n"
            '  "hearing_title": "Case Title and Court Forum",\n'
            '  "today_objective": "Single most important tactical objective the advocate must achieve today",\n'
            '  "case_brief": "Executive factual summary for quick bench reference (3-4 sentences)",\n'
            '  "key_chronology_highlights": ["Array of the 3-5 most critical dates to keep at fingertips"],\n'
            '  "governing_statutes": ["Array of controlling Bangladesh Act & Section provisions with short statutory rules"],\n'
            '  "precedents": ["Array of applicable Supreme Court DLR / BLD / BLC citations with ratio"],\n'
            '  "evidence_in_hand": ["Key documents and exhibits ready to present today"],\n'
            '  "evidence_missing_or_risky": ["Missing proofs or vulnerabilities opponent might exploit"],\n'
            '  "anticipated_opposing_arguments": ["Points the opposing counsel will likely raise"],\n'
            '  "effective_counter_arguments": ["Counter-arguments and statutory rebuttals to neutralize opponent"],\n'
            '  "witness_questions": [\n'
            '    {\n'
            '      "target": "Witness name or designation",\n'
            '      "question": "Exact question to put in cross or examination-in-chief",\n'
            '      "intended_admission": "Fact this question establishes",\n'
            '      "caution": "Warning on how to handle hostile answer"\n'
            '    }\n'
            '  ],\n'
            '  "closing_prayer": "Concise, authoritative verbal submission / prayer to state before the Bench"\n'
            "}\n"
            + ("Output all explanatory and tactical text in professional legal Bengali (বাংলা)." if is_bn else "Output in professional legal English.")
        )

        prompt = f"FULL MATTER RECORD DOSSIER:\n\"\"\"\n{dossier}\n\"\"\"\n\nGenerate the courtroom Hearing Preparation Pack for: {hearing_type}."

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        result = await self._call_gemini_json(contents, system_instruction)

        if not result:
            return {
                "status": "error",
                "message": "Failed to generate hearing preparation pack.",
                "data": {}
            }

        return {
            "status": "ok",
            "data": result
        }

    async def check_matter_consistency_and_evidence(
        self,
        matter: Dict[str, Any],
        language: str = "bn"
    ) -> Dict[str, Any]:
        """
        Matter Consistency Checker & Evidence Matrix:
        Cross-checks all consultation transcripts, pleadings, deeds, and notes in the matter file
        to detect factual contradictions (dates, sums, dags, names) and builds an Evidence Matrix.
        """
        is_bn = language.lower().startswith("bn")
        dossier = self._extract_matter_dossier(matter)

        system_instruction = (
            "You are Justor AI's Chief Litigation Auditor and Evidence Analyst for Bangladesh Courts.\n"
            "Thoroughly cross-examine all parts of the matter dossier (client consultations, notes, documents, and chronology).\n\n"
            "Tasks:\n"
            "1. DETECT CONTRADICTIONS: Look for:\n"
            "   - Date clashes (e.g. petition says notice sent 12th, postal receipt says 15th).\n"
            "   - Financial mismatches (cheque sum vs. claimed debt in consultation vs. statutory notice amount).\n"
            "   - Property description inconsistencies (CS/SA/RS/BS Dag numbers, Khatian numbers, Mouza, land quantity).\n"
            "   - Party spelling variations or conflicting factual statements.\n"
            "2. BUILD EVIDENCE MATRIX: For every essential legal ingredient of the claim or defense, evaluate what document proves it and identify what is missing.\n\n"
            "Generate JSON with structure:\n"
            "{\n"
            '  "audit_summary": "High-level integrity verdict of the case record",\n'
            '  "integrity_score": "e.g. 85%",\n'
            '  "contradictions": [\n'
            '    {\n'
            '      "category": "date_inconsistency | amount_mismatch | property_mismatch | party_mismatch | factual_conflict",\n'
            '      "severity": "critical | warning | minor",\n'
            '      "title": "Short title of conflict",\n'
            '      "source_a": "Document or note A stating X",\n'
            '      "source_b": "Document or note B stating Y",\n'
            '      "impact": "How opposing counsel could exploit this defect",\n'
            '      "remedy": "Specific corrective step for advocate to harmonize before trial"\n'
            '    }\n'
            '  ],\n'
            '  "evidence_matrix": [\n'
            '    {\n'
            '      "legal_issue": "Material fact / element to be established",\n'
            '      "supporting_evidence": "Document or witness currently in file",\n'
            '      "status": "proven | partial | missing | vulnerable",\n'
            '      "evidence_gap": "Exact missing proof required under Bangladesh Evidence Act"\n'
            '    }\n'
            '  ]\n'
            "}\n"
            + ("Output all analysis and recommendations in natural legal Bengali (বাংলা)." if is_bn else "Output in clear legal English.")
        )

        prompt = f"MATTER DOSSIER TO AUDIT:\n\"\"\"\n{dossier}\n\"\"\"\n\nAudit all documents for internal contradictions and generate the Evidence Matrix."

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        result = await self._call_gemini_json(contents, system_instruction)

        if not result:
            return {
                "status": "error",
                "message": "Failed to audit matter consistency.",
                "data": {}
            }

        return {
            "status": "ok",
            "data": result
        }

    async def generate_legal_memo(
        self,
        matter: Dict[str, Any],
        question_presented: str,
        language: str = "bn"
    ) -> Dict[str, Any]:
        """
        Source-Linked Legal Memo Generator:
        Generates a formal, rigorous advocate memorandum (IRAC format)
        grounded strictly in the matter facts and Bangladesh statutory/precedential corpus.
        """
        is_bn = language.lower().startswith("bn")
        dossier = self._extract_matter_dossier(matter)

        system_instruction = (
            "You are Justor AI's Senior Legal Research Counsel for Bangladesh Chambers.\n"
            "Draft a comprehensive, formal Legal Memorandum addressing the Question Presented.\n"
            "Adhere strictly to the facts in the Matter Dossier. Do NOT invent external facts.\n"
            "Apply canonical Bangladesh statutory provisions (Bangladesh Code) and Supreme Court precedential case law.\n\n"
            "Generate JSON with structure:\n"
            "{\n"
            '  "memo_title": "LEGAL MEMORANDUM: [Subject Matter]",\n'
            '  "matter_title": "Case / Client title",\n'
            '  "date": "Date of Memorandum",\n'
            '  "question_presented": "Specific legal question analyzed",\n'
            '  "short_answer": "Definitive 1-2 paragraph legal conclusion answering the question directly",\n'
            '  "statement_of_facts": [\n'
            '    "Chronological material fact from matter record",\n'
            '    "Another verified fact from matter record"\n'
            '  ],\n'
            '  "statutory_authorities": [\n'
            '    {\n'
            '      "act": "Name of Statute (e.g. Negotiable Instruments Act, 1881 / The Code of Civil Procedure, 1908)",\n'
            '      "section": "Section or Order & Rule (e.g. Section 138 / Order XXXIX Rule 1)",\n'
            '      "rule": "Statutory rule and legal requirements",\n'
            '      "application": "How it controls our client\'s position",\n'
            '      "exact_passage": "Verbatim or precise statutory text excerpt from the Bangladesh Code"\n'
            '    }\n'
            '  ],\n'
            '  "judicial_precedents": [\n'
            '    {\n'
            '      "citation": "Official Law Report Citation (e.g. 54 DLR (AD) 12 / 18 BLD (HCD) 34)",\n'
            '      "parties": "Parties name",\n'
            '      "ratio": "Principle of law laid down by Supreme Court of Bangladesh",\n'
            '      "application": "Relevance to current matter facts",\n'
            '      "exact_passage": "Direct quote or key holding from the judgment"\n'
            '    }\n'
            '  ],\n'
            '  "irac_analysis": {\n'
            '    "issue": "Legal issue defined concisely",\n'
            '    "rule": "Controlling principles of statutory and case law",\n'
            '    "application": "Thorough application of the legal rules to the matter dossier facts",\n'
            '    "conclusion": "Definitive legal conclusion on this issue"\n'
            '  },\n'
            '  "counterarguments_and_rebuttals": [\n'
            '    "Anticipated argument or procedural objection from opposing counsel and specific legal counter-strategy"\n'
            '  ],\n'
            '  "conclusion_and_recommendations": "Actionable chamber steps, filings, limitation deadlines, and advice for the advocate",\n'
            '  "source_citations": [\n'
            '    {\n'
            '      "title": "Short title (e.g. NI Act 1881, s. 138 or 54 DLR (AD) 12)",\n'
            '      "act": "Statute name or Court",\n'
            '      "section": "Section, Order, or Precedent Citation",\n'
            '      "passage": "Exact verbatim source passage or statutory extract that directly supports the memorandum",\n'
            '      "authority_type": "statute | precedent | gazette"\n'
            '    }\n'
            '  ]\n'
            "}\n"
            + ("Output all explanatory and legal analysis in authoritative legal Bengali (বাংলা)." if is_bn else "Output in authoritative legal English.")
        )

        prompt = (
            f"QUESTION PRESENTED FOR OPINION:\n\"{question_presented}\"\n\n"
            f"MATTER RECORD DOSSIER:\n\"\"\"\n{dossier}\n\"\"\"\n\n"
            "Draft the complete formal Legal Memorandum with exact source citations and passages."
        )

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        result = await self._call_gemini_json(contents, system_instruction)

        if not result:
            return {
                "status": "error",
                "message": "Failed to generate legal memorandum.",
                "data": {}
            }

        # Normalize keys for bidirectional frontend compatibility
        statutes = result.get("statutory_authorities") or result.get("applicable_statutes") or []
        precedents = result.get("judicial_precedents") or result.get("relevant_precedents") or []
        facts = result.get("statement_of_facts") or result.get("facts_considered") or []
        irac = result.get("irac_analysis")
        if not irac and result.get("legal_analysis"):
            irac = {"application": result["legal_analysis"]}
        counterargs = result.get("counterarguments_and_rebuttals") or result.get("counterarguments_and_risks") or []
        recom = result.get("conclusion_and_recommendations") or result.get("final_recommendation") or ""

        # Ensure source_citations is fully populated with exact passages
        source_citations = result.get("source_citations") or []
        if not source_citations:
            for s in statutes:
                if isinstance(s, dict):
                    source_citations.append({
                        "title": f"{s.get('act', 'Act')} {s.get('section', '')}".strip(),
                        "act": s.get("act", ""),
                        "section": s.get("section", ""),
                        "passage": s.get("exact_passage") or s.get("rule") or s.get("rule_of_law") or s.get("application", ""),
                        "authority_type": "statute"
                    })
            for p in precedents:
                if isinstance(p, dict):
                    source_citations.append({
                        "title": p.get("citation") or p.get("case_citation") or p.get("parties", "Precedent"),
                        "act": "Supreme Court of Bangladesh",
                        "section": p.get("citation") or p.get("case_citation", ""),
                        "passage": p.get("exact_passage") or p.get("ratio") or p.get("principle_held") or p.get("application", ""),
                        "authority_type": "precedent"
                    })

        normalized: Dict[str, Any] = {
            "memo_title": result.get("memo_title") or f"LEGAL MEMORANDUM: {question_presented[:40]}",
            "question_presented": result.get("question_presented") or question_presented,
            "short_answer": result.get("short_answer") or "",
            "statement_of_facts": facts if isinstance(facts, list) else [facts],
            "facts_considered": facts if isinstance(facts, list) else [facts],
            "statutory_authorities": statutes,
            "applicable_statutes": [
                {
                    "act": s.get("act", ""),
                    "section": s.get("section", ""),
                    "rule_of_law": s.get("rule") or s.get("rule_of_law") or s.get("application", ""),
                    "exact_passage": s.get("exact_passage", "")
                } for s in statutes if isinstance(s, dict)
            ],
            "judicial_precedents": precedents,
            "relevant_precedents": [
                {
                    "case_citation": p.get("citation") or p.get("case_citation") or (f"{p.get('parties')} ({p.get('citation')})" if p.get("parties") else "Precedent"),
                    "principle_held": p.get("ratio") or p.get("principle_held") or p.get("application", ""),
                    "exact_passage": p.get("exact_passage", "")
                } for p in precedents if isinstance(p, dict)
            ],
            "irac_analysis": irac if isinstance(irac, dict) else {"application": str(irac)},
            "counterarguments_and_rebuttals": counterargs if isinstance(counterargs, list) else [counterargs],
            "counterarguments_and_risks": counterargs if isinstance(counterargs, list) else [counterargs],
            "conclusion_and_recommendations": recom,
            "final_recommendation": recom,
            "source_citations": source_citations
        }

        return {
            "status": "ok",
            "data": normalized
        }


# Singleton instance
matter_service = JustorMatterService()
