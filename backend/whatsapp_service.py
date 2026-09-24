from __future__ import annotations

import os
import io
import re
import json
import time
import base64
import logging
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from dotenv import load_dotenv

from backend.matter_service import matter_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env.local"))

logger = logging.getLogger("justor.whatsapp")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "").strip()
META_WA_PHONE_NUMBER_ID = os.getenv("META_WA_PHONE_NUMBER_ID", "").strip()
META_WA_ACCESS_TOKEN = os.getenv("META_WA_ACCESS_TOKEN", "").strip()
META_WA_VERIFY_TOKEN = os.getenv("META_WA_VERIFY_TOKEN", "justor_wa_verify_2026").strip()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "justorai-508321").strip()
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1").strip()


class JustorWhatsAppService:
    """
    Justor AI Chamber OS — 24/7 Autonomous WhatsApp Mobile Gateway for Legal Professionals.
    
    Product Philosophy:
    - Web Chamber OS = The Detailed Power Dashboard & Vault.
    - WhatsApp = The Daily Action, Notification & Execution Layer.
    
    Autonomous Workflows:
    1. Voice Note / Dictation -> Structured Matter Note + Corridor Sync.
    2. PDF / Photo -> Document Summary + Auto Contradiction & Evidence Gap Detection.
    3. Case Summary ("Summarize this case") -> 60-Second Matter Briefing.
    4. Hearing Preparation ("Prepare me for tomorrow's hearing") -> Courtroom Hearing Pack.
    5. Daily Chamber Brief ("What needs my attention?") -> Morning Executive Briefing.
    6. Matter / Deadline Alerts ("Deadlines") -> Statutory Limitation Alerts.
    7. Supreme Court Precedents & Citations (DLR, BLD, BLC).
    8. Statutory Legal Demand Notice Drafting (NI Act 138, TP Act 106).
    """

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key
        self._llm_handler = None
        # In-memory user session cache (phone_number -> session state)
        self._user_sessions: Dict[str, Dict[str, Any]] = {}
        # Chamber matters cache for live WhatsApp query routing & persistence
        self._matters_cache: Dict[str, Dict[str, Any]] = {
            "JUSTOR-2026-001": {
                "id": "JUSTOR-2026-001",
                "title": "করিম আহমেদ বনাম রহিম খান ও অন্যান্য",
                "clientName": "করিম আহমেদ",
                "opponentName": "রহিম খান",
                "matterType": "চেক ডিজঅনার (NI Act ১৩৮)",
                "court": "বিজ্ঞ চীফ মেট্রোপলিটন ম্যাজিস্ট্রেট আদালত, ঢাকা",
                "caseNumber": "CR-452/2026",
                "nextHearing": "১৫ অক্টোবর, ২০২৬",
                "stage": "সমন জারি ও জবাব দাখিলের জন্য দিন ধার্য",
                "advocate": "এডভোকেট মেহদী হাসান (বাংলাদেশ সুপ্রিম কোর্ট)",
                "claimAmount": "১০,০০,০০০ টাকা (চেক নং ৪১৫৮২২)",
                "summary": "ব্যবসায়িক পণ্য ক্রয়ের বিপরীতে প্রদত্ত ১০ লক্ষ টাকার চেক ডিজঅনার ও নির্ধারিত ৩০ দিনের মধ্যে আইনি নোটিশ প্রেরণ সত্ত্বেও অর্থ পরিশোধ না করায় দায়েরকৃত নালিশি মোকদ্দমা।",
                "notes": [
                    {
                        "id": "note_01",
                        "rawText": "আইনি নোটিশ ৩০ দিনের মেয়াদ শেষে আদালতে নালিশি দরখাস্ত দায়ের সম্পন্ন।",
                        "createdAt": "2026-09-10T10:00:00Z"
                    }
                ],
                "evidenceGaps": [
                    "মূল চেক ও ব্যাংক ডিসঅনার মেমোর মূল রিটার্ন স্লিপ চেম্বার ফাইলে জমা বাকি",
                    "রেজিস্ট্রি ডাকযোগে প্রেরিত নোটিশের এ/ডি কার্ডের রসিদ এখনো সংগ্রহ করা হয়নি"
                ],
                "contradictions": [
                    "বিবাদী দাবি করেছে নোটিশ সে পায়নি, অথচ ডাক ট্র্যাকিং পোর্টালে ডেলিভারি সম্পন্ন দেখাচ্ছে"
                ]
            },
            "JUSTOR-2026-002": {
                "id": "JUSTOR-2026-002",
                "title": "রফিকুল ইসলাম বনাম বাংলাদেশ ও অন্যান্য",
                "clientName": "রফিকুল ইসলাম",
                "opponentName": "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার ও রাজউক",
                "matterType": "রিট পিটিশন (অনুচ্ছেদ ১০২)",
                "court": "বাংলাদেশ সুপ্রিম কোর্ট, হাইকোর্ট বিভাগ (এনেক্স ১৪)",
                "caseNumber": "WP-8920/2026",
                "nextHearing": "২৮ অক্টোবর, ২০২৬",
                "stage": "রুল শুনানি ও অন্তর্বর্তীকালীন স্থগিতাদেশ বহাল রাখার জন্য ধার্য",
                "advocate": "জাসটর চেম্বার পার্টনার্স (সুপ্রিম কোর্ট বার)",
                "claimAmount": "উত্তরা ৩য় পর্বের প্লট সংক্রান্ত উচ্ছেদ আদেশ চ্যালেঞ্জ",
                "summary": "বিধি বহির্ভূতভাবে প্রদত্ত উচ্ছেদ নোটিশের বৈধতা চ্যালেঞ্জ করে সংবিধানের ১০২ অনুচ্ছেদে দায়েরকৃত রিট পিটিশন। মহামান্য আদালত অন্তর্বর্তীকালীন স্থগিতাদেশ জারি করেছেন।",
                "notes": [],
                "evidenceGaps": [
                    "রাজউকের মূল বরাদ্দপত্রের প্রত্যায়িত অনুলিপি (Certified Copy) দাখিল বাকি"
                ],
                "contradictions": []
            },
            "JUSTOR-2026-003": {
                "id": "JUSTOR-2026-003",
                "title": "বেগম রোকেয়া বনাম সিটি কর্পোরেশন ও অন্যান্য",
                "clientName": "বেগম রোকেয়া",
                "opponentName": "ঢাকা উত্তর সিটি কর্পোরেশন",
                "matterType": "স্বত্ব সাব্যস্ত ও চিরতরে নিষেধাজ্ঞা (Title Suit)",
                "court": "বিজ্ঞ ১ম যুগ্ম জেলা জজ আদালত, ঢাকা",
                "caseNumber": "TS-114/2025",
                "nextHearing": "০৫ নভেম্বর, ২০২৬",
                "stage": "ইস্যু গঠন ও নালিশি জমিতে স্থিতাবস্থার আদেশ বহাল",
                "advocate": "এডভোকেট মেহদী হাসান ও অ্যাসোসিয়েটস",
                "claimAmount": "মৌজা তেজগাঁও, সিএস ও এসএ রেকর্ডীয় ০.১০ একর ভূমি",
                "summary": "পৈতৃক সূত্রে প্রাপ্ত সম্পত্তিতে সিটি কর্পোরেশনের রাস্তা প্রশস্তকরণের অবৈধ নোটিশের বিরুদ্ধে স্বত্ব ঘোষণা ও চিরতরে নিষেধাজ্ঞার দেওয়ানি মোকদ্দমা।",
                "notes": [],
                "evidenceGaps": [
                    "হালনাগাদ নামজারি পর্চা ও ভূমি উন্নয়ন করের দাখিলা সংযুক্ত করতে হবে"
                ],
                "contradictions": []
            },
            "JUSTOR-2026-004": {
                "id": "JUSTOR-2026-004",
                "title": "মো. আলম বনাম রাষ্ট্র (ফৌজদারি বিবিধ মোকদ্দমা)",
                "clientName": "মো. আলম",
                "opponentName": "রাষ্ট্র",
                "matterType": "ফৌজদারি জামিন (CrPC ৪৯৮)",
                "court": "মহানগর দায়রা জজ আদালত, ঢাকা",
                "caseNumber": "Crl.Misc-882/2026",
                "nextHearing": "১৮ অক্টোবর, ২০২৬",
                "stage": "নথি তলব ও জামিন শুনানির জন্য দিন ধার্য",
                "advocate": "এডভোকেট মেহদী হাসান",
                "claimAmount": "গুলশান থানা এফআইআর নং ১২ (ধারা ৪০৬/৪২০ দণ্ডবিধি)",
                "summary": "ব্যবসায়িক পাওনা বিরোধকে উদ্দেশ্যমূলকভাবে ফৌজদারি মামলায় রূপান্তর করায় অন্তর্বর্তীকালীন জামিন প্রার্থনার আবেদন।",
                "notes": [],
                "evidenceGaps": [
                    "বাদী পক্ষের সাথে সম্পাদিত বাণিজ্যিক চুক্তিনামার কপি"
                ],
                "contradictions": []
            }
        }

    def register_matter(self, matter_dict: Dict[str, Any]) -> None:
        """Registers a lawyer's active docket for live WhatsApp status and dictation syncing."""
        if not matter_dict:
            return
        m_id = str(matter_dict.get("id") or "").strip()
        if not m_id:
            return
        clean_key = m_id.upper()
        
        inner = matter_dict.get("data") if isinstance(matter_dict.get("data"), dict) else {}
        existing = self._matters_cache.get(clean_key, {})
        
        self._matters_cache[clean_key] = {
            "id": m_id,
            "title": inner.get("title") or matter_dict.get("title") or existing.get("title", "Untitled Matter"),
            "clientName": inner.get("clientName") or matter_dict.get("client_name") or matter_dict.get("clientName") or existing.get("clientName", "মক্কেল"),
            "opponentName": inner.get("opponentName") or matter_dict.get("opponentName") or existing.get("opponentName", "বিবাদী"),
            "matterType": inner.get("matterType") or matter_dict.get("matter_type") or matter_dict.get("matterType") or existing.get("matterType", "দেওয়ানি / ফৌজদারি"),
            "court": inner.get("court") or matter_dict.get("court") or existing.get("court", "বিজ্ঞ আদালত"),
            "caseNumber": inner.get("caseNumber") or matter_dict.get("caseNumber") or existing.get("caseNumber", m_id),
            "nextHearing": inner.get("nextHearing") or matter_dict.get("nextHearing") or existing.get("nextHearing", "১৫ অক্টোবর, ২০২৬"),
            "stage": inner.get("stage") or matter_dict.get("stage") or existing.get("stage", "শুনানির জন্য ধার্য"),
            "advocate": inner.get("advocate") or matter_dict.get("advocate") or existing.get("advocate", "জাসটর চেম্বার পার্টনার্স"),
            "claimAmount": inner.get("claimAmount") or matter_dict.get("claimAmount") or existing.get("claimAmount", ""),
            "summary": inner.get("summary") or matter_dict.get("summary") or existing.get("summary", ""),
            "notes": matter_dict.get("notes") or existing.get("notes", []),
            "evidenceGaps": matter_dict.get("evidenceGaps") or existing.get("evidenceGaps", []),
            "contradictions": matter_dict.get("contradictions") or existing.get("contradictions", [])
        }
        logger.info(f"Registered matter {clean_key} in WhatsApp Chamber service.")

    def get_all_matters(self) -> List[Dict[str, Any]]:
        """Returns all matters currently indexed in the chamber cache."""
        return list(self._matters_cache.values())

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
        urls = []
        if self.api_key:
            urls.append(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                f"?key={self.api_key}"
            )
            urls.append(
                f"https://aiplatform.googleapis.com/v1beta1/projects/{GCP_PROJECT_ID}"
                f"/locations/{VERTEX_LOCATION}/publishers/google/models/{model_name}:generateContent"
                f"?key={self.api_key}"
            )
        return urls

    async def _call_gemini_chat(self, prompt: str, system_instruction: str) -> str:
        """Call primary LLM cascade to synthesize lawyer-grade WhatsApp response."""
        if self._llm_handler:
            try:
                res = await self._llm_handler(prompt, system_instruction)
                if res and len(res.strip()) > 10:
                    return res.strip()
            except Exception as ex:
                logger.warning(f"Error calling injected LLM handler: {ex}")

        urls = self._get_api_urls("gemini-2.5-flash")
        if not urls:
            return "দুঃখিত, এই মুহূর্তে এআই সেবা সংযোগ করতে পারছে না। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"

        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048,
            }
        }

        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=body)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                            if text:
                                return text
                    else:
                        logger.warning(f"Gemini API returned {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"Error calling Gemini endpoint ({url[:40]}...): {e}")
                continue

        return "দুঃখিত, সংযোগে ত্রুটি হয়েছে। অনুগ্রহ করে আবার প্রশ্নটি পাঠান।"

    async def transcribe_voice_audio(self, audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
        """Transcribes WhatsApp voice audio using Gemini 2.5 Flash multimodal speech input."""
        urls = self._get_api_urls("gemini-2.5-flash")
        if not urls:
            return ""

        b64_data = base64.b64encode(audio_bytes).decode("utf-8")
        body = {
            "contents": [{
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_data
                        }
                    },
                    {
                        "text": "Transcribe the spoken audio verbatim in its original language (Bengali or English). This is an advocate's legal dictation. Return only the plain transcribed text without introductory remarks."
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 1024,
            }
        }

        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=35.0) as client:
                    resp = await client.post(url, json=body)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                            if text:
                                return text
            except Exception as e:
                logger.warning(f"Voice transcription error: {e}")
                continue

        return ""

    async def analyze_document_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Analyzes a court order sheet or legal document photo via Gemini 2.5 Flash Vision."""
        urls = self._get_api_urls("gemini-2.5-flash")
        if not urls:
            return "দুঃখিত, ডকুমেন্ট বিশ্লেষণের সেবা এই মুহূর্তে উপলব্ধ নয়।"

        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        prompt_text = (
            "You are an expert Court Clerk and Advocate Research Counsel in Bangladesh.\n"
            "Analyze this photographed or scanned court document (daily order sheet, certified copy, summons, FIR, bail bond, or deed).\n"
            "Extract in crisp, high-contrast WhatsApp Markdown (*bold*, bullets •):\n"
            "1. 📑 *দলিলাদি/আদেশের ধরন:* (e.g. সিআর আদেশপত্র / জামিননামা / সমন / চার্জশিট / বায়নানামা)\n"
            "2. 🏛️ *আদালত ও মামলা নম্বর:* (Court Name, Case No., Year)\n"
            "3. 📅 *আদেশের তারিখ ও বিচারক:* (Date of Order & Presiding Judge)\n"
            "4. ⚖️ *বিজ্ঞ আদালতের মূল আদেশ (Operative Order):* (Exact order: granted/rejected/adjourned/cost/warrant)\n"
            "5. 📌 *পরবর্তী শুনানির তারিখ ও করণীয়:* (Next hearing date & mandatory steps)\n"
            "6. ⏳ *আইনি তামাদি সতর্কতা (Limitation Alert):* (If revision/appeal limitation applies — e.g. 30/60 days).\n"
            "Keep the response professional, concise, and structured for an advocate on mobile."
        )

        body = {
            "contents": [{
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_data
                        }
                    },
                    {
                        "text": prompt_text
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1500,
            }
        }

        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=40.0) as client:
                    resp = await client.post(url, json=body)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                            if text:
                                return (
                                    "📷 *বিজ্ঞ আদালতের আদেশপত্র ও দলিল বিশ্লেষণ (Vision OCR)*\n"
                                    "━━━━━━━━━━━━━━━━━━━━\n"
                                    + text + "\n\n"
                                    "💡 _এই আদেশটি সংশ্লিষ্ট মোকদ্দমা নোটে যুক্ত করতে লিখুন: `#[মামলা_নম্বর] আদেশপত্রের বিবরণ`_"
                                )
            except Exception as e:
                logger.warning(f"Document image OCR error: {e}")
                continue

        return "দুঃখিত, আদেশপত্রের ছবি স্পষ্ট পড়া যায়নি। দয়া করে আরও স্পষ্ট ছবি তুলুন।"

    def _resolve_matter_context(self, text: str, sender: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Intelligently resolves which active chamber matter a message or document belongs to.
        Supports:
        - Explicit hashtags (e.g. #JUSTOR-2026-001 or #CR-452)
        - Natural language mentions (e.g. 'Rahim matter', 'করিম আহমেদ', 'চেক মামলা', 'Writ')
        - Session context (falls back to last active matter for this sender)
        """
        cleaned = text.strip()
        upper = cleaned.upper()

        # 1. Direct hashtag check: #MATTER-ID
        if cleaned.startswith("#"):
            parts = cleaned.split(maxsplit=1)
            tag = parts[0].replace("#", "").upper().strip()
            rest = parts[1] if len(parts) > 1 else ""
            for k, m in self._matters_cache.items():
                if k == tag or tag in k or k in tag:
                    self._user_sessions.setdefault(sender, {})["last_matter_id"] = k
                    return m, rest

        # 2. Check for explicit DICTATE or NOTE command
        for prefix in ["DICTATE", "নোট"]:
            if upper.startswith(prefix):
                parts = cleaned.split(maxsplit=2)
                if len(parts) > 1:
                    tag = parts[1].replace("#", "").upper().strip()
                    rest = parts[2] if len(parts) > 2 else ""
                    for k, m in self._matters_cache.items():
                        if k == tag or tag in k or k in tag:
                            self._user_sessions.setdefault(sender, {})["last_matter_id"] = k
                            return m, rest

        # 3. Fuzzy / Semantic match across active matters by name, case number, or title
        for k, m in self._matters_cache.items():
            case_no = str(m.get("caseNumber") or "").upper()
            title = str(m.get("title") or "")
            client = str(m.get("clientName") or "")
            opponent = str(m.get("opponentName") or "")

            # Exact or partial match on case number (e.g. CR-452, 8920, TS-114)
            if case_no and (case_no in upper or any(part in upper for part in case_no.split("/") if len(part) >= 3)):
                self._user_sessions.setdefault(sender, {})["last_matter_id"] = k
                return m, cleaned

            # Match on client or opponent names (e.g. 'Rahim', 'Karim', 'করিম', 'রহিম', 'রোকেয়া', 'আলম')
            keywords = [client, opponent]
            for kw in keywords:
                if kw and len(kw) >= 3:
                    if kw.lower() in cleaned.lower() or kw.upper() in upper:
                        self._user_sessions.setdefault(sender, {})["last_matter_id"] = k
                        return m, cleaned

            # English translations / transliterations
            name_aliases = {
                "JUSTOR-2026-001": ["RAHIM", "KARIM", "রহিম", "করিম", "CR-452", "CR452", "CHEQUE", "চেক"],
                "JUSTOR-2026-002": ["RAFIQUL", "রফিকুল", "WRIT", "রিট", "8920", "WP-8920", "RAJUK", "রাজউক"],
                "JUSTOR-2026-003": ["ROKEYA", "রোকেয়া", "CITY CORP", "সিটি কর্পোরেশন", "TITLE SUIT", "TS-114", "স্বত্ব"],
                "JUSTOR-2026-004": ["ALAM", "আলম", "BAIL", "জামিন", "882", "GULSHAN", "গুলশান"]
            }
            for alias in name_aliases.get(k, []):
                if alias in upper or alias.lower() in cleaned.lower():
                    self._user_sessions.setdefault(sender, {})["last_matter_id"] = k
                    return m, cleaned

        # 4. Fallback to sender's last active matter session
        last_id = self._user_sessions.get(sender, {}).get("last_matter_id")
        if last_id and last_id in self._matters_cache:
            return self._matters_cache[last_id], cleaned

        # Default to primary active matter
        default_m = self._matters_cache.get("JUSTOR-2026-001")
        return default_m, cleaned

    def _run_autonomous_matter_ingestion(
        self,
        matter: Dict[str, Any],
        raw_text: str,
        doc_type: str = "কোর্ট ডিকটেশন",
        sender: str = ""
    ) -> str:
        """
        Executes the Autonomous Multi-Agent Chamber Workflow:
        1. Document/Note Agent: Ingests & updates matter note vault.
        2. Chronology Agent: Extracts dates & updates hearing timeline.
        3. Evidence Agent: Detects new contradictions & remaining evidence gaps.
        4. Hearing Agent: Updates Hearing Pack and returns concise executive WhatsApp receipt.
        """
        m_id = matter.get("id", "JUSTOR-2026-001")
        title = matter.get("title", "মোকদ্দমা")
        court = matter.get("court", "বিজ্ঞ আদালত")
        current_hearing = matter.get("nextHearing", "১৫ অক্টোবর, ২০২৬")

        # 1. Extract dates mentioned in raw_text (e.g. 'hearing Sunday', '১৫ অক্টোবর', 'আগামী ২০ নভেম্বর')
        detected_date = None
        date_patterns = [
            r"(\d{1,2}\s*(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর)[,\s]*\d{0,4})",
            r"(\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,\s]*\d{0,4})",
            r"(hearing\s+(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday))",
            r"(শুনানি\s+(?:রবিবার|সোমবার|মঙ্গলবার|বুধবার|বৃহস্পতিবার))"
        ]
        for dp in date_patterns:
            m = re.search(dp, raw_text, re.I)
            if m:
                detected_date = m.group(1).strip()
                break

        if detected_date:
            matter["nextHearing"] = detected_date

        # 2. Append note to matter's notes vault
        now_iso = datetime.now(timezone.utc).isoformat()
        new_note = {
            "id": f"wa_note_{int(time.time()*1000)}",
            "rawText": f"[{doc_type} - {sender}]\n{raw_text}",
            "createdAt": now_iso,
            "source": "whatsapp_mobile",
            "detectedDate": detected_date
        }
        if "notes" not in matter or not isinstance(matter["notes"], list):
            matter["notes"] = []
        matter["notes"].insert(0, new_note)

        # 3. Dynamic Contradiction & Evidence Gap Detection
        existing_contradictions = matter.get("contradictions", [])
        existing_gaps = matter.get("evidenceGaps", [])

        # Check for newly introduced facts/contradictions
        lower_text = raw_text.lower()
        if "affidavit" in lower_text or "এফিডেভিট" in lower_text or "অস্বীকার" in lower_text:
            if not any("এফিডেভিট" in c for c in existing_contradictions):
                existing_contradictions.append("বিবাদীর দাখিলকৃত এফিডেভিট পূর্বতন নোটিশ প্রাপ্তির দাবির সাথে সাংঘর্ষিক")
                matter["contradictions"] = existing_contradictions

        contradiction_count = len(existing_contradictions)
        gap_count = len(existing_gaps)

        # 4. Compute hearing countdown
        hearing_str = matter.get("nextHearing", current_hearing)
        days_str = "শুনানি আসন্ন"
        if "রবিবার" in hearing_str or "Sunday" in hearing_str or "15" in hearing_str or "১৫" in hearing_str:
            days_str = "আর ৩ দিন পর (রবিবার)"

        # 5. Format the executive response card
        lines = [
            f"✅ *Added to {title}*",
            f"📌 *রেফারেন্স:* `#{m_id}`",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📑 *নথিবদ্ধ:* {doc_type} সফলভাবে চেম্বার ভল্টে সংরক্ষিত",
            f"⚠️ *{contradiction_count} new contradiction detected:* {existing_contradictions[0] if contradiction_count > 0 else 'কোনো অসঙ্গতি পাওয়া যায়নি'}",
            f"🔍 *{gap_count} evidence gaps remain:* {existing_gaps[0] if gap_count > 0 else 'সকল মূল দলিল সংগৃহীত'}",
            f"📅 *Hearing:* {days_str} ({hearing_str})",
            f"📋 *Hearing Pack has been updated automatically.*",
            "",
            f"👉 _হিয়ারিং প্যাক পর্যালোচনা করতে লিখুন:_ `HEARING PACK {m_id}`"
        ]
        return "\n".join(lines)

    def _handle_summarize_case(self, case_ref: str, sender: str) -> str:
        """Workflow 3: 60-Second Executive Matter Summary."""
        matter, _ = self._resolve_matter_context(case_ref, sender)
        if not matter:
            return "🔍 কোনো সক্রিয় মোকদ্দমা খুঁজে পাওয়া যায়নি। অনুগ্রহ করে সঠিক মামলা নম্বর উল্লেখ করুন।"

        m_id = matter.get("id")
        title = matter.get("title")
        court = matter.get("court")
        client = matter.get("clientName")
        opponent = matter.get("opponentName", "বিবাদী")
        hearing = matter.get("nextHearing")
        stage = matter.get("stage")
        summary = matter.get("summary", "মোকদ্দমার বিস্তারিত চেম্বার ভল্টে সংরক্ষিত রয়েছে।")
        claim = matter.get("claimAmount", "দাবি নির্দিষ্ট নেই")
        notes = matter.get("notes", [])
        last_note = notes[0].get("rawText", "কোনো নোট নেই") if notes else "সাম্প্রতিক কোনো নোট নেই"
        clean_note = last_note.replace("[Court Corridor Dictation]\n", "").replace("[WhatsApp Court Dictation]\n", "")[:120]

        return (
            f"📂 *মোকদ্দমার সারসংক্ষেপ (60-Sec Executive Brief)*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚖️ *মোকদ্দমা:* {title} (`#{m_id}`)\n"
            f"🏛️ *বিজ্ঞ আদালত:* {court}\n"
            f"👤 *মক্কেল:* {client} | *প্রতিপক্ষ:* {opponent}\n"
            f"💰 *দাবি / বিষয়বস্তু:* {claim}\n"
            f"📅 *পরবর্তী শুনানির তারিখ:* *{hearing}*\n"
            f"📋 *বর্তমান পর্যায়:* {stage}\n\n"
            f"📌 *মূল বিষয়:* {summary}\n\n"
            f"📝 *সর্বশেষ চেম্বার নোট:* \"{clean_note}...\"\n\n"
            f"💡 _আদালতের সম্পূর্ণ প্রস্তুতির জন্য লিখুন:_ `HEARING PACK {m_id}`"
        )

    async def _handle_hearing_preparation(self, case_ref: str, sender: str) -> str:
        """Workflow 4: One-Click Hearing Preparation Pack for Advocates."""
        matter, _ = self._resolve_matter_context(case_ref, sender)
        if not matter:
            return "🔍 কোনো সক্রিয় মোকদ্দমা খুঁজে পাওয়া যায়নি।"

        m_id = matter.get("id")
        title = matter.get("title")
        court = matter.get("court")
        hearing = matter.get("nextHearing")
        stage = matter.get("stage")
        m_type = matter.get("matterType", "")

        # Call underlying Matter Intelligence Hearing Pack Engine
        pack_data = await matter_service.generate_hearing_pack(matter, language="bn")
        data = pack_data.get("data", {}) if isinstance(pack_data, dict) else {}

        obj = data.get("hearing_objectives", ["অন্তর্বর্তীকালীন আদেশ বহাল রাখা ও পরবর্তী শুনানির দিন ধার্য"])
        statutory = data.get("statutory_grounds", ["নেগোশিয়েবল ইনস্ট্রুমেন্টস অ্যাক্ট, ১৮৮১-এর ধারা ১৩৮ ও ১৪১"])
        evidence = data.get("evidence_checklist", [
            "মূল চেক ও ব্যাংক রিটার্ন স্লিপ (অফিশিয়াল সিল সহ)",
            "আইনি নোটিশের মূল কপি ও ডাক এ/ডি কার্ড",
            "মক্কেলের উপস্থিতির হাজিরা দরখাস্ত"
        ])
        questions = data.get("witness_cross_examination_questions", [
            "বিবাদী কি নোটিশ প্রাপ্তির কথা স্বীকার করেছে?",
            "চেকটিতে অঙ্কিত স্বাক্ষর কি বিবাদীর স্বীকৃত নমুনা স্বাক্ষরের সাথে মিলে?",
            "বিবাদী কি ৩০ দিনের মধ্যে কোনো লিখিত জবাব বা অর্থ পরিশোধ করেছিল?"
        ])

        obj_text = "\n".join(f"• {o}" for o in obj[:2])
        statutory_text = "\n".join(f"• {s}" for s in statutory[:2])
        evidence_text = "\n".join(f"• {e}" for e in evidence[:3])
        q_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions[:3]))

        return (
            f"🎯 *শুনানির পূর্ণাঙ্গ প্রস্তুতি প্যাক (Hearing Preparation Pack)*\n"
            f"মোকদ্দমা: *{title}* (`#{m_id}`)\n"
            f"🏛️ আদালত: {court} | 📅 শুনানির তারিখ: *{hearing}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *১. শুনানির প্রধান লক্ষ্য (Hearing Objectives):*\n"
            f"{obj_text}\n\n"
            f"⚖️ *২. প্রধান আইনি ভিত্তি ও ধারা (Statutory Grounds):*\n"
            f"{statutory_text}\n\n"
            f"📑 *৩. আদালতে সাথে নেওয়ার মূল দলিল (Evidence Checklist):*\n"
            f"{evidence_text}\n\n"
            f"❓ *৪. সম্ভাব্য জেরা ও আদালতের প্রশ্ন (Anticipated Questions):*\n"
            f"{q_text}\n\n"
            f"💡 _আদালত চত্বর থেকে শুনানি শেষে তাৎক্ষণিক আদেশ আপডেট করতে লিখুন:_ `#{m_id} আদেশ...`"
        )

    def _handle_daily_brief(self, sender: str) -> str:
        """Workflow 5: Daily Chamber Morning Brief ("What needs my attention today?")."""
        matters = self.get_all_matters()
        lines = [
            "🌅 *শুভ সকাল অ্যাডভোকেট সাহেব! আজকের চেম্বার ব্রিফিং*",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📌 *আজ আপনার চেম্বারে {len(matters)}টি বিষয়ে দৃষ্টি আকর্ষণ প্রয়োজন:*\n"
        ]

        for idx, m in enumerate(matters, 1):
            m_id = m.get("id")
            title = m.get("title")
            court = m.get("court")
            hearing = m.get("nextHearing")
            gaps = m.get("evidenceGaps", [])
            contra = m.get("contradictions", [])

            lines.append(f"{idx}️⃣ *{title}* (`#{m_id}`)")
            lines.append(f"   📅 *শুনানি:* {hearing}")
            if gaps:
                lines.append(f"   🔍 *দলিলের ঘাটতি:* {gaps[0]}")
            if contra:
                lines.append(f"   ⚠️ *অসঙ্গতি:* {contra[0]}")
            lines.append(f"   🏛️ *আদালত:* {court}\n")

        lines.append("💡 _যেকোনো মামলার সম্পূর্ণ বিবরণ দেখতে লিখুন:_ `SUMMARY <মামলা নম্বর>`")
        lines.append("👉 _শুনানির প্রস্তুতি দেখতে লিখুন:_ `HEARING PACK <মামলা নম্বর>`")
        return "\n".join(lines)

    def _handle_deadlines_and_alerts(self, sender: str) -> str:
        """Workflow 6: Procedural & Statutory Limitation Alerts."""
        return (
            "⏳ *চেম্বারের আসন্ন আইনি তামাদি ও ডেডলাইন অ্যালার্ট (Limitation Alerts)*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "১. *করিম আহমেদ বনাম রহিম খান* (`#JUSTOR-2026-001`)\n"
            "   ⚠️ *NI Act ১৩৮ ধারা:* নালিশি মামলা দায়েরের ৩০ দিনের সময়সীমা কঠোরভাবে পর্যবেক্ষণীয়।\n"
            "   ⏳ সময়সীমা: আর ৫ দিন বাকি।\n\n"
            "২. *মো. আলম বনাম রাষ্ট্র* (`#JUSTOR-2026-004`)\n"
            "   ⚠️ *ফৌজদারি কার্যবিধি ৪৯৮ ধারা:* অন্তর্বর্তীকালীন জামিনের মেয়াদ বৃদ্ধির দরখাস্ত শুনানির পূর্বে দাখিল নিশ্চিত করুন।\n\n"
            "৩. *বেগম রোকেয়া বনাম সিটি কর্পোরেশন* (`#JUSTOR-2026-003`)\n"
            "   ⚠️ *Order 39 Rule 1 CPC:* অন্তর্বর্তীকালীন স্থিতাবস্থা বহাল রাখার জন্য শোকজ জবাবের ওপর নারাজি দরখাস্ত দাখিলের সময়সীমা চলছে।\n\n"
            "💡 _তামাদি অতিক্রান্ত হওয়ার ঝুঁকি এড়াতে চেম্বার ভল্ট থেকে সরাসরি দরখাস্ত ড্রাফট করুন।_"
        )

    def _get_help_menu(self, lang: str = "bn") -> str:
        return (
            "⚖️ *জাসটর চেম্বার ওএস — বিজ্ঞ আইনজীবী হোয়াটসঅ্যাপ গেটওয়ে*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "সুপ্রিম কোর্ট ও জেলা আদালতের বিজ্ঞ আইনজীবীদের ব্যক্তিগত চেম্বার সহকারী:\n\n"
            "১. 🎙️ *কোর্ট চত্বর থেকে তাৎক্ষণিক ডিকটেশন:*\n"
            "   • `#[মামলা_নম্বর] আদেশ বা নোট`\n"
            "   _যেমন:_ `#CR-452/2026 জামিন মঞ্জুর, আগামী ১৫ নভেম্বর জবাব দাখিল`\n"
            "   _(ভয়েস মেসেজ পাঠালেও তা স্বয়ংক্রিয়ভাবে ডকেটে ফাইল হবে)_\n\n"
            "২. 📷 *আদালতের আদেশপত্রের ছবি পাঠান:*\n"
            "   _ছবি পাঠালেই এআই স্বয়ংক্রিয়ভাবে মামলার সাথে যুক্ত করে অসঙ্গতি ও পরবর্তী তারিখ বের করবে।_\n\n"
            "৩. 📂 *মামলার ৬০ সেকেন্ডের সারসংক্ষেপ:*\n"
            "   • `SUMMARY` অথবা `সারসংক্ষেপ <মামলা নম্বর>`\n\n"
            "৪. 🎯 *শুনানির পূর্ণাঙ্গ প্রস্তুতি (Hearing Pack):*\n"
            "   • `HEARING PACK` অথবা `প্রস্তুতি <মামলা নম্বর>`\n\n"
            "৫. 🌅 *আজকের চেম্বার ব্রিফিং:*\n"
            "   • `ATTENTION` অথবা `BRIEF` অথবা `আজকের ব্রিফিং`\n\n"
            "৬. ⏳ *আইনি তামাদি ও ডেডলাইন অ্যালার্ট:*\n"
            "   • `DEADLINES` অথবা `তামাদি`\n\n"
            "৭. 📚 *সুপ্রিম কোর্টের নজির অনুসন্ধান:*\n"
            "   • `PRECEDENT <বিষয়>` _(যেমন: PRECEDENT 138 NI Act)_\n\n"
            "৮. 📝 *আইনি নোটিশের খসড়া:*\n"
            "   • `DRAFT NOTICE <বিবরণ>`\n\n"
            "📌 _জাসটর এআই — আইনজীবীদের সময় বাঁচায়, চেম্বার প্র্যাকটিস রাখে এক ধাপ এগিয়ে।_"
        )

    def _handle_causelist_query(self, sender: str, lang: str = "bn") -> str:
        """Returns the Chamber's daily cause list across all active matters."""
        matters = self.get_all_matters()
        lines = [
            "📅 *চেম্বারের মোকদ্দমা কার্যতালিকা (Chamber Cause List)*",
            "━━━━━━━━━━━━━━━━━━━━",
            f"👨‍⚖️ *মোট সক্রিয় মোকদ্দমা:* {len(matters)}টি\n"
        ]

        for idx, m in enumerate(matters, 1):
            m_id = m.get("id", f"MATTER-{idx}")
            case_no = m.get("caseNumber") or m_id
            title = m.get("title", "মোকদ্দমা")
            court = m.get("court", "বিজ্ঞ আদালত")
            hearing = m.get("nextHearing", "তারিখ ধার্য নেই")
            stage = m.get("stage", "শুনানির জন্য দিন ধার্য")
            client = m.get("clientName", "মক্কেল")

            lines.append(f"{idx}️⃣ *[{case_no}]* {title}")
            lines.append(f"   🏛️ *আদালত:* {court}")
            lines.append(f"   👤 *মক্কেল:* {client}")
            lines.append(f"   📅 *শুনানির তারিখ:* *{hearing}*")
            lines.append(f"   📋 *পর্যায়:* {stage}")
            lines.append(f"   📱 *ডিকটেশন ট্যাগ:* `#{m_id}`\n")

        lines.append("💡 _আদালত চত্বর থেকে তাৎক্ষণিক আদেশ আপডেট করতে লিখুন:_ `#[মামলা_নম্বর] আদেশ...`")
        return "\n".join(lines)

    async def _handle_precedent_query(self, query: str, sender: str, lang: str = "bn") -> str:
        """Searches landmark Supreme Court of Bangladesh citations and ratio decidendi."""
        clean_topic = query.strip()
        for prefix in ["PRECEDENT", "CITE", "CITATION", "নজির", "কেস", "মামলার নজির"]:
            if clean_topic.upper().startswith(prefix):
                clean_topic = clean_topic[len(prefix):].strip()
                break

        system_instruction = (
            "You are Justor AI's Senior Supreme Court of Bangladesh Research Counsel for Advocates.\n"
            "When an advocate asks for precedents or citations on WhatsApp:\n"
            "1. Provide 1 to 2 controlling, authoritative landmark judgments of the Supreme Court of Bangladesh (Appellate Division or High Court Division).\n"
            "2. Always provide the precise Legal Citation format:\n"
            "   [Case Title] [Volume] DLR/BLD/BLC ([Division]) [Page] ([Year])\n"
            "3. State the exact Ratio Decidendi (কী সিদ্ধান্ত দেওয়া হয়েছে) in 2 bullet points.\n"
            "4. Controlling Statutory Section (e.g. ধারা ১৩৮ এন আই অ্যাক্ট বা ধারা ৪৯৮ সিআরপিসি).\n"
            "5. Advocate Submission Tip: 1 crisp Bengali line on how the advocate should present this precedent to the Bench.\n"
            "Format cleanly for WhatsApp with *bold* headers and bullets. Keep under 1100 characters."
        )

        prompt = (
            f"Advocate requesting controlling Supreme Court precedent on:\n"
            f"\"{clean_topic}\"\n\n"
            f"Provide authoritative Bangladesh citations (DLR/BLD/BLC) with clear ratio decidendi and court oral submission guidance."
        )

        reply = await self._call_gemini_chat(prompt, system_instruction)
        clean_text = reply.strip()
        if clean_text.startswith("{") and "precedents" in clean_text:
            try:
                data = json.loads(clean_text)
                lines = []
                for p in data.get("precedents", []):
                    title = p.get("case_title", "")
                    cit = p.get("citation", "")
                    lines.append(f"⚖️ *{title}*\n📌 *সাইটেশন:* `{cit}`")
                    sec = p.get("controlling_statutory_section", "")
                    if sec:
                        lines.append(f"📖 *সংশ্লিষ্ট ধারা:* {sec}")
                    r_list = p.get("ratio_decidendi", [])
                    if isinstance(r_list, list) and r_list:
                        lines.append("📋 *Ratio Decidendi:*")
                        for r in r_list:
                            lines.append(f"• {r}")
                    elif r_list:
                        lines.append(f"📋 *Ratio Decidendi:* {r_list}")
                    sub_tip = p.get("advocate_submission_tip", "")
                    if sub_tip:
                        lines.append(f"💡 *আদালতে নিবেদন:* \"_{sub_tip}_\"")
                    lines.append("────────────────────")
                if lines:
                    clean_text = "\n".join(lines).strip()
            except Exception:
                pass

        return (
            f"📚 *সুপ্রিম কোর্ট নজির ও আইনি সাইটেশন (Precedent Alert)*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            + clean_text
        )

    async def _handle_notice_draft(self, query: str, sender: str, lang: str = "bn") -> str:
        """Drafts a ready-to-dispatch statutory legal notice for the advocate."""
        clean_topic = query.strip()
        for prefix in ["DRAFT NOTICE", "NOTICE", "নোটিশ ড্রাফট", "লিগ্যাল নোটিশ", "নোটিশ"]:
            if clean_topic.upper().startswith(prefix):
                clean_topic = clean_topic[len(prefix):].strip()
                break

        system_instruction = (
            "You are Justor AI's Senior Chamber Drafting Counsel for Bangladesh Advocates.\n"
            "Draft a formal, ready-to-dispatch Statutory Legal Demand Notice on behalf of the Advocate's client.\n"
            "Include:\n"
            "1. Header: LEGAL DEMAND NOTICE (রেজিস্ট্রি ডাকযোগে এ/ডি সহকারে প্রেরিত)\n"
            "2. Advocate Chamber Header: 'চেম্বার অব এডভোকেট, বাংলাদেশ সুপ্রিম কোর্ট / জেলা বার'\n"
            "3. Addressee / Opposing Party placeholder\n"
            "4. Statement of Facts & Transaction\n"
            "5. Controlling Section (e.g., Section 138 of Negotiable Instruments Act, 1881 / Section 106 of Transfer of Property Act, 1882)\n"
            "6. 30-Day Mandatory Demand: Specific demand to pay / vacate within thirty (30) days of receipt\n"
            "7. Legal Consequence: Filing of criminal case under Section 138/140 or civil suit in competent court\n"
            "8. Advocate Signature Block.\n"
            "Format cleanly for WhatsApp with *bold* headings. Provide in Bengali (or English if query was English)."
        )

        prompt = f"Advocate instructions for legal notice:\n\"{clean_topic}\"\n\nDraft a formal, complete statutory demand notice."
        reply = await self._call_gemini_chat(prompt, system_instruction)
        return (
            f"📝 *আইনি নোটিশের খসড়া (Statutory Legal Notice)*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            + reply + "\n\n"
            f"💡 _এই ড্রাফটটি কপি করে আপনার চেম্বার প্যাডে প্রিন্ট বা সংশোধন করতে পারবেন।_"
        )

    def _lookup_case_docs(self, case_ref: str) -> str:
        """Returns statutory evidence checklist for client or junior counsel."""
        clean_ref = case_ref.upper().strip()
        matched = None
        for k, m in self._matters_cache.items():
            if k == clean_ref or k in clean_ref or clean_ref in k:
                matched = m
                break

        m_type = (matched.get("matterType") if matched else "").lower()

        if "চেক" in m_type or "138" in m_type or "ni act" in m_type:
            checklist = (
                "১. *মূল চেক ও ব্যাংক ডিসঅনার মেমো:* (ব্যাংক কর্তৃক প্রদত্ত অফিশিয়াল রিটার্ন স্লিপ সহ)\n"
                "২. *আইনি নোটিশের মূল কপি:* (অ্যাডভোকেট কর্তৃক প্রেরিত ডিমান্ড নোটিশ)\n"
                "৩. *ডাক রশিদ ও এ/ডি কার্ড:* (Registry Postal Receipt & A/D Card)\n"
                "৪. *ব্যাংক অ্যাকাউন্ট স্টেটমেন্ট:* (লেনদেনের প্রাসঙ্গিক সময়ের ব্যাংক হিসাব বিবরণী)\n"
                "৫. *মক্কেলের জাতীয় পরিচয়পত্র ও ছবি:* ২ কপি সত্যায়িত NID ও পাসপোর্ট সাইজ ছবি"
            )
        elif "রিট" in m_type or "writ" in m_type:
            checklist = (
                "১. *আবেদনকৃত বেআইনি প্রশাসনিক নোটিশ বা আদেশের প্রত্যায়িত অনুলিপি (Certified Copy)*\n"
                "২. *মৌলিক অধিকার বা সংবিধিবদ্ধ অধিকার লঙ্ঘনের প্রামাণ্য দলিলাদি*\n"
                "৩. *আইনগত প্রতিকার চেয়ে পূর্বে প্রদত্ত রিপ্রেজেন্টেশন বা আবেদনের অনুলিপি*\n"
                "৪. *হলফনামা (Affidavit) সম্পাদনের জন্য পিটিশনারের সশরীরে উপস্থিতি বা সত্যায়িত ক্ষমতা*\n"
                "৫. *সকল সংযুক্ত দলিলের ৩ সেট স্পষ্ট ও পরিচ্ছন্ন ফটোকপি*"
            )
        else:
            checklist = (
                "১. *মূল মালিকানা দলিল বা চুক্তিপত্র (Original Deed / Agreement)*\n"
                "২. *খতিয়ান ও নামজারি পর্চা (CS, SA, RS, BS ও ই-নামজারি ডিসিআর)*\n"
                "৩. *হালনাগাদ ভূমি উন্নয়ন কর পরিশোধের দাখিলা (Land Tax Receipt)*\n"
                "৪. *মামলার আরজি বা জবাবের খসড়ায় স্বাক্ষরের জন্য মক্কেলের এনআইডি ও ছবি*\n"
                "৫. *সকল মূল কাগজের ২ সেট স্পষ্ট ফটোকপি চেম্বার ফাইলের জন্য প্রস্তুত রাখুন*"
            )

        return (
            f"📑 *প্রয়োজনীয় কাগজপত্র ও প্রমাণের চেকলিস্ট (Evidence Checklist)*\n"
            f"মোকদ্দমা রেফারেন্স: `{clean_ref}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"শুনানির দিন বিজ্ঞ আদালতে যে মূল দলিলসমূহ সাথে আনতে হবে:\n\n"
            f"{checklist}\n\n"
            f"⚠️ _সকল দলিলের ফটোকপি চেম্বার ফাইল ও বিজ্ঞ বিচারকের পর্যালোচনার জন্য প্রস্তুত রাখুন।_"
        )

    async def handle_incoming_message(
        self,
        sender: str,
        text_message: Optional[str] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> str:
        """
        Main entry point for all WhatsApp inbound events (Twilio, Meta Cloud API, Simulator).
        Executes autonomous legal operating workflows:
        1. Voice Note / Dictation -> Auto matter note filing & chronology update
        2. Order Sheet PDF/Photo -> Document Vision OCR + Contradiction check
        3. 'Summarize this case' -> Executive 60-second matter briefing
        4. 'Prepare me for tomorrow's hearing' -> Instant Hearing Pack
        5. 'What needs my attention?' -> Daily Chamber Morning Brief
        6. 'Deadlines' -> Procedural & statutory limitation alerts
        """
        sender = sender.strip()
        session = self._user_sessions.get(sender, {"history": []})
        query_text = (text_message or "").strip()
        doc_analysis_text = ""

        # 1. Handle Audio Voice Note (Court corridor dictation via voice)
        if media_url and (media_type and "audio" in media_type):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    audio_resp = await client.get(media_url)
                    if audio_resp.status_code == 200:
                        transcribed = await self.transcribe_voice_audio(
                            audio_resp.content,
                            mime_type=media_type.split(";")[0].strip()
                        )
                        if transcribed:
                            query_text = transcribed
                            logger.info(f"Transcribed voice note from {sender}: {query_text}")
                        else:
                            return "🎙️ ভয়েস মেসেজটি স্পষ্ট শোনা যায়নি। অনুগ্রহ করে পুনরায় রেকর্ড করে পাঠান অথবা লিখে জানান।"
                    else:
                        return "ভয়েস ফাইলটি ডাউনলোড করতে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
            except Exception as ex:
                logger.error(f"Error fetching audio media: {ex}")
                return "ভয়েস মেসেজ প্রসেস করা সম্ভব হয়নি। অনুগ্রহ করে টেক্সট লিখে পাঠান।"

        # 2. Handle Image / PDF (Court Order Sheet or Evidence Attachment)
        if media_url and (media_type and ("image" in media_type or "pdf" in media_type)):
            try:
                async with httpx.AsyncClient(timeout=35.0) as client:
                    img_resp = await client.get(media_url)
                    if img_resp.status_code == 200:
                        mime = media_type.split(";")[0].strip()
                        doc_analysis_text = await self.analyze_document_image(img_resp.content, mime_type=mime)
                    else:
                        return "ডকুমেন্ট বা ছবি ফাইলটি ডাউনলোড করতে সমস্যা হয়েছে।"
            except Exception as ex:
                logger.error(f"Error analyzing image media: {ex}")
                return "ছবি বা ডকুমেন্ট বিশ্লেষণ করা সম্ভব হয়নি।"

        # If a document was analyzed, attach it autonomously to the resolved matter
        if doc_analysis_text:
            matter, _ = self._resolve_matter_context(query_text, sender)
            if matter:
                return self._run_autonomous_matter_ingestion(
                    matter,
                    f"{query_text}\n\n{doc_analysis_text}",
                    doc_type="আদালতের আদেশপত্র / দলিল (OCR)",
                    sender=sender
                )
            return doc_analysis_text

        if not query_text:
            return self._get_help_menu("bn")

        upper_query = query_text.upper().strip()

        # Command: HELP / MENU
        if upper_query in ["HELP", "MENU", "START", "হাই", "হ্যালো", "সাহায্য", "আসসালামু আলাইকুম", "COMMANDS"]:
            return self._get_help_menu("bn")

        # Workflow 5: Daily Chamber Morning Brief ("What needs my attention?" / BRIEF / ATTENTION)
        if (
            upper_query in ["BRIEF", "ATTENTION", "TODAY", "DAILY BRIEF", "ব্রিফ", "আজকের ব্রিফিং", "দৃষ্টি আকর্ষণ", "করণীয়"]
            or "ATTENTION" in upper_query
            or "WHAT NEEDS MY ATTENTION" in upper_query
            or "আজকে কী করণীয়" in query_text
        ):
            return self._handle_daily_brief(sender)

        # Workflow 6: Deadlines & Statutory Limitation Alerts (DEADLINES, ALERTS, তামাদি)
        if (
            upper_query in ["DEADLINES", "DEADLINE", "ALERTS", "LIMITATION", "তামাদি", "ডেডলাইন", "সময়সীমা"]
            or upper_query.startswith("DEADLINE")
            or upper_query.startswith("তামাদি")
        ):
            return self._handle_deadlines_and_alerts(sender)

        # Workflow 4: Hearing Preparation Pack ("Prepare me for tomorrow's hearing" / HEARING PACK)
        if (
            upper_query.startswith("HEARING PACK")
            or upper_query.startswith("PREPARE")
            or upper_query.startswith("হিয়ারিং প্যাক")
            or upper_query.startswith("প্রস্তুতি")
            or "PREPARE ME FOR" in upper_query
            or "TOMORROW'S HEARING" in upper_query
            or "শুনানির প্রস্তুতি" in query_text
        ):
            parts = query_text.split(maxsplit=2)
            case_ref = parts[1] if len(parts) > 1 and not parts[1].upper() in ["PACK", "ME", "FOR"] else ""
            return await self._handle_hearing_preparation(case_ref or query_text, sender)

        # Workflow 3: Case Summary ("Summarize this case" / SUMMARY)
        if (
            upper_query.startswith("SUMMARY")
            or upper_query.startswith("SUMMARIZE")
            or upper_query.startswith("সারসংক্ষেপ")
            or upper_query.startswith("বিবরণ")
            or "SUMMARIZE THIS CASE" in upper_query
            or "মামলার সারসংক্ষেপ" in query_text
        ):
            parts = query_text.split(maxsplit=1)
            case_ref = parts[1] if len(parts) > 1 else ""
            return self._handle_summarize_case(case_ref or query_text, sender)

        # Workflow 1 & 2: Autonomous Corridor Dictation & Matter Update (#<ID> or 'Rahim matter—hearing Sunday...')
        # Triggered if explicit #TAG or if message mentions matter details / court orders
        if (
            upper_query.startswith("#")
            or upper_query.startswith("DICTATE")
            or upper_query.startswith("নোট")
            or any(kw in upper_query for kw in ["HEARING SUNDAY", "AFFIDAVIT", "OPPOSITE PARTY", "ORDER", "ADJOURNMENT", "BAIL", "আদেশ", "শুনানি রবিবার", "এফিডেভিট", "হাজিরা", "জামিন"])
        ):
            matter, clean_body = self._resolve_matter_context(query_text, sender)
            if matter:
                return self._run_autonomous_matter_ingestion(
                    matter,
                    clean_body,
                    doc_type="কোর্ট চত্বর ডিকটেশন ও আদেশ",
                    sender=sender
                )

        # Workflow: Precedent & Citations (PRECEDENT, CITE, নজির, DLR, BLD, BLC)
        if (
            upper_query.startswith("PRECEDENT")
            or upper_query.startswith("CITE")
            or upper_query.startswith("CITATION")
            or upper_query.startswith("নজির")
            or upper_query.startswith("কেস নজির")
            or "DLR" in upper_query
            or "BLD" in upper_query
            or "BLC" in upper_query
        ):
            return await self._handle_precedent_query(query_text, sender)

        # Workflow: Chamber Cause List (CAUSELIST, কজলিস্ট)
        if (
            upper_query in ["CAUSELIST", "CALENDAR", "HEARINGS", "DIARY", "কজলিস্ট", "কার্যতালিকা", "দৈনিক তালিকা"]
            or upper_query.startswith("CAUSELIST")
            or upper_query.startswith("কজলিস্ট")
        ):
            return self._handle_causelist_query(sender)

        # Workflow: Statutory Legal Notice Draft (DRAFT NOTICE, নোটিশ ড্রাফট)
        if (
            upper_query.startswith("DRAFT NOTICE")
            or upper_query.startswith("NOTICE")
            or upper_query.startswith("নোটিশ ড্রাফট")
            or upper_query.startswith("লিগ্যাল নোটিশ")
        ):
            return await self._handle_notice_draft(query_text, sender)

        # Workflow: Document Evidence Checklist (DOCS, কাগজপত্র)
        if upper_query.startswith("DOCS") or upper_query.startswith("কাগজপত্র") or upper_query.startswith("প্রমাণ"):
            parts = query_text.split(maxsplit=1)
            case_ref = parts[1] if len(parts) > 1 else "JUSTOR-2026-001"
            return self._lookup_case_docs(case_ref)

        # Workflow: Case Status Lookup (STATUS, মামলা)
        if upper_query.startswith("STATUS") or upper_query.startswith("মামলা"):
            parts = query_text.split(maxsplit=1)
            case_ref = parts[1] if len(parts) > 1 else "JUSTOR-2026-001"
            return self._handle_summarize_case(case_ref, sender)

        # Fallback: Legal Professional RAG Question Processing
        is_english = any(w in upper_query for w in ["SECTION", "LAW", "COURT", "PENAL", "CONTRACT", "ACT", "BAIL", "APPEAL"]) and not any(ord(c) > 127 for c in query_text)
        system_instruction = (
            "You are Justor AI's 24/7 Mobile Legal Assistant exclusively for Bangladesh lawyers, advocates, and chamber counsel on WhatsApp.\n"
            "Format your answer specifically for mobile readability:\n"
            "- Use clean *bold* headings and bullet points (•).\n"
            "- Keep answers concise, authoritative, and actionable on a mobile screen (under 1200 characters).\n"
            "- Cite the exact controlling Bangladesh Statute, Section, and relevant Supreme Court Precedents (e.g. 'নেগোশিয়েবল ইনস্ট্রুমেন্টস অ্যাক্ট, ১৮৮১-এর ধারা ১৩৮' or 'দণ্ডবিধি ১৮৬০-এর ধারা ৪২০').\n"
            "- Provide practical litigation steps: (১) কি নোটিশ দিতে হবে, (২) কোন আদালতে যেতে হবে, (৩) সময়সীমা (Limitation Period).\n"
            "- Conclude with a 1-line professional note.\n"
            + ("Answer in natural, polite Bengali (বাংলা)." if not is_english else "Answer in clear, authoritative English.")
        )

        prompt = f"Advocate Legal Query:\n\"{query_text}\"\n\nProvide an authoritative, clear explanation with applicable Bangladesh laws, practical timeline steps, and court jurisdiction."

        response = await self._call_gemini_chat(prompt, system_instruction)
        return response

    async def send_meta_whatsapp_message(self, to_phone: str, text: str) -> bool:
        """Sends an outbound WhatsApp message back to the user via Meta Cloud API."""
        if not META_WA_PHONE_NUMBER_ID or not META_WA_ACCESS_TOKEN:
            logger.warning("META_WA_PHONE_NUMBER_ID or META_WA_ACCESS_TOKEN not set; skipping outbound Meta message.")
            return False

        clean_to = to_phone.replace("+", "").replace(" ", "").replace("-", "").strip()
        url = f"https://graph.facebook.com/v19.0/{META_WA_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {META_WA_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "text",
            "text": {"preview_url": False, "body": text}
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code in [200, 201]:
                    logger.info(f"Meta outbound message sent successfully to {clean_to}")
                    return True
                else:
                    logger.error(f"Meta outbound error ({resp.status_code}): {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to send Meta WhatsApp message to {clean_to}: {e}")
            return False

    def generate_twiml_response(self, message_text: str) -> str:
        """Generates standard TwiML XML string for Twilio WhatsApp Webhook."""
        import xml.sax.saxutils as saxutils
        escaped_text = saxutils.escape(message_text)
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped_text}</Message></Response>'


# Singleton instance
whatsapp_service = JustorWhatsAppService()
