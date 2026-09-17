from __future__ import annotations

import os
import io
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


class JustorMatterService:
    """
    Justor Matter Intelligence Service
    Empowers legal practitioners with workflow automation:
    1. Lawyer Dictaphone: Quick voice notes -> structured matter notes.
    2. Consultation Audio Intelligence: Audio recordings -> transcript + legal summary + missing questions.
    3. Legal Document & Judgment Summarization: 60-second case breakdown with Ratio Decidendi.
    4. Matter Chronology & Timeline: Automated date-ordered timeline with statutory limitation alerts.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key

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
        """Returns primary Google AI Studio endpoint and optional Vertex endpoint."""
        urls = []
        if self.api_key:
            # Google AI Studio endpoint (Primary for API keys starting with AIza)
            urls.append(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                f"?key={self.api_key}"
            )
            # Vertex AI Express URL fallback (for GCP environments with enabled express keys)
            urls.append(
                f"https://aiplatform.googleapis.com/v1beta1/projects/{GCP_PROJECT_ID}"
                f"/locations/{VERTEX_LOCATION}/publishers/google/models/{model_name}:generateContent"
                f"?key={self.api_key}"
            )
        return urls

    async def _call_gemini_json(self, contents: list, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Invokes Gemini 2.5 Flash with JSON schema response."""
        urls = self._get_api_urls("gemini-2.5-flash")
        if not urls:
            logger.error("No API key configured for Matter Service.")
            return None

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

        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(url, json=body)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                            if text:
                                return json.loads(text)
                    else:
                        logger.warning(f"Gemini API returned {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"Error calling Gemini endpoint ({url[:40]}...): {e}")
                continue

        return None

    async def parse_voice_dictation(
        self,
        text: str,
        language: str = "bn"
    ) -> Dict[str, Any]:
        """
        Parses raw dictated notes into a structured matter note card.
        Extracts client name, matter type, dispute summary, claim amounts, limitation dates,
        relevant Bangladesh statutes, and missing questions.
        """
        is_bn = language.lower().startswith("bn")
        system_instruction = (
            "You are Justor AI's Senior Chamber Practice Assistant for Bangladesh Advocates.\n"
            "You parse an advocate's raw spoken notes or dictation into a clean, structured matter file.\n"
            "Identify:\n"
            "- Client name and opposing party\n"
            "- Legal dispute type (e.g. NI Act Cheque Dishonour, Specific Relief Title/Eviction, Section 498 CrPC Bail, Family MFLO)\n"
            "- Disputed amount (BDT / Taka) or property description (Mouza, Khatian, Dag)\n"
            "- Crucial dates mentioned\n"
            "- Controlling Bangladesh statutes and sections (e.g. 'The Negotiable Instruments Act, 1881, Section 138')\n"
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
        """
        Multimodal audio ingestion for client consultations.
        Transcribes audio (Bengali/English) and extracts:
        - Transcript
        - Consultation summary
        - Key client facts
        - Documents mentioned (Khatian, Sale deed, Mutation, Bank memo, etc.)
        - Crucial dates
        - Red flags & missing legal questions
        """
        is_bn = language.lower().startswith("bn")
        b64_data = base64.b64encode(audio_bytes).decode("utf-8")

        prompt = (
            "You are Justor AI's Legal Consultation Audio Transcriber and Analyst for Bangladesh.\n"
            "Listen to this client-advocate consultation recording.\n"
            "Tasks:\n"
            "1. Transcribe the conversation accurately in the original spoken languages (Bengali, Banglish, and English).\n"
            "2. Generate an executive consultation summary.\n"
            "3. Extract all concrete facts stated by the client.\n"
            "4. List all documents mentioned (e.g. Sale Deed/বায়া দলিল, Khatian/খতিয়ান, Mutation/নামজারি, Cheque/চেক, Dishonour Memo, Postal A/D Receipt).\n"
            "5. Extract all dates and timelines.\n"
            "6. Identify potential legal risks, limitation traps, or missing evidentiary links.\n"
            "7. Formulate 4-6 specific follow-up questions the lawyer must ask the client.\n\n"
            "Return valid JSON matching this schema:\n"
            "{\n"
            '  "matter_title": "string",\n'
            '  "transcript": "string verbatim transcription",\n'
            '  "consultation_summary": "string",\n'
            '  "client_facts": ["fact 1", "fact 2"],\n'
            '  "documents_mentioned": ["doc 1", "doc 2"],\n'
            '  "crucial_dates": [{"date": "string", "event": "string"}],\n'
            '  "statutory_provisions": ["Act and Section names"],\n'
            '  "red_flags_and_risks": ["risk 1", "risk 2"],\n'
            '  "questions_to_ask_client": ["question 1", "question 2"]\n'
            "}"
        )

        contents = [
            {
                "role": "user",
                "parts": [
                    {"inlineData": {"mimeType": mime_type, "data": b64_data}},
                    {"text": prompt}
                ]
            }
        ]

        result = await self._call_gemini_json(contents)
        if not result:
            return {
                "status": "error",
                "message": "Audio transcription failed. Please check audio clarity and size.",
                "data": {}
            }

        return {
            "status": "ok",
            "data": result
        }

    async def summarize_legal_document(
        self,
        document_content: Union[str, bytes],
        mime_type: str = "text/plain",
        filename: str = "document.txt",
        language: str = "bn"
    ) -> Dict[str, Any]:
        """
        'Case in 60 Seconds' analyzer for judgments, court orders, and legal pleadings.
        Extracts:
        - Court, Bench / Judges, Case Number, Parties
        - Facts in brief
        - Contested Legal Issues
        - Petitioner Arguments vs Respondent Arguments
        - Ratio Decidendi (the core binding rule of law)
        - Final Operative Decision
        - Study Mode FIRAC summary
        """
        is_bn = language.lower().startswith("bn")
        
        parts: list = []
        if isinstance(document_content, bytes) and mime_type.startswith("application/pdf"):
            b64_pdf = base64.b64encode(document_content).decode("utf-8")
            parts.append({"inlineData": {"mimeType": "application/pdf", "data": b64_pdf}})
            prompt_intro = "Analyze this uploaded court judgment / legal document PDF."
        elif isinstance(document_content, bytes):
            text = document_content.decode("utf-8", errors="ignore")
            parts.append({"text": f"Document Text:\n{text[:25000]}"})
            prompt_intro = "Analyze this court judgment / legal document text."
        else:
            parts.append({"text": f"Document Text:\n{document_content[:25000]}"})
            prompt_intro = "Analyze this court judgment / legal document text."

        prompt = (
            f"{prompt_intro}\n"
            "You are Justor AI's Senior Judicial Case Summarizer for Bangladesh Law.\n"
            "Produce an executive 'Case in 60 Seconds' summary:\n"
            "1. Case Header: Court (e.g. Appellate Division / High Court Division), Bench/Judges, Case Number, Date of Decision, Parties.\n"
            "2. Facts in Brief: Concise 3-4 sentence background.\n"
            "3. Contested Issues: Core legal questions framed by the court.\n"
            "4. Arguments: Petitioner/Appellant's stance vs Respondent/State's stance.\n"
            "5. Statutory Provisions & Precedents Cited: Bangladesh statutes, articles of the Constitution, and landmark precedents.\n"
            "6. Ratio Decidendi: The exact binding legal principle or doctrine articulated by the court.\n"
            "7. Operative Order / Decision: The final ruling (Rule made absolute, Appeal allowed/dismissed, Bail granted/rejected, Sentence modified).\n"
            "8. Study Mode: A simplified FIRAC (Facts, Issue, Rule, Analysis, Conclusion) explanation for students.\n\n"
            "Return valid JSON with keys: case_title, court, bench, case_number, decision_date, parties (petitioner, respondent), "
            "facts_brief, legal_issues (list), petitioner_arguments (list), respondent_arguments (list), "
            "statutes_cited (list), precedents_cited (list), ratio_decidendi, operative_order, study_mode_firac (facts, issue, rule, analysis, conclusion)."
        )
        parts.append({"text": prompt})

        contents = [{"role": "user", "parts": parts}]
        result = await self._call_gemini_json(contents)

        if not result:
            return {
                "status": "error",
                "message": "Failed to generate document summary.",
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
        """
        Parses case pleadings, notices, and facts into an ordered chronological timeline.
        Detects statutory limitation alerts under Bangladesh Limitation Act, NI Act, CPC, and CrPC.
        """
        is_bn = language.lower().startswith("bn")
        prompt = (
            "You are Justor AI's Legal Chronology & Limitation Specialist for Bangladesh Law.\n"
            "Extract all chronological events, dates, agreements, notices, and occurrences from this matter text:\n"
            f"\"\"\"\n{events_text}\n\"\"\"\n\n"
            "Tasks:\n"
            "1. Identify every date or time milestone mentioned (even relative ones like 'two weeks later').\n"
            "2. Order all events chronologically from earliest to most recent.\n"
            "3. Tag each event's importance: 'critical' (e.g. cheque dishonour, notice served, suit filing, dispossession) or 'standard'.\n"
            "4. Identify any STATUTORY LIMITATION RISKS under Bangladesh law (e.g., 30 days to serve NI Act notice, 30 days to file NI Act complaint after notice expiry, 6 months for s.9 Specific Relief Act, 3 years for contract breach).\n\n"
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
            '      "provision": "Act and Section name",\n'
            '      "rule": "Statutory time limit rule",\n'
            '      "status": "expired | urgent | active | compliant",\n'
            '      "warning": "Detailed risk advice"\n'
            '    }\n'
            '  ],\n'
            '  "summary": "2-3 sentence overview of timeline"\n'
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


# Singleton instance
matter_service = JustorMatterService()
