import os
import re
import logging
import asyncio
import json
import urllib.request
from typing import List, Optional, Dict, Any, cast

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from supabase import create_client, Client
import PyPDF2
from groq import Groq

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from groq import Groq

# ─── Environment Variables ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env.local"))

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="JustorAI RAG Brain",
    description="Custom RAG engine — Supabase pgvector + Groq Llama 3.1 8B Instant",
    version="4.0.0",
)

# Relaxed CORS for all frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Health / Keep-Alive ──────────────────────────────────────────────────────
@app.get("/ping")
async def ping():
    """Ultra-lightweight health check for heartbeat monitors."""
    return "ok"


# ─── Supabase ─────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
).strip()

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized.")
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")
else:
    logger.warning("Supabase credentials missing.")

# ─── Groq LLM ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("VITE_GROQ_API_KEY", "").strip()
groq_client: Optional[Groq] = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq client initialized.")
else:
    logger.warning("VITE_GROQ_API_KEY missing.")

# ─── Gemini (For Embeddings) ────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
gemini_ready: bool = False
if GEMINI_API_KEY:
    gemini_ready = True
    logger.info("Gemini API Key detected for embeddings.")
else:
    logger.warning("GEMINI_API_KEY missing.")

# ─── OpenRouter ─────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
openrouter_client = None
if OPENROUTER_API_KEY and OpenAI:
    openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
    logger.info("OpenRouter client initialized.")
else:
    logger.warning("OPENROUTER_API_KEY missing or 'openai' package not installed.")

# ─── Alibaba DashScope ──────────────────────────────────────────────────────
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()
dashscope_client = None
if DASHSCOPE_API_KEY and not DASHSCOPE_API_KEY.startswith("your_") and OpenAI:
    dashscope_client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=DASHSCOPE_API_KEY
    )
    logger.info("Alibaba DashScope client initialized.")
else:
    logger.warning("DASHSCOPE_API_KEY missing, is placeholder, or 'openai' package not installed.")

# ─── Pydantic Models ──────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    role: Optional[str] = "General Public"   # e.g. "Law Student", "Legal Professional"
    history: Optional[List[ChatMessage]] = []


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _embed(text: str) -> List[float]:
    """Generate a 768-dim embedding via Gemini native REST API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY missing.")
    # Strip null bytes — PostgreSQL cannot store \u0000
    clean_text = text.replace('\x00', '').replace('\u0000', '')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key={GEMINI_API_KEY}"
    payload = {
        "model": "models/gemini-embedding-2",
        "outputDimensionality": 768,
        "content": {
            "parts": [{"text": clean_text}]
        }
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as response:
        resp_data = json.loads(response.read().decode("utf-8"))
        return resp_data["embedding"]["values"]


def _call_gemini_native(messages, temperature=0.1) -> str:
    """Helper to query Gemini 2.5 Flash directly via native Google REST API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY missing.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    system_instruction = None
    for msg in messages:
        if msg["role"] == "system":
            system_instruction = {"parts": [{"text": msg["content"]}]}
        else:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2000
        }
    }
    if system_instruction:
        payload["systemInstruction"] = system_instruction

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        resp_data = json.loads(response.read().decode("utf-8"))
        return resp_data["candidates"][0]["content"]["parts"][0]["text"]


def prompt_general_public(context: str) -> str:
    return f"""You are Justor AI — a legal information assistant for Bangladesh.
Your only job is to help ordinary Bangladeshi citizens understand 
their legal rights in plain, simple language.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO HALLUCINATION RULES — READ BEFORE ANYTHING ELSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 1: You may ONLY state legal facts that exist in 
        VERIFIED SOURCES below. Nothing else. Ever.

RULE 2: Every single legal claim MUST have a citation.
        Format: [ACT-1], [ACT-2], [DLR-1] etc.
        No citation = you cannot make that claim.

RULE 3: If the user asks about ANY section, law, or 
        provision NOT present in VERIFIED SOURCES, 
        respond with this exact sentence:
        "This is not in my verified database. I cannot 
        confirm this. Please consult the Bangladesh Code 
        directly or a licensed lawyer."

RULE 4: Your training memory about Indian law is 
        PERMANENTLY BANNED. This includes:
        - Indian Penal Code (IPC)
        - Indian CrPC
        - Indian CPC
        - Indian Supreme Court judgments
        - Any law from India, Pakistan, or any country 
          other than Bangladesh
        Never use any of it. Not even as a reference.

RULE 5: If VERIFIED SOURCES is empty or says 
        "NO VERIFIED SOURCES FOUND", respond with:
        "I don't have verified information on this topic 
        yet. Please consult the Bangladesh Code or a 
        licensed lawyer."

RULE 6: If a section is marked OMITTED — tell the user 
        clearly: this section does not exist in Bangladesh 
        law. Tell them what replaced it if that information 
        is in VERIFIED SOURCES.

RULE 7: If a section is marked REPEALED — tell the user 
        clearly: this law no longer applies.

RULE 8: Never invent, estimate, or guess:
        - Section numbers
        - Penalty amounts
        - Time periods
        - Fine amounts
        - Any number at all
        If it is not in VERIFIED SOURCES, you cannot say it.

RULE 9: Never say "typically", "generally", "usually", 
        or "in most cases" about specific legal provisions.
        Either the law says it or it does not.

RULE 10: Never predict outcomes. Never say someone will 
         win or lose. Never give strategic legal advice.

RULE 11: CITATION INTEGRITY: Never write an [ACT-N] or [DLR-N] tag that does not appear
         in VERIFIED SOURCES above. State every section number exactly as it appears in
         VERIFIED SOURCES — never copy a section number from the user's question.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFIED SOURCES — USE ONLY THESE. NOTHING ELSE:
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT — follow this structure exactly:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**What This Means For You**
[2-3 sentences maximum. Plain English or plain Bangla.
 No legal jargon. Explain what happened and why it matters
 to this person right now.]

**What the Law Says**
[Start with: "Under Section X [ACT-1] of the [Act Name]..."
 Then explain what the law actually says in simple words.
 Do NOT copy-paste the raw legal text — translate it into 
 language a non-lawyer understands.
 If DLR case law is available, add:
 "A court also ruled in [Case Name] [DLR-1] that..."]

**What You Should Do Now**
[Numbered steps. Practical. Specific to Bangladesh.]
1. 
2. 
3. 

**Evidence to Keep**
[Bullet list of documents or evidence this person needs.]
- 
- 

**Where to Go / Who to Contact**
[Name the specific authority, court type, or helpline.
 Be specific — "Magistrate Court" not just "court".
 Include helpline numbers if relevant:
 Legal Aid: 16430 | Police: 999 | Women's Helpline: 109]

**When You Need a Lawyer**
[One sentence only. When does this become serious enough
 that professional legal help is essential.]

---
⚠️ *This is legal information, not legal advice. 
Justor AI is not a lawyer. Verify with a licensed 
Bangladeshi lawyer before taking any legal action.*"""

def prompt_law_student(context: str) -> str:
    return f"""You are Justor AI — a legal education assistant for Bangladesh.
Your job is to help law students understand Bangladeshi law 
through clear explanation, legal doctrine, and real examples.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO HALLUCINATION RULES — READ BEFORE ANYTHING ELSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 1: You may ONLY use legal information from 
        VERIFIED SOURCES below. Nothing else. Ever.

RULE 2: Every legal claim MUST cite its source.
        Format: [ACT-1], [ACT-2], [DLR-1] etc.
        No citation = you cannot make that claim.

RULE 3: If a section is NOT in VERIFIED SOURCES, say:
        "This is not in my verified database. Check the 
        official Bangladesh Code for this provision."

RULE 4: Your training memory about Indian law is 
        PERMANENTLY BANNED. This includes:
        - Indian Penal Code (IPC)
        - Indian CrPC and Indian CPC
        - Indian Supreme Court judgments
        - Any non-Bangladeshi legal source
        Never use it. Not even for comparison unless the 
        user explicitly asks you to compare, AND you clearly 
        label it as Indian law, NOT Bangladeshi law.

RULE 5: If a section is OMITTED from Bangladesh law —
        explain clearly that it does not exist here,
        why it was omitted, when, and what replaced it.
        This is important legal knowledge for students.

RULE 6: If a section is AMENDED — explain the current 
        text AND what was changed, using Amendment_Notes 
        from VERIFIED SOURCES only.

RULE 7: For DLR case law, cite the full citation:
        "In [Case Name] [DLR-1] ([Court], [Year]), 
        the court held that..."
        Never invent case citations.

RULE 8: Never invent doctrines, section numbers, case 
        names, or legal principles not in VERIFIED SOURCES.

RULE 9: If VERIFIED SOURCES is empty, say:
        "I don't have verified database entries on this 
        topic yet. Please check the Bangladesh Code directly."

RULE 10: CITATION INTEGRITY: Never write an [ACT-N] or [DLR-N] tag that does not appear
         in VERIFIED SOURCES above. State every section number exactly as it appears in
         VERIFIED SOURCES — never copy a section number from the user's question.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFIED SOURCES — USE ONLY THESE. NOTHING ELSE:
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT — follow this structure exactly:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**The Legal Issue**
[State the precise legal question this response answers.
 One or two sentences. Clear and specific.]

**Applicable Law**
[Quote the section:
 "Section X [ACT-1] of the [Act Name] provides:
 '[exact text from VERIFIED SOURCES]'"
 
 Then explain what it means in plain English.
 If multiple sections apply, cite each one separately.]

**The Legal Doctrine / Principle**
[Name and explain any doctrine involved.
 Examples: Doctrine of Representation, Res Judicata,
 Nemo dat quod non habet, Caveat Emptor etc.
 If no named doctrine applies, explain the underlying 
 legal principle in your own words.
 If none applies, omit this section entirely.]

**Real-Life Example (Bangladesh Context)**
[Create a concrete, realistic Bangladesh scenario showing 
 exactly how this law operates in practice.
 Use Bangladeshi names, places, and contexts.
 Show both what the law protects and what it does not.]

**Case Law Reference**
[If DLR sources are in VERIFIED SOURCES:
 "In [Case Name] [DLR-1] ([Court Division], [Year]), 
 the court held: '[ratio decidendi from source]'"
 
 If no DLR in VERIFIED SOURCES, write exactly:
 "No case law is currently in my verified database 
 on this specific point."]

**Key Points to Remember**
[3-5 bullet points for exam and courtroom relevance.
 Focus on what is distinctive about Bangladesh law
 compared to what students might assume from general 
 legal principles.]
- 
- 
- 

---
⚠️ *Verify all provisions against the official Bangladesh 
Code before relying on this in academic or professional work. 
Justor AI is a study tool, not a substitute for primary sources.*"""

def prompt_lawyer(context: str) -> str:
    return f"""You are Justor AI — a legal research assistant for Bangladesh.
You produce IRAC-structured legal analysis for practicing lawyers,
advocates, and legal professionals. Every claim must be grounded 
in verified Bangladeshi law only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO HALLUCINATION RULES — READ BEFORE ANYTHING ELSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 1: You may ONLY use legal authority from 
        VERIFIED SOURCES below. Nothing else. Ever.

RULE 2: Every legal proposition MUST cite its source.
        Format: [ACT-1], [ACT-2], [DLR-1] etc.
        If you cannot cite a source, you cannot state 
        the proposition. State the gap instead.

RULE 3: If a section is NOT in VERIFIED SOURCES, write:
        "Section [X] is not in my verified database.
        Independent verification against the official 
        Bangladesh Code is required before reliance."

RULE 4: Your training memory about Indian law is 
        PERMANENTLY BANNED as Bangladeshi authority.
        This includes:
        - Indian Penal Code (IPC) cited as Bangladeshi law
        - Indian CrPC provisions cited as Bangladeshi law
        - Indian CPC provisions cited as Bangladeshi law
        - Indian Supreme Court as binding authority
        - Any Indian, Pakistani, or foreign statute cited 
          as Bangladeshi law
        You may only reference foreign law if the user 
        explicitly asks for comparative analysis, AND you 
        clearly label it as foreign law throughout.

RULE 5: Distinguish clearly between:
        - Statutory authority: Acts and Ordinances
        - Case law authority: DLR judgments
        - Persuasive authority: foreign decisions (label clearly)
        Never blend these without distinction.

RULE 6: For OMITTED sections (like CrPC Section 438,
        CPC Sections 100-103):
        State clearly in RULE section that this provision 
        was omitted, when, by which law, and what replaced it.
        Do not apply an omitted section as if it exists.

RULE 7: For DLR citations, use the full citation format:
        "[Case Name] [DLR-1] ([Court Division], [Year])"
        Example: "Karim vs State [DLR-1] (Appellate Division, 2005)"
        Never abbreviate or invent citations.

RULE 8: Acknowledge database gaps explicitly in APPLICATION:
        "My database does not currently contain [X].
        Independent verification is recommended before 
        reliance in proceedings."
        This is professional and honest, not a weakness.

RULE 9: Never predict outcomes with certainty.
        Use: "the balance of authority suggests..."
        or "on the present facts, the stronger argument is..."
        Never: "you will win" or "the court will decide..."

RULE 10: If VERIFIED SOURCES is empty, write:
         "VERIFIED SOURCES returned no results for this query.
         This analysis cannot proceed without verified 
         Bangladeshi legal authority. Please consult the 
         official Bangladesh Code and relevant DLR volumes."

RULE 11: CITATION INTEGRITY: Never write an [ACT-N] or [DLR-N] tag that does not appear
         in VERIFIED SOURCES above. State every section number exactly as it appears in
         VERIFIED SOURCES — never copy a section number from the user's question.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFIED SOURCES — USE ONLY THESE. NOTHING ELSE:
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT — IRAC — follow this structure exactly:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ISSUE**
[State the precise legal question(s) to be resolved.
 Identify: the legal relationship, the right or duty in 
 dispute, the jurisdictional context, and what legal 
 determination must be made.
 No argument here. No conclusion here. Only the question.]

**RULE**
[State ALL governing legal authority from VERIFIED SOURCES.
 
 For each statute:
 "Section X [ACT-N] of [Full Act Name] provides:
 '[exact statutory text from VERIFIED SOURCES]'"
 
 For each case:
 "In [Case Name] [DLR-N] ([Court Division], [Year]),
 the court held: '[ratio decidendi from VERIFIED SOURCES]'"
 
 List every applicable section and case separately.
 Do NOT apply law to facts here — only state the rules.
 If a relevant provision is not in your database, state:
 "The applicable provision [description] is not in my 
 verified database. Independent verification required."]

**APPLICATION**
[Apply rules to facts. This is the analytical core.
 STRICT APPLICATION RULE: Reason ONLY from rules quoted in RULE above. Do not
 introduce any doctrine, principle, or statutory language not quoted there —
 even from the same Act, even if you believe it applies. If you reach for
 anything not in RULE, stop and write: "[X] may be relevant but is not in my
 verified sources; independent verification required." Do not mix language from
 different sections unless both are quoted in RULE.

 Address each of the following:
 
 — Statutory analysis: which elements of each cited 
   section are satisfied on the present facts and which 
   are not, and why
 — Case law analysis: how the ratio of each cited case 
   applies or is distinguished on the present facts
 — Procedural requirements: what procedural steps apply
 — Evidentiary requirements: what evidence is required
 — Counter-arguments: what the opposing party will argue 
   and how strong that argument is
 — Uncertainty: where the law is unsettled or your 
   database has gaps, acknowledge this explicitly
 
 Every analytical point must trace back to a cited source.
 No analytical point can rest on uncited assertion.]

**CONCLUSION**
[State the likely legal outcome from the analysis above.
 Include:
 - The probable legal position on the current facts
 - Conditions or qualifications on this conclusion
 - What additional facts or authorities would change it
 Do NOT introduce new arguments or new authorities here.
 The conclusion must follow from the Application section.]

**REFERENCES**

*Statutory Law:*
[List every ACT-N cited in this analysis:]
[ACT-N] [Full Act Name] | Section [Number]: [Section Title] | Status: [Active/Amended/Repealed/Omitted] | [Source Reference]

*Case Law:*
[List every DLR-N cited in this analysis:]
[DLR-N] [Case Title] | [DLR Citation] | [Court Division] | [Year]

---
⚠️ *This analysis is based on Justor AI's verified database 
as of the date of this query. The database covers 33 Acts and 
selected DLR volumes. Independent verification against the 
complete official Bangladesh Code and all relevant DLR volumes 
is required before reliance in court proceedings or formal 
legal advice.*"""

# Add a line ONLY for acts confirmed present in STEP 0b.
ACT_NAME_MAP = {
    r'nat act|non.?agricultural tenancy act': 'The Non-Agricultural Tenancy Act, 1949',
    r'land reforms act|bhumi sanskar|land reform 2023': 'The Land Reforms Act, 2023',
    r'\bsat act\b|state acquisition.*tenancy|sat 1950': 'The State Acquisition and Tenancy Act, 1950',
    r'transfer of property act|\btpa\b': 'The Transfer of Property Act, 1882',
    r'trademarks? act|trademark 2009': 'The Trademarks Act, 2009',
}

def classify_query(query: str) -> dict:
    section_pattern = (
        r"(?:section|sec\.?|dhara|\u09a7\u09be\u09b0\u09be|article|\u0985\u09a8\u09c1\u099a\u09cd\u099b\u09c7\u09a6|rule)"
        r"\s*(\d+[A-Za-z]?)"
    )
    sections = re.findall(section_pattern, query, re.IGNORECASE)

    detected_act = None
    for pattern, act_name in ACT_NAME_MAP.items():
        if re.search(pattern, query, re.IGNORECASE):
            detected_act = act_name
            break

    return {
        "is_dlr_request": any(k in query.lower() for k in
            ["dlr", "case law", "judgment", "\u09a8\u099c\u09c0\u09b0", "precedent", "court held"]),
        "is_repealed_request": any(k in query.lower() for k in
            ["repealed", "\u09ac\u09be\u09a4\u09bf\u09b2", "omitted", "old law", "previously", "was it ever"]),
        "sections": sections,
        "primary_section": sections[0] if sections else None,
        "detected_act": detected_act,
    }

def _act_matches(chunk_act: str, detected: str) -> bool:
    a, b = (chunk_act or "").lower(), (detected or "").lower()
    return bool(a) and bool(b) and (a in b or b in a)

async def retrieve_context(query_vec: list, intent: dict):
    db = cast(Client, supabase)

    acts_search = db.rpc("match_acts_v2", {
        "query_embedding": query_vec,
        "match_count": 8,                       # over-fetch; trimmed below
        "match_threshold": 0.40,
        "query_section": intent.get("primary_section"),
        "prefer_dead_law": intent.get("is_repealed_request", False),
        "prefer_amended": False,
        "filter_act_name": intent.get("detected_act"),
    }).execute()
    acts = acts_search.data or []

    # Cross-act post-filter: if a specific act was named AND we found chunks
    # from it, keep ONLY those. If none matched, leave as-is (validate_retrieval
    # will refuse, which is correct). This avoids false refusals on misdetection.
    detected = intent.get("detected_act")
    if detected:
        same = [a for a in acts if _act_matches(a.get("act_name", ""), detected)]
        acts = (same or acts)[:6]
    else:
        acts = acts[:6]

    dlrs_search = db.rpc("match_dlrs_v2", {
        "query_embedding": query_vec,
        "match_count": 2,
        "match_threshold": 0.40,
    }).execute()

    return acts, dlrs_search.data or []

def validate_retrieval(intent: dict, acts: list, dlrs: list):
    """Returns (is_valid, status_code)."""
    if not acts and not dlrs:
        return False, "no_results"
    if intent.get("detected_act") and acts:
        if not any(_act_matches(a.get("act_name", ""), intent["detected_act"]) for a in acts):
            return False, "wrong_act_retrieved"
    if intent.get("primary_section") and acts:
        secs = [str(a.get("section_number", "")).lower() for a in acts]
        if str(intent["primary_section"]).lower() not in secs:
            return True, "section_not_exact"   # soft: section may be inside related chunk
    return True, "ok"

def clean_act_name(raw: str) -> str:
    cleaned = re.sub(r'\s*\([^)]*\)', '', raw or '').strip().rstrip('.,;:').strip()
    return cleaned or (raw or 'Unknown Act')

def format_retrieved_context(acts: list, dlrs: list):
    """Returns (context_block, sources_list)."""
    if not acts and not dlrs:
        return "NO_VERIFIED_SOURCES_FOUND", []

    sources = []
    block = "=== STATUTORY LAW (ACTS) ===\n"
    if not acts:
        block += "No matching Acts found for this query.\n"
    for i, act in enumerate(acts):
        sid = f"ACT-{i+1}"
        name = clean_act_name(act.get('act_name', ''))
        num, title = act.get('section_number', ''), act.get('section_title', '')
        status = act.get('status') or 'Active'
        sl = status.lower()
        if sl == 'omitted':
            tag = " ⚠️ [STATUS: OMITTED — NO LONGER EXISTS IN BANGLADESH LAW]"
        elif sl == 'repealed':
            tag = " ⚠️ [STATUS: REPEALED — NO LONGER IN FORCE]"
        elif sl == 'amended':
            tag = " [STATUS: AMENDED — current law; see amendment notes]"
        elif sl == 'active':
            tag = ""
        else:
            tag = f" [STATUS: {status.upper()}]"
        block += f"[{sid}] {name} — Section {num}: {title}{tag}\n"
        block += f"Content: {act.get('content','')}\n"
        if act.get('repealed_clauses'):
            block += f"Omission/Repeal Authority: {act['repealed_clauses']}\n"
        if act.get('amendment_notes'):
            block += f"Amendment Notes: {act['amendment_notes']}\n"
        block += "---\n"
        sources.append({"id": sid, "type": "statute", "act": name,
                        "section": num, "title": title, "status": status})

    block += "\n=== CASE LAW (DLR) ===\n"
    if not dlrs:
        block += "No matching Case Law found for this query.\n"
    for i, dlr in enumerate(dlrs):
        sid = f"DLR-{i+1}"
        title = dlr.get('case_title', 'Unknown Case')
        year, court = dlr.get('year', ''), dlr.get('court_division', '')
        cite = dlr.get('dlr_citation') or \
            f"{dlr.get('dlr_volume','')} DLR ({dlr.get('dlr_series','AD')}) {year}".strip()
        block += (f"[{sid}] Case: {title} ({year})\nCitation: {cite}\nCourt: {court}\n"
                  f"Subject: {dlr.get('subject_law','')}\n"
                  f"Ratio Decidendi: {dlr.get('ratio_decidendi','')}\n"
                  f"Reference Context: {(dlr.get('judgment_content','') or '')[:300]}...\n---\n")
        sources.append({"id": sid, "type": "case_law", "case": title,
                        "court": court, "year": year, "citation": cite})

    return block, sources

def build_citation_footer(answer: str, sources: list) -> str:
    if "REFERENCES" in answer or not sources:   # lawyer IRAC builds its own
        return answer
    used = {u.strip('[]') for u in re.findall(r'\[(?:ACT|DLR)-\d+\]', answer)}
    cited = [s for s in sources if s['id'] in used] or sources
    lines = ["\n\n---\n**Sources**"]
    for s in cited:
        if s['type'] == 'statute':
            lines.append(f"- **[{s['id']}]** {s['act']}, Section {s['section']}: "
                         f"{s['title']} *(Status: {s['status']})*")
        else:
            lines.append(f"- **[{s['id']}]** {s['case']} — {s.get('citation','')} "
                         f"| {s.get('court','')} | {s.get('year','')}")
    return answer + "\n".join(lines)

def log_query(**row):
    try:
        row["query"] = (row.get("query") or "")[:500]
        row["response_preview"] = (row.get("response_preview") or "")[:300]
        cast(Client, supabase).table("pilot_query_log").insert(row).execute()
    except Exception as e:
        logger.warning(f"pilot log failed (non-critical): {e}")

def get_system_prompt(role: str, context: str) -> str:
    if context == "NO_VERIFIED_SOURCES_FOUND":
        return ("You are Justor AI. The verified database returned no results. "
                "Reply with EXACTLY: \"I don't have verified information on this "
                "in my database yet. Please consult the Bangladesh Code at "
                "bdlaws.minlaw.gov.bd or a licensed lawyer.\" Do not use training memory.")
    if role == "Legal Professional": return prompt_lawyer(context)
    if role == "Law Student":        return prompt_law_student(context)
    return prompt_general_public(context)


SMALL_MODELS = {"llama-3.1-8b-instant"}

FALLBACK_PROMPT = """You are Justor AI, a Bangladesh legal information assistant.
Answer ONLY from VERIFIED SOURCES below. Never use training memory.
Tag every legal claim with its source: [ACT-1], [ACT-2], [DLR-1].
Never write a tag that is not in the sources. Use section numbers exactly as
they appear in the sources, never from the question.
If VERIFIED SOURCES is empty: reply exactly "Not in my verified database.
Please consult the Bangladesh Code or a licensed lawyer." and nothing else.
Never cite Indian law. If a source is Omitted/Repealed, say it is not current law.

VERIFIED SOURCES:
{context}

End with: "⚠️ Verify with a licensed Bangladeshi lawyer before acting."
"""

def _extract_context(messages: list) -> str:
    sys = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
    i = sys.find("VERIFIED SOURCES")
    return sys[i:] if i != -1 else "No verified sources."

def compress_for_small_model(messages: list) -> list:
    ctx = _extract_context(messages)
    return [{"role": "system", "content": FALLBACK_PROMPT.format(context=ctx)}] + messages[1:]

# Provider strings match your code: "alibaba", "gemini", "groq".
# Lawyer chain intentionally ends at the 70B — never route IRAC to the 8B.
MODEL_CHAINS = {
    "Legal Professional": [("alibaba","qwen-max"), ("gemini","gemini-2.5-flash"),
                           ("groq","llama-3.3-70b-versatile")],
    "Law Student":        [("alibaba","qwen-plus"), ("gemini","gemini-2.5-flash"),
                           ("groq","llama-3.3-70b-versatile"), ("groq","llama-3.1-8b-instant")],
    "General Public":     [("gemini","gemini-2.5-flash"), ("alibaba","qwen-plus"),
                           ("groq","llama-3.3-70b-versatile"), ("groq","llama-3.1-8b-instant")],
}

def call_llm_with_fallbacks(models: list, messages) -> tuple:
    """Returns (text, 'provider/model'). Compresses the prompt for small models."""
    for provider, model in models:
        try:
            payload = compress_for_small_model(messages) if model in SMALL_MODELS else messages
            if provider == "alibaba" and dashscope_client:
                c = dashscope_client.chat.completions.create(
                    model=model, messages=payload, temperature=0.1, max_tokens=2000)
                return c.choices[0].message.content, f"{provider}/{model}"
            elif provider == "gemini" and GEMINI_API_KEY:
                return _call_gemini_native(payload, temperature=0.1), f"{provider}/{model}"
            elif provider == "groq" and groq_client:
                c = groq_client.chat.completions.create(
                    model=model, messages=payload, temperature=0.1, max_tokens=2000)
                return c.choices[0].message.content, f"{provider}/{model}"
            elif provider == "openrouter" and openrouter_client:
                c = openrouter_client.chat.completions.create(
                    model=model, messages=payload, temperature=0.1, max_tokens=2000)
                return c.choices[0].message.content, f"{provider}/{model}"
        except Exception as e:
            logger.warning(f"[LLM] {provider}/{model} failed: {e}")
            continue
    raise HTTPException(status_code=503, detail="AI service busy. Please try again in a moment.")


def extract_pdf_text(file_obj) -> str:
    """Extract plain text from all pages of a PDF file object."""
    reader = PyPDF2.PdfReader(file_obj)
    pages: List[str] = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            pages.append(txt)
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Naive recursive chunker.
    """
    # Normalise whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        break_at = text.rfind("\n\n", start, end)
        if break_at == -1 or break_at <= start:
            break_at = text.rfind(". ", start, end)
        if break_at == -1 or break_at <= start:
            break_at = text.rfind(" ", start, end)
        if break_at == -1 or break_at <= start:
            break_at = end  # hard cut

        chunk = text[int(start):int(break_at)].strip()
        if chunk:
            chunks.append(chunk)
        start = max(break_at - overlap, start + 1)

    return chunks

# Job status store (in-memory — resets on server restart)
_jobs: Dict[str, Dict[str, Any]] = {}

import uuid


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok"}


@app.get("/health", tags=["Health"])
async def health():
    return {
        "supabase_ready": supabase is not None,
        "groq_ready": groq_client is not None,
        "openrouter_ready": openrouter_client is not None,
        "gemini_embeddings_ready": gemini_ready,
    }


def _process_pdf_background(job_id: str, title: str, filename: str, raw_bytes: bytes):
    """Run in background thread — embed all chunks and store in Supabase."""
    import io
    _jobs[job_id] = {"status": "processing", "title": title, "chunks_done": 0, "total_chunks": 0}

    try:
        db = cast(Client, supabase)

        # Extract text from bytes
        raw_text = extract_pdf_text(io.BytesIO(raw_bytes))
        if not raw_text.strip():
            _jobs[job_id] = {"status": "error", "error": "No text extracted from PDF"}
            return

        # Insert document metadata
        preview = raw_text[:500]
        doc_resp = db.table("documents").insert({
            "title": title,
            "content": preview,
            "metadata": {"filename": filename},
        }).execute()
        document_id = doc_resp.data[0]["id"]

        # Chunk
        chunks = chunk_text(raw_text, chunk_size=800, overlap=150)
        _jobs[job_id]["total_chunks"] = len(chunks)
        logger.info(f"[job {job_id}] '{title}' -> {len(chunks)} chunks, embedding...")

        # Embed + batch insert
        records = []
        for i, chunk in enumerate(chunks):
            vec = _embed(chunk)
            records.append({
                "document_id": document_id,
                "content": chunk,
                "embedding": vec,
                "chunk_index": i,
                "metadata": {"source": filename, "chunk": i},
            })
            _jobs[job_id]["chunks_done"] = i + 1
            if len(records) >= 50:
                db.table("document_chunks").insert(records).execute()
                records = []

        if records:
            db.table("document_chunks").insert(records).execute()

        _jobs[job_id] = {
            "status": "done",
            "title": title,
            "document_id": document_id,
            "total_chunks": len(chunks),
        }
        logger.info(f"[job {job_id}] Done — {len(chunks)} chunks stored.")

    except Exception as e:
        logger.error(f"[job {job_id}] Error: {e}")
        _jobs[job_id] = {"status": "error", "error": str(e)}


@app.post("/upload", tags=["Knowledge Base"])
async def upload_document(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a legal PDF. Returns immediately with a job_id.
    Poll GET /upload/status/{job_id} to track progress.
    """
    if supabase is None:
        raise HTTPException(503, "Supabase not available.")
    if openrouter_client is None:
        raise HTTPException(503, "OpenRouter client not loaded.")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    # Read file bytes NOW (before background task, file object closes after response)
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(422, "Empty file uploaded.")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "title": title}

    background_tasks.add_task(
        _process_pdf_background, job_id, title, file.filename, raw_bytes
    )

    return JSONResponse(202, content={
        "message": f"'{title}' accepted — processing in background.",
        "job_id": job_id,
        "poll_url": f"/upload/status/{job_id}",
    })


@app.get("/upload/status/{job_id}", tags=["Knowledge Base"])
async def upload_status(job_id: str):
    """Poll the status of a background PDF upload job."""
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"Job {job_id} not found.")
    return job



@app.post("/chat", tags=["Chat"])
async def chat(request: ChatRequest):
    """
    User question → embed → retrieve context from Supabase →
    build prompt → generate answer with LLM routing chains and fallbacks.
    """
    if supabase is None:
        raise HTTPException(503, "Supabase database client is not ready.")

    try:
        intent = classify_query(request.message)
        query_vec = _embed(request.message)
        acts, dlrs = await retrieve_context(query_vec, intent)
        ok, status = validate_retrieval(intent, acts, dlrs)

        if not ok:
            msg = {
                "no_results": ("I don't have verified information on this specific topic "
                               "in my database yet. Please consult the Bangladesh Code at "
                               "bdlaws.minlaw.gov.bd or call Legal Aid at 16430."),
                "wrong_act_retrieved": ("I could not locate the specific Act you asked about "
                               "in my verified database. Please consult the Bangladesh Code "
                               "or a licensed lawyer for this question."),
            }.get(status, "Not found in verified database.")
            log_query(user_id=request.user_id, persona=request.role, query=request.message,
                      act_detected=intent.get("detected_act"),
                      section_detected=intent.get("primary_section"),
                      sources_found=0, retrieval_status=status,
                      model_used="none-refused", response_preview=msg)
            return JSONResponse(content={
                "response": msg, "sources_used": 0, "sources": [], "retrieval_status": status,
                "metadata": {"detected_act": intent.get("detected_act"),
                             "sections_found": intent["sections"]}})

        context, sources = format_retrieved_context(acts, dlrs)
        messages = [{"role": "system", "content": get_system_prompt(request.role, context)}]
        messages += [{"role": m.role, "content": m.content} for m in (request.history or [])[-6:]]
        messages.append({"role": "user", "content": request.message})

        models = MODEL_CHAINS.get(request.role, MODEL_CHAINS["General Public"])
        answer, model_used = call_llm_with_fallbacks(models, messages)
        final = answer if request.role == "Legal Professional" else build_citation_footer(answer, sources)

        log_query(user_id=request.user_id, persona=request.role, query=request.message,
                  act_detected=intent.get("detected_act"),
                  section_detected=intent.get("primary_section"),
                  sources_found=len(acts) + len(dlrs), retrieval_status=status,
                  model_used=model_used, response_preview=final)

        return JSONResponse(content={
            "response": final, "sources_used": len(acts) + len(dlrs), "sources": sources,
            "retrieval_status": status, "model_used": model_used,
            "metadata": {"detected_act": intent.get("detected_act"),
                         "sections_found": intent["sections"],
                         "section_detected": intent.get("primary_section"),
                         "is_dlr": intent["is_dlr_request"]}})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, str(e))


@app.get("/documents", tags=["Knowledge Base"])
async def list_documents():
    """List all documents in the knowledge base."""
    if supabase is None:
        raise HTTPException(503, "Supabase not available.")
    db = cast(Client, supabase)
    try:
        resp = (
            db.table("documents")
            .select("id, title, created_at")
            .order("created_at", desc=True)
            .execute()
        )
        return {"documents": resp.data}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.delete("/documents/{document_id}", tags=["Knowledge Base"])
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks (cascading delete via FK constraint).
    """
    if supabase is None:
        raise HTTPException(503, "Supabase not available.")
    db = cast(Client, supabase)
    try:
        db.table("documents").delete().eq("id", document_id).execute()
        return {"message": f"Document {document_id} deleted."}
    except Exception as e:
        raise HTTPException(500, str(e))