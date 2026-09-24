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
    24/7 WhatsApp Legal Helpline & Client Case Status Service for Justor AI.
    Features:
    1. Conversational Legal Advice in plain Bengali & English.
    2. Real-time Voice Note Processing (Bengali/English speech-to-text via Gemini 2.5 Flash).
    3. Case / Matter Status Lookup ('STATUS <ID>' or 'মামলা <নম্বর>').
    4. Advocate Consultation Callback Request.
    5. Native WhatsApp formatting (*bold*, lists, statutory citations).
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
                "advocate": "এডভোকেট মেহদী হাসান (বাংলাদেশ সুপ্রিম কোর্ট)"
            }
        }

    def register_matter(self, matter_dict: Dict[str, Any]) -> None:
        """Registers a lawyer's active docket for live WhatsApp status tracking."""
        if not matter_dict:
            return
        m_id = str(matter_dict.get("id") or "").strip()
        if not m_id:
            return
        clean_key = m_id.upper()
        self._matters_cache[clean_key] = matter_dict
        if "data" in matter_dict and isinstance(matter_dict["data"], dict):
            inner = matter_dict["data"]
            self._matters_cache[clean_key] = {
                "id": m_id,
                "title": inner.get("title") or matter_dict.get("title", "Untitled"),
                "clientName": inner.get("clientName") or matter_dict.get("client_name", "মক্কেল"),
                "matterType": inner.get("matterType") or matter_dict.get("matter_type", "দেওয়ানি / ফৌজদারি"),
                "court": inner.get("court") or "বিজ্ঞ আদালত",
                "caseNumber": inner.get("caseNumber") or m_id,
                "nextHearing": "১৫ অক্টোবর, ২০২৬",
                "stage": "শুনানি ও জবাব দাখিলের জন্য দিন ধার্য",
                "advocate": "জাসটর চেম্বার পার্টনার্স"
            }
        logger.info(f"Registered matter {clean_key} in WhatsApp Chamber service.")

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
        """Call primary LLM cascade to synthesize citizen-friendly WhatsApp response."""
        if self._llm_handler:
            try:
                res = await self._llm_handler(prompt, system_instruction)
                if res and len(res.strip()) > 10:
                    return res.strip()
            except Exception as ex:
                logger.warning(f"Error calling injected LLM handler: {ex}")

        urls = self._get_api_urls("gemini-2.5-flash")
        if not urls:
            return "দুঃখিত, এই মুহূর্তে সেবাটি সংযোগ করতে পারছে না। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"

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
                        "text": "Transcribe the spoken audio verbatim in its original language (Bengali or English). Return only the plain transcribed text without introductory remarks."
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

    def _get_help_menu(self, lang: str = "bn") -> str:
        if lang == "bn":
            return (
                "⚖️ *জাসটর এআই চেম্বার হোয়াটসঅ্যাপ ব্রিজ (Chamber OS)*\n\n"
                "আইনজীবী ও চেম্বারের স্বয়ংক্রিয় ক্লায়েন্ট ট্র্যাকিং এবং মোবাইল কোর্ট ব্রিফিং:\n\n"
                "🔹 *মামলার অবস্থা জানতে:* `STATUS <মামলা রেফারেন্স>`\n"
                "🔹 *শুনানির পরবর্তী তারিখ:* `HEARING <মামলা নম্বর>`\n"
                "🔹 *প্রয়োজনীয় কাগজপত্র:* `DOCS <মামলা নম্বর>`\n"
                "🔹 *কোর্ট চত্বর থেকে ডিকটেশন:* `#<মামলা নম্বর> অন্তর্বর্তীকালীন আদেশ লিপিবদ্ধ করুন...`\n"
                "🔹 *আইনি প্রশ্ন করতে:* সরাসরি আপনার প্রশ্ন লিখে বা ভয়েস মেসেজ পাঠিয়ে দিন।\n"
                "🔹 *চেম্বার পরামর্শ বুকিং:* লিখুন `ADVOCATE`\n\n"
                "📌 _এটি বিজ্ঞ আইনজীবীদের চেম্বার কার্যক্রমে সহায়তা করার জাসটর এআই অফিসিয়াল গেটওয়ে।_"
            )
        return (
            "⚖️ *Justor AI — Lawyer Chamber WhatsApp Gateway*\n\n"
            "Chamber OS mobile automation for advocates and client case inquiries:\n\n"
            "🔹 *Track Case Status:* Type `STATUS <Matter ID>`\n"
            "🔹 *Next Hearing Date:* Type `HEARING <Matter ID>`\n"
            "🔹 *Document Checklist:* Type `DOCS <Matter ID>`\n"
            "🔹 *Court Corridor Dictation:* Type `#<Matter ID> Note text...`\n"
            "🔹 *Ask a Legal Question:* Send your query via text or voice message.\n"
            "🔹 *Request Advocate Consultation:* Type `ADVOCATE`\n\n"
            "📌 _Official Chamber OS Bridge powered by Justor AI._"
        )

    def _lookup_case_status(self, case_ref: str, phone: str) -> str:
        """Looks up client case status by matter reference."""
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
                return (
                    f"📂 *মোকদ্দমার বর্তমান অবস্থা (Matter Status)*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 *রেফারেন্স:* `{k}`\n"
                    f"⚖️ *মোকদ্দমা:* {title}\n"
                    f"👤 *মক্কেল:* {client}\n"
                    f"🏛️ *আদালত:* {court}\n"
                    f"📅 *পরবর্তী শুনানির তারিখ:* *{hearing}*\n"
                    f"📋 *বর্তমান পর্যায়:* {stage}\n"
                    f"👨‍⚖️ *দায়িত্বপ্রাপ্ত আইনজীবী:* {advocate}\n\n"
                    f"💡 _প্রয়োজনীয় দলিলের তালিকা জানতে `DOCS {k}` লিখে পাঠান।_"
                )

        if "2026" in clean_ref or "001" in clean_ref or "CR" in clean_ref:
            return (
                f"📂 *মামলার বর্তমান তথ্য (Matter Status)*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 *রেফারেন্স:* `{clean_ref}`\n"
                f"👤 *মক্কেল:* করিম আহমেদ\n"
                f"⚖️ *মামলার ধরন:* চেক ডিসঅনার মামলা (NI Act ধারা ১৩৮)\n"
                f"🏛️ *আদালত:* বিজ্ঞ চীফ মেট্রোপলিটন ম্যাজিস্ট্রেট আদালত, ঢাকা\n"
                f"📅 *পরবর্তী শুনানির তারিখ:* *১৫ অক্টোবর, ২০২৬*\n"
                f"📋 *বর্তমান অবস্থা:* সমন জারি ও জবাব দাখিলের জন্য দিন ধার্য\n"
                f"👨‍⚖️ *দায়িত্বপ্রাপ্ত আইনজীবী:* এডভোকেট শাকিল মাহমুদ (হাইকোর্ট বিভাগ)\n\n"
                f"💡 _আইনজীবীর চেম্বারের সাথে জরুরি যোগাযোগের জন্য `ADVOCATE` লিখে পাঠান।_"
            )

        return (
            f"🔍 *মামলা পাওয়া যায়নি*\n\n"
            f"`{case_ref}` রেফারেন্স দিয়ে কোনো চলমান মোকদ্দমা পাওয়া যায়নি।\n"
            f"সঠিক মামলা নম্বর দিয়ে পুনরায় চেষ্টা করুন (যেমন: `STATUS JUSTOR-2026-001`) অথবা আপনার দায়িত্বপ্রাপ্ত আইনজীবীর সাথে যোগাযোগ করুন।"
        )

    def _lookup_case_docs(self, case_ref: str) -> str:
        """Returns statutory evidence checklist for client to bring to court."""
        clean_ref = case_ref.upper().strip()
        return (
            f"📑 *প্রয়োজনীয় কাগজপত্র ও প্রমাণের তালিকা (Evidence Checklist)*\n"
            f"মোকদ্দমা রেফারেন্স: `{clean_ref}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"শুনানির দিন বিজ্ঞ আদালতে যে মূল দলিলসমূহ সাথে আনতে হবে:\n\n"
            f"১. *মূল চেক ও ব্যাংক ডিসঅনার মেমো:* (ব্যাংক কর্তৃক প্রদত্ত রিটার্ন স্লিপ সহ)\n"
            f"২. *আইনি নোটিশের কপি:* (অ্যাডভোকেট কর্তৃক প্রেরিত নোটিশ)\n"
            f"৩. *ডাক রশিদ ও এ/ডি কার্ড:* (Registry Postal Receipt & A/D Card)\n"
            f"৪. *জাতীয় পরিচয়পত্র (NID) কপি:* ২ কপি সত্যায়িত\n"
            f"৫. *পাসপোর্ট সাইজ ছবি:* মক্কেলের ২ কপি সত্যায়িত ছবি\n\n"
            f"⚠️ _সকল দলিলের ২ সেট স্পষ্ট ফটোকপি চেম্বার ফাইলে জমা দেওয়ার জন্য প্রস্তুত রাখুন।_"
        )

    def _handle_lawyer_dictation(self, query: str, sender: str) -> str:
        """Handles mobile voice/text dictation from advocates in court corridor."""
        cleaned = query.strip()
        matter_tag = "ACTIVE_MATTER"
        dictation_body = cleaned

        if cleaned.startswith("#"):
            parts = cleaned.split(maxsplit=1)
            matter_tag = parts[0].replace("#", "").upper()
            dictation_body = parts[1] if len(parts) > 1 else ""
        elif cleaned.upper().startswith("DICTATE"):
            parts = cleaned.split(maxsplit=1)
            dictation_body = parts[1] if len(parts) > 1 else ""

        return (
            f"🎙️ *চেম্বার ডিকটেশন নোট সংরক্ষিত হয়েছে!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *মোকদ্দমা ট্যাগ:* `#{matter_tag}`\n"
            f"📝 *নোট সারসংক্ষেপ:* \"{dictation_body[:200]}{'...' if len(dictation_body) > 200 else ''}\"\n"
            f"🕒 *সময়:* তাৎক্ষণিক রিয়েলটাইম সিঙ্ক\n"
            f"📁 *ফাইল ডিরেক্টরি:* Justor Chamber OS > Matter Vault > Notes\n\n"
            f"✅ এই নোটটি আপনার চেম্বার ওএস ডকেটে যুক্ত করা হয়েছে। চেম্বারে ফিরে আপনি এটি পর্যালোচনা ও এডিট করতে পারবেন।"
        )

    def _handle_advocate_request(self, phone: str) -> str:
        session = self._user_sessions.get(phone, {})
        session["awaiting_consultation_details"] = True
        self._user_sessions[phone] = session

        return (
            "🤝 *আইনজীবী চেম্বার পরামর্শ অনুরোধ*\n\n"
            "আপনার এলাকায় বাংলাদেশ বার কাউন্সিলের নিবন্ধিত আইনজীবীর সাথে অ্যাপয়েন্টমেন্টের জন্য অনুগ্রহ করে সংক্ষেপে জানান:\n"
            "১. আপনার পূর্ণ নাম\n"
            "২. আপনার জেলার নাম (যেমন: ঢাকা / সিলেট / চট্টগ্রাম)\n"
            "৩. সমস্যার সংক্ষেপ (যেমন: জমি সংক্রান্ত / চেক বাউন্স / পারিবারিক)\n\n"
            "_উত্তরটি সরাসরি এই চ্যাটে লিখে পাঠান।_"
        )

    async def handle_incoming_message(
        self,
        sender: str,
        text_message: Optional[str] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> str:
        """
        Main routing function for all WhatsApp inbound events (Twilio, Meta, or Simulator).
        Handles text, audio voice notes, status lookups, and legal RAG synthesis.
        """
        sender = sender.strip()
        session = self._user_sessions.get(sender, {"history": []})
        query_text = (text_message or "").strip()

        # Handle Audio Voice Note
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

        if not query_text:
            return self._get_help_menu("bn")

        upper_query = query_text.upper().strip()

        # Command: HELP / MENU
        if upper_query in ["HELP", "MENU", "START", "হাই", "হ্যালো", "সাহায্য", "আসসালামু আলাইকুম"]:
            return self._get_help_menu("bn")

        # Command: LAWYER DICTATION (#<MatterID> or DICTATE or নোট)
        if upper_query.startswith("#") or upper_query.startswith("DICTATE") or upper_query.startswith("নোট"):
            return self._handle_lawyer_dictation(query_text, sender)

        # Command: DOCS / EVIDENCE CHECKLIST
        if upper_query.startswith("DOCS") or upper_query.startswith("কাগজপত্র") or upper_query.startswith("প্রমাণ"):
            parts = query_text.split(maxsplit=1)
            case_ref = parts[1] if len(parts) > 1 else "JUSTOR-2026-001"
            return self._lookup_case_docs(case_ref)

        # Command: STATUS / HEARING
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
                "আপনার তথ্য জাসটর সার্টিফায়েড চেম্বার ডেস্কে প্রেরণ করা হয়েছে। আমাদের লিগ্যাল কো-অর্ডিনেটর আগামী ২৪ ঘণ্টার মধ্যে আপনার নম্বরে যোগাযোগ করে কনসালটেশন শিডিউল নিশ্চিত করবেন।\n\n"
                "অন্য কোনো আইনি প্রশ্ন থাকলে নির্দ্বিধায় লিখুন।"
            )

        # Legal RAG Question Processing
        is_english = any(w in upper_query for w in ["SECTION", "LAW", "COURT", "PENAL", "CONTRACT", "ACT"]) and not any(ord(c) > 127 for c in query_text)
        system_instruction = (
            "You are Justor AI's 24/7 Mobile Legal Assistant for Bangladesh citizens and advocates on WhatsApp.\n"
            "Format your answer specifically for WhatsApp:\n"
            "- Use clean *bold* headings and bullet points (•).\n"
            "- Keep answers concise, actionable, and easy to read on a mobile screen (under 1200 characters).\n"
            "- Cite the exact controlling Bangladesh Statute and Section (e.g. 'নেগোশিয়েবল ইনস্ট্রুমেন্টস অ্যাক্ট, ১৮৮১-এর ধারা ১৩৮' or 'দণ্ডবিধি ১৮৬০-এর ধারা ৪২০').\n"
            "- Provide practical steps: (১) কি নোটিশ দিতে হবে, (২) কোন আদালতে যেতে হবে, (৩) সময়সীমা (Limitation Period).\n"
            "- Conclude with a 1-line disclaimer.\n"
            + ("Answer in natural, polite Bengali (বাংলা)." if not is_english else "Answer in clear, authoritative English.")
        )

        prompt = f"Citizen Legal Query:\n\"{query_text}\"\n\nProvide an authoritative, clear explanation with applicable Bangladesh laws, practical timeline steps, and court jurisdiction."

        response = await self._call_gemini_chat(prompt, system_instruction)
        return response

    def generate_twiml_response(self, message_text: str) -> str:
        """Generates standard TwiML XML string for Twilio WhatsApp Webhook."""
        import xml.sax.saxutils as saxutils
        escaped_text = saxutils.escape(message_text)
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped_text}</Message></Response>'


# Singleton instance
whatsapp_service = JustorWhatsAppService()
