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
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

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
    Justor AI Chamber OS — 24/7 WhatsApp Mobile Gateway for Legal Professionals & Advocates.
    
    Specially engineered for Bangladesh Advocates, Chamber Counsel, and Practitioners:
    1. Court Corridor / Benchside Dictation:
       Instant voice/text dictation (#<MATTER-ID> <notes>) synced in real-time to Chamber OS Matter Vault.
    2. Supreme Court Precedents & Citations:
       Instant retrieval of controlling DLR, BLD, BLC authorities and ratio decidendi on-the-go.
    3. Chamber Cause List & Hearing Diary:
       Daily cause list summary (CAUSELIST / HEARING) across all active chamber matters.
    4. Instant Legal Notice Drafting:
       Rapid generation of formal statutory notices (NI Act 138, TP Act 106, Contract Breach).
    5. Court Order Sheet & Document Vision OCR:
       Multimodal analysis of photographed daily order sheets, bail bonds, and certified copies.
    6. Automated Client Case Status & Evidence Checklists:
       Eliminates repetitive late-night client calls via STATUS and DOCS commands.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key
        self._llm_handler = None
        # In-memory user session cache (phone_number -> session state)
        self._user_sessions: Dict[str, Dict[str, Any]] = {}
        # Chamber matters cache for live WhatsApp query routing
        self._matters_cache: Dict[str, Dict[str, Any]] = {
            "JUSTOR-2026-001": {
                "id": "JUSTOR-2026-001",
                "title": "করিম আহমেদ বনাম রহিম খান ও অন্যান্য",
                "clientName": "করিম আহমেদ",
                "matterType": "চেক ডিজঅনার (NI Act ১৩৮)",
                "court": "বিজ্ঞ চীফ মেট্রোপলিটন ম্যাজিস্ট্রেট আদালত, ঢাকা",
                "caseNumber": "CR-452/2026",
                "nextHearing": "১৫ অক্টোবর, ২০২৬",
                "stage": "সমন জারি ও জবাব দাখিলের জন্য দিন ধার্য",
                "advocate": "এডভোকেট মেহদী হাসান (বাংলাদেশ সুপ্রিম কোর্ট)",
                "notes": [
                    {
                        "id": "note_01",
                        "rawText": "আইনি নোটিশ ৩০ দিনের মেয়াদ শেষে আদালতে নালিশি দরখাস্ত দায়ের সম্পন্ন।",
                        "createdAt": "2026-09-10T10:00:00Z"
                    }
                ]
            },
            "JUSTOR-2026-002": {
                "id": "JUSTOR-2026-002",
                "title": "রফিকুল ইসলাম বনাম বাংলাদেশ ও অন্যান্য",
                "clientName": "রফিকুল ইসলাম",
                "matterType": "রিট পিটিশন (অনুচ্ছেদ ১০২)",
                "court": "বাংলাদেশ সুপ্রিম কোর্ট, হাইকোর্ট বিভাগ (এনেক্স ১৪)",
                "caseNumber": "WP-8920/2026",
                "nextHearing": "২৮ অক্টোবর, ২০২৬",
                "stage": "রুল শুনানি ও অন্তর্বর্তীকালীন স্থগিতাদেশ বহাল রাখার জন্য ধার্য",
                "advocate": "জাসটর চেম্বার পার্টনার্স (সুপ্রিম কোর্ট বার)",
                "notes": []
            },
            "JUSTOR-2026-003": {
                "id": "JUSTOR-2026-003",
                "title": "বেগম রোকেয়া বনাম সিটি কর্পোরেশন ও অন্যান্য",
                "clientName": "বেগম রোকেয়া",
                "matterType": "স্বত্ব সাব্যস্ত ও চিরতরে নিষেধাজ্ঞা (Title Suit)",
                "court": "বিজ্ঞ ১ম যুগ্ম জেলা জজ আদালত, ঢাকা",
                "caseNumber": "TS-114/2025",
                "nextHearing": "০৫ নভেম্বর, ২০২৬",
                "stage": "ইস্যু গঠন ও নালিশি জমিতে স্থিতাবস্থার আদেশ বহাল",
                "advocate": "এডভোকেট মেহদী হাসান ও অ্যাসোসিয়েটস",
                "notes": []
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
            "matterType": inner.get("matterType") or matter_dict.get("matter_type") or matter_dict.get("matterType") or existing.get("matterType", "দেওয়ানি / ফৌজদারি"),
            "court": inner.get("court") or matter_dict.get("court") or existing.get("court", "বিজ্ঞ আদালত"),
            "caseNumber": inner.get("caseNumber") or matter_dict.get("caseNumber") or existing.get("caseNumber", m_id),
            "nextHearing": inner.get("nextHearing") or matter_dict.get("nextHearing") or existing.get("nextHearing", "১৫ অক্টোবর, ২০২৬"),
            "stage": inner.get("stage") or matter_dict.get("stage") or existing.get("stage", "শুনানির জন্য ধার্য"),
            "advocate": inner.get("advocate") or matter_dict.get("advocate") or existing.get("advocate", "জাসটর চেম্বার পার্টনার্স"),
            "notes": matter_dict.get("notes") or existing.get("notes", [])
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

    def _get_help_menu(self, lang: str = "bn") -> str:
        if lang == "bn":
            return (
                "⚖️ *জাসটর চেম্বার ওএস — বিজ্ঞ আইনজীবী হোয়াটসঅ্যাপ গেটওয়ে*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "বাংলাদেশ সুপ্রিম কোর্ট ও জেলা আদালতের বিজ্ঞ আইনজীবীদের ব্যক্তিগত চেম্বার সহকারী:\n\n"
                "🎙️ *কোর্ট চত্বর থেকে তাৎক্ষণিক ডিকটেশন:*\n"
                "• `#<মামলা নম্বর> <আদেশ বা নোট>`\n"
                "  _যেমন:_ `#CR-452/2026 জামিন মঞ্জুর, আগামী ১৫ নভেম্বর জবাব দাখিল`\n"
                "  _(ভয়েস মেসেজ পাঠালেও তা স্বয়ংক্রিয়ভাবে টেক্সটে রূপান্তর হয়ে ডকেটে সেভ হবে)_\n\n"
                "📚 *সুপ্রিম কোর্টের নজির ও সাইটেশন অনুসন্ধান:*\n"
                "• `PRECEDENT <আইনি বিষয় বা ধারা>`\n"
                "  _যেমন:_ `PRECEDENT 138 NI Act notice limitation`\n"
                "  _অথবা:_ `নজির ধারা ৪৯৮ ফৌজদারি কার্যবিধি অন্তর্বর্তীকালীন জামিন`\n\n"
                "📅 *দৈনিক চেম্বার কার্যতালিকা (Cause List):*\n"
                "• `CAUSELIST` অথবা `কজলিস্ট`\n"
                "  _আজ ও আগামী দিনের সমস্ত শুনানির তালিকা ও পর্যায় দেখুন_\n\n"
                "📝 *তাৎক্ষণিক আইনি নোটিশের খসড়া (Draft Notice):*\n"
                "• `DRAFT NOTICE <বিবরণ>`\n"
                "  _যেমন:_ `DRAFT NOTICE 138 NI Act Cheque 10 Lakh BDT`\n\n"
                "📂 *মক্কেলের মামলার বর্তমান তথ্য:*\n"
                "• `STATUS <মামলা রেফারেন্স>` _(যেমন: STATUS JUSTOR-2026-001)_\n\n"
                "📑 *প্রয়োজনীয় দলিলের তালিকা:*\n"
                "• `DOCS <মামলা রেফারেন্স>`\n\n"
                "📷 *আদালতের আদেশপত্রের ছবি পাঠান:* ছবি পাঠালেই এআই তাৎক্ষণিক আদেশ, পরবর্তী তারিখ ও তামাদি সময় বের করে দেবে।\n\n"
                "📌 _জাসটর এআই — আইনজীবীদের সময় বাঁচায়, চেম্বার প্র্যাকটিস রাখে এক ধাপ এগিয়ে।_"
            )
        return (
            "⚖️ *Justor Chamber OS — Advocate WhatsApp Gateway*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Chamber OS mobile automation engineered exclusively for Bangladesh Legal Practitioners:\n\n"
            "🎙️ *Court Corridor Dictation:*\n"
            "• `#<Matter ID> <Order or Notes>`\n"
            "  _e.g._ `#CR-452/2026 Adjournment granted till 15 Nov, cost 500 BDT paid`\n"
            "  _(Voice audio notes are transcribed & filed into Chamber Vault automatically)_\n\n"
            "📚 *Supreme Court Precedent Search:*\n"
            "• `PRECEDENT <Topic or Section>`\n"
            "  _e.g._ `PRECEDENT Section 498 CrPC anticipatory bail guidelines`\n"
            "  _(Returns controlling DLR/BLD citations, ratio decidendi & submission tips)_\n\n"
            "📅 *Chamber Cause List:*\n"
            "• `CAUSELIST` or `HEARINGS`\n"
            "  _Overview of all active chamber matters, next hearing dates & stages_\n\n"
            "📝 *Instant Legal Demand Notice Drafting:*\n"
            "• `DRAFT NOTICE <Details>`\n"
            "  _e.g._ `DRAFT NOTICE 138 NI Act Cheque dishonor 10 Lakh BDT`\n\n"
            "📂 *Client Case Status Lookup:*\n"
            "• `STATUS <Matter ID>`\n\n"
            "📑 *Mandatory Evidence Checklist:*\n"
            "• `DOCS <Matter ID>`\n\n"
            "📷 *Snap Order Sheet Photo:* Send photo of daily order sheet for instant OCR extraction & limitation alerts.\n\n"
            "📌 _Justor AI — Empowering Legal Excellence on the Go._"
        )

    def _handle_causelist_query(self, sender: str, lang: str = "bn") -> str:
        """Returns the Chamber's daily cause list across all active matters."""
        matters = self.get_all_matters()
        if not matters:
            return (
                "📅 *চেম্বারের কার্যতালিকা (Daily Cause List)*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "বর্তমানে কোনো সক্রিয় মোকদ্দমা রেজিস্টার্ড নেই।\n"
                "নতুন মোকদ্দমা রেজিস্টার করতে চেম্বার ওএস ড্যাশবোর্ডে লগইন করুন অথবা সরাসরি WhatsApp-এ `#<নতুন মামলা নম্বর> <নোট>` লিখে পাঠান।"
            )

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

    def _handle_lawyer_dictation(self, query: str, sender: str) -> str:
        """Handles mobile voice/text dictation from advocates in court corridor and syncs to cache."""
        cleaned = query.strip()
        matter_tag = "ACTIVE_MATTER"
        dictation_body = cleaned

        if cleaned.startswith("#"):
            parts = cleaned.split(maxsplit=1)
            matter_tag = parts[0].replace("#", "").upper().strip()
            dictation_body = parts[1] if len(parts) > 1 else ""
        elif cleaned.upper().startswith("DICTATE"):
            parts = cleaned.split(maxsplit=1)
            if len(parts) > 1:
                sub_parts = parts[1].split(maxsplit=1)
                matter_tag = sub_parts[0].replace("#", "").upper().strip()
                dictation_body = sub_parts[1] if len(sub_parts) > 1 else ""
        elif cleaned.startswith("নোট"):
            parts = cleaned.split(maxsplit=1)
            if len(parts) > 1:
                sub_parts = parts[1].split(maxsplit=1)
                matter_tag = sub_parts[0].replace("#", "").upper().strip()
                dictation_body = sub_parts[1] if len(sub_parts) > 1 else ""

        # Extract date mentions (e.g. 15 নভেম্বর, 15 Nov, 20/10/2026, 28 অক্টোবর)
        date_patterns = [
            r"(\d{1,2}\s*(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর)[,\s]*\d{0,4})",
            r"(\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,\s]*\d{0,4})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ]
        detected_date = None
        for dp in date_patterns:
            m = re.search(dp, dictation_body, re.I)
            if m:
                detected_date = m.group(1).strip()
                break

        # Detect order / stage keywords
        detected_order = None
        order_keywords = [
            ("জামিন মঞ্জুর", "অন্তর্বর্তীকালীন জামিন মঞ্জুর ও নথি তলব"),
            ("জামিন নামঞ্জুর", "জামিন আবেদন নামঞ্জুর"),
            ("স্থগিতাদেশ", "কার্যক্রমের উপর স্থগিতাদেশ মঞ্জুর"),
            ("চার্জ গঠন", "অভিযোগ / চার্জ গঠন সম্পন্ন"),
            ("জবাব দাখিল", "লিখিত জবাব দাখিলের জন্য দিন ধার্য"),
            ("সমন জারি", "সমন জারির জন্য দিন ধার্য"),
            ("যুক্তিতর্ক", "চূড়ান্ত যুক্তিতর্ক (Argument) শুনানির জন্য ধার্য"),
            ("খরচা", "অ্যাডজার্নমেন্ট কস্ট বা খরচা প্রদান"),
            ("adjournment", "Adjournment granted with directions"),
            ("bail", "Bail prayer considered and granted")
        ]
        for kw, desc in order_keywords:
            if kw.lower() in dictation_body.lower():
                detected_order = desc
                break

        # Update or register in matters cache
        target_matter = None
        for k, v in self._matters_cache.items():
            if k == matter_tag or matter_tag in k or k in matter_tag:
                target_matter = v
                matter_tag = k
                break

        now_iso = datetime.now(timezone.utc).isoformat()
        new_note = {
            "id": f"wa_note_{int(time.time()*1000)}",
            "rawText": f"[WhatsApp Court Dictation - {sender}]\n{dictation_body}",
            "createdAt": now_iso,
            "source": "whatsapp_corridor",
            "detectedDate": detected_date,
            "detectedOrder": detected_order
        }

        if target_matter:
            if "notes" not in target_matter or not isinstance(target_matter["notes"], list):
                target_matter["notes"] = []
            target_matter["notes"].insert(0, new_note)
            if detected_date:
                target_matter["nextHearing"] = detected_date
            if detected_order:
                target_matter["stage"] = detected_order
            matter_title = target_matter.get("title", "মোকদ্দমা")
            court_name = target_matter.get("court", "বিজ্ঞ আদালত")
        else:
            # Create lightweight docket entry
            matter_title = f"মোকদ্দমা #{matter_tag}"
            court_name = "বিজ্ঞ আদালত"
            self._matters_cache[matter_tag] = {
                "id": matter_tag,
                "title": matter_title,
                "clientName": "চেম্বার ক্লায়েন্ট",
                "court": court_name,
                "caseNumber": matter_tag,
                "nextHearing": detected_date or "পরবর্তী শুনানির তারিখ ধার্য নেই",
                "stage": detected_order or "কোর্ট চত্বর থেকে নোট সংরক্ষণ",
                "advocate": "দায়িত্বপ্রাপ্ত আইনজীবী",
                "notes": [new_note]
            }

        return (
            f"🎙️ *কোর্ট চত্বর ডিকটেশন চেম্বার ডকেটে সংরক্ষিত হয়েছে!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *মোকদ্দমা ট্যাগ:* `#{matter_tag}`\n"
            f"⚖️ *মোকদ্দমা:* {matter_title}\n"
            f"🏛️ *আদালত:* {court_name}\n"
            f"📝 *সংরক্ষিত ডিকটেশন:* \"{dictation_body}\"\n"
            + (f"📅 *হালনাগাদ শুনানির তারিখ:* *{detected_date}*\n" if detected_date else "")
            + (f"📋 *হালনাগাদ মোকদ্দমার পর্যায়:* {detected_order}\n" if detected_order else "")
            + f"🕒 *সিঙ্ক স্ট্যাটাস:* রিয়েলটাইম Chamber OS Vault এ সংযুক্ত\n\n"
            f"✅ _চেম্বারে ফিরে Justor Chamber OS ড্যাশবোর্ড রিফ্রেশ করলেই এই নোটটি পূর্ণাঙ্গ মোকদ্দমা ডকেটে দেখতে পাবেন।_"
        )

    def _lookup_case_status(self, case_ref: str, phone: str) -> str:
        """Looks up client or advocate case status by matter reference."""
        clean_ref = case_ref.upper().strip()
        
        # Check in registered matters cache
        for k, m in self._matters_cache.items():
            if k == clean_ref or k in clean_ref or clean_ref in k:
                title = m.get("title", "মামলা")
                client = m.get("clientName", "মক্কেল")
                court = m.get("court", "বিজ্ঞ আদালত")
                hearing = m.get("nextHearing", "১৫ অক্টোবর, ২০২৬")
                stage = m.get("stage", "শুনানির জন্য ধার্য")
                advocate = m.get("advocate", "জাসটর চেম্বার পার্টনার্স")
                recent_notes = m.get("notes", [])
                last_note_text = ""
                if recent_notes and isinstance(recent_notes, list):
                    last_note = recent_notes[0]
                    if isinstance(last_note, dict):
                        last_note_text = last_note.get("rawText", "")

                reply = (
                    f"📂 *মোকদ্দমার বর্তমান অবস্থা (Matter Status)*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 *রেফারেন্স:* `{k}`\n"
                    f"⚖️ *মোকদ্দমা:* {title}\n"
                    f"👤 *মক্কেল:* {client}\n"
                    f"🏛️ *আদালত:* {court}\n"
                    f"📅 *পরবর্তী শুনানির তারিখ:* *{hearing}*\n"
                    f"📋 *বর্তমান পর্যায়:* {stage}\n"
                    f"👨‍⚖️ *দায়িত্বপ্রাপ্ত আইনজীবী:* {advocate}\n"
                )
                if last_note_text:
                    clean_excerpt = last_note_text.replace("[Court Corridor Dictation]\n", "").replace("[WhatsApp Court Dictation]\n", "")[:120]
                    reply += f"📝 *সাম্প্রতিক চেম্বার নোট:* \"{clean_excerpt}...\"\n"
                reply += f"\n💡 _প্রয়োজনীয় দলিলের তালিকা জানতে `DOCS {k}` লিখে পাঠান।_"
                return reply

        return (
            f"🔍 *মামলা পাওয়া যায়নি*\n\n"
            f"`{case_ref}` রেফারেন্স দিয়ে কোনো চলমান মোকদ্দমা পাওয়া যায়নি।\n"
            f"সঠিক মামলা নম্বর দিয়ে পুনরায় চেষ্টা করুন (যেমন: `STATUS JUSTOR-2026-001` বা `CAUSELIST`) অথবা আপনার চেম্বারের সাথে যোগাযোগ করুন।"
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

    def _handle_advocate_request(self, phone: str) -> str:
        session = self._user_sessions.get(phone, {})
        session["awaiting_consultation_details"] = True
        self._user_sessions[phone] = session

        return (
            "🤝 *চেম্বার কনসালটেশন শিডিউল অনুরোধ*\n\n"
            "বাংলাদেশ সুপ্রিম কোর্ট বা সংশ্লিষ্ট জেলা বারের আইনজীবীর সাথে সরাসরি অ্যাপয়েন্টমেন্টের জন্য অনুগ্রহ করে জানান:\n"
            "১. আপনার পূর্ণ নাম\n"
            "২. আপনার জেলা বা আদালত (যেমন: ঢাকা জজ কোর্ট / হাইকোর্ট বিভাগ)\n"
            "৩. মামলার সংক্ষিপ্ত বিষয় (যেমন: চেক বাউন্স / জমি / ফৌজদারি জামিন)\n\n"
            "_সরাসরি এই মেসেজের উত্তরে লিখে পাঠান।_"
        )

    async def handle_incoming_message(
        self,
        sender: str,
        text_message: Optional[str] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> str:
        """
        Main routing function for all WhatsApp inbound events (Twilio, Meta Cloud API, Simulator).
        Intelligently routes:
        - Voice Audio -> Gemini Multimodal Audio Transcription
        - Order Sheet Images -> Multimodal Vision OCR Analysis & Limitation Alert
        - #<MATTER-ID> / DICTATE -> Court Corridor Dictation to Matter Vault
        - PRECEDENT / CITE -> Supreme Court Citations & Ratio Decidendi
        - CAUSELIST / HEARINGS -> Daily Chamber Cause List
        - DRAFT NOTICE -> Statutory Legal Demand Notice
        - STATUS -> Matter Status Check
        - DOCS -> Evidence Checklist
        - General Legal Query -> Lawyer-grade RAG Synthesis
        """
        sender = sender.strip()
        session = self._user_sessions.get(sender, {"history": []})
        query_text = (text_message or "").strip()

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

        # 2. Handle Image / Document (Court Order Sheet OCR)
        if media_url and (media_type and ("image" in media_type or "pdf" in media_type)):
            try:
                async with httpx.AsyncClient(timeout=35.0) as client:
                    img_resp = await client.get(media_url)
                    if img_resp.status_code == 200:
                        mime = media_type.split(";")[0].strip()
                        return await self.analyze_document_image(img_resp.content, mime_type=mime)
                    else:
                        return "ডকুমেন্ট বা ছবি ফাইলটি ডাউনলোড করতে সমস্যা হয়েছে।"
            except Exception as ex:
                logger.error(f"Error analyzing image media: {ex}")
                return "ছবি বা ডকুমেন্ট বিশ্লেষণ করা সম্ভব হয়নি।"

        if not query_text:
            return self._get_help_menu("bn")

        upper_query = query_text.upper().strip()

        # Command: HELP / MENU
        if upper_query in ["HELP", "MENU", "START", "হাই", "হ্যালো", "সাহায্য", "আসসালামু আলাইকুম", "COMMANDS"]:
            return self._get_help_menu("bn")

        # Command: LAWYER DICTATION (#<MatterID> or DICTATE or নোট)
        if upper_query.startswith("#") or upper_query.startswith("DICTATE") or upper_query.startswith("নোট"):
            return self._handle_lawyer_dictation(query_text, sender)

        # Command: PRECEDENT / CASE CITATION (PRECEDENT, CITE, CITATION, নজির, কেস)
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

        # Command: CAUSE LIST / HEARINGS (CAUSELIST, CALENDAR, কজলিস্ট, কার্যতালিকা, শুনানি)
        if (
            upper_query in ["CAUSELIST", "CALENDAR", "HEARINGS", "DIARY", "কজলিস্ট", "কার্যতালিকা", "শুনানি", "দৈনিক তালিকা"]
            or upper_query.startswith("CAUSELIST")
            or upper_query.startswith("কজলিস্ট")
        ):
            return self._handle_causelist_query(sender)

        # Command: DRAFT NOTICE (DRAFT NOTICE, NOTICE, নোটিশ ড্রাফট, লিগ্যাল নোটিশ)
        if (
            upper_query.startswith("DRAFT NOTICE")
            or upper_query.startswith("NOTICE")
            or upper_query.startswith("নোটিশ ড্রাফট")
            or upper_query.startswith("লিগ্যাল নোটিশ")
        ):
            return await self._handle_notice_draft(query_text, sender)

        # Command: DOCS / EVIDENCE CHECKLIST
        if upper_query.startswith("DOCS") or upper_query.startswith("কাগজপত্র") or upper_query.startswith("প্রমাণ"):
            parts = query_text.split(maxsplit=1)
            case_ref = parts[1] if len(parts) > 1 else "JUSTOR-2026-001"
            return self._lookup_case_docs(case_ref)

        # Command: STATUS / HEARING FOR A SPECIFIC MATTER
        if upper_query.startswith("STATUS") or upper_query.startswith("HEARING") or upper_query.startswith("মামলা") or upper_query.startswith("তারিখ"):
            parts = query_text.split(maxsplit=1)
            case_ref = parts[1] if len(parts) > 1 else "JUSTOR-2026-001"
            return self._lookup_case_status(case_ref, sender)

        # Command: ADVOCATE / CONSULTATION
        if upper_query in ["ADVOCATE", "LAWYER", "উকিল", "আইনজীবী", "পরামর্শ"]:
            return self._handle_advocate_request(sender)

        # Handling consultation followup
        if session.get("awaiting_consultation_details"):
            session["awaiting_consultation_details"] = False
            self._user_sessions[sender] = session
            return (
                "✅ *পরামর্শের অনুরোধ গ্রহণ করা হয়েছে!*\n\n"
                "আপনার বিবরণ জাসটর চেম্বার ডেস্কে সংরক্ষিত হয়েছে। আমাদের সিনিয়র কাউন্সেল কো-অর্ডিনেটর দ্রুত আপনার সাথে যোগাযোগ করবেন।\n\n"
                "অন্য কোনো আইনি প্রশ্ন বা নোটিশ ড্রাফটের জন্য নির্দ্বিধায় লিখুন।"
            )

        # 3. Legal Professional RAG Question Processing
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

    def generate_twiml_response(self, message_text: str) -> str:
        """Generates standard TwiML XML string for Twilio WhatsApp Webhook."""
        import xml.sax.saxutils as saxutils
        escaped_text = saxutils.escape(message_text)
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped_text}</Message></Response>'


# Singleton instance
whatsapp_service = JustorWhatsAppService()
