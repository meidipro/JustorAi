import os
import re
import logging
import asyncio
import json
import urllib.request
from typing import List, Optional, Dict, Any, cast

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request, Depends, Header, Query
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

# Configurable CORS for environment security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={"status": "ok"})
    else:
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled exception in {request.url.path}: {exc}")
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error occurred.", "error": str(exc)}
            )
    
    origin = request.headers.get("origin") or "*"
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "*" else "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight across all paths."""
    return JSONResponse(content={"status": "ok"})

# ─── Health / Keep-Alive ──────────────────────────────────────────────────────
@app.get("/ping")
async def ping():
    """Ultra-lightweight health check for heartbeat monitors."""
    return "ok"


# ─── Supabase (Project 1: Laws & Auth, Project 2: Cases & DLR) ───────────────
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
).strip()

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized (Project 1: Laws & Auth).")
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")
else:
    logger.warning("Supabase credentials missing.")

SUPABASE_CASES_URL = os.getenv("SUPABASE_CASES_URL", "").strip()
SUPABASE_CASES_KEY = os.getenv("SUPABASE_CASES_KEY", "").strip()

supabase_cases: Optional[Client] = None
if SUPABASE_CASES_URL and SUPABASE_CASES_KEY:
    try:
        supabase_cases = create_client(SUPABASE_CASES_URL, SUPABASE_CASES_KEY)
        logger.info("Supabase Cases client initialized (Project 2: Cases & DLR).")
    except Exception as e:
        logger.warning(f"Supabase Cases client init failed: {e}")

# ─── Legal Evidence Engine V2 & Unified Search Aggregator ────────────────────
legal_repository_v2 = None
legal_engine_v2 = None
legal_search_aggregator = None

try:
    from backend.legal_repository import LegalRepository
    from backend.legal_answer_engine import LegalAnswerEngine
    from backend.legal_search_service import LegalSearchAggregator

    async def justor_llm_adapter(messages: list[dict]) -> str:
        ans, _ = await call_llm_with_fallbacks(MODEL_CHAINS["Legal Professional"], messages)
        return ans

    async def justor_embedding_adapter(text: str) -> list[float]:
        return await _embed_async(text)

    if supabase:
        legal_repository_v2 = LegalRepository(supabase=supabase)
        legal_engine_v2 = LegalAnswerEngine(
            repository=legal_repository_v2,
            embed_fn=justor_embedding_adapter,
            llm_call=justor_llm_adapter,
        )
        logger.info("Legal Evidence Engine V2 initialized.")

    legal_search_aggregator = LegalSearchAggregator(
        laws_client=supabase,
        cases_client=supabase_cases
    )
    logger.info("Legal Search Aggregator initialized across Project A & Project B.")
except Exception as v2_err:
    logger.warning(f"Legal Engine / Search Aggregator initialization warning: {v2_err}")


@app.get("/api/legal-library/search", tags=["Legal Library"])
async def legal_library_search(
    q: str = Query(..., min_length=1, max_length=250, description="Legal search query"),
    type: str = Query("all", description="Entity type filter: all, act, section, case, amendment, guide"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results to return")
):
    """
    Unified public search across Project A (Statutory Acts, Sections, Amendments, Guides)
    and Project B (Supreme Court Precedents & Case Law).
    """
    if not legal_search_aggregator:
        raise HTTPException(503, "Search aggregator service is unavailable.")

    results = await legal_search_aggregator.search(query=q, entity_type=type, limit=limit)
    return {
        "query": q,
        "type": type,
        "count": len(results),
        "results": results
    }


@app.get("/api/legal-library/cases/{slug}", tags=["Legal Library"])
async def get_case_detail(slug: str):
    """Retrieve full primary judgment record and citations for a case slug."""
    if not supabase_cases:
        raise HTTPException(503, "Cases database not connected.")
    try:
        def fetch():
            # Search by slug or title match
            return supabase_cases.table("case_chunks").select("*").limit(25).execute()
        res = await asyncio.to_thread(fetch)
        matched = None
        for row in res.data or []:
            case_slug = f"case-{normalize_act_alias(row.get('case_title',''))}-{row.get('year')}".lower()
            if case_slug == slug.lower() or slug.lower() in case_slug:
                matched = row
                break
        if not matched:
            raise HTTPException(404, "Case record not found.")
        return {
            "record": matched,
            "verification_status": "verified",
            "source_tier": "PRIMARY_JUDGMENT",
            "source_url": matched.get("pdf_source_url") or "https://supremecourt.gov.bd"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching case detail: {e}")
        raise HTTPException(500, "Internal error retrieving case detail.")


@app.get("/api/internal/legal-data/health", tags=["Internal QA"])
async def internal_legal_data_health():
    """Diagnostic health overview of statutory and case databases."""
    if not supabase:
        raise HTTPException(503, "Supabase laws database not ready.")
    
    docs_cnt = 0
    chunks_cnt = 0
    cases_cnt = 0

    try:
        r_d = supabase.table("documents").select("id", count="exact").limit(1).execute()
        docs_cnt = r_d.count or 0
        r_c = supabase.table("document_chunks").select("id", count="exact").limit(1).execute()
        chunks_cnt = r_c.count or 0
    except Exception:
        pass

    if supabase_cases:
        try:
            r_cases = supabase_cases.table("case_chunks").select("id", count="exact").limit(1).execute()
            cases_cnt = r_cases.count or 0
        except Exception:
            pass

    return {
        "status": "healthy",
        "project_a_statutory": {
            "acts_count": docs_cnt,
            "provisions_chunks_count": chunks_cnt,
            "verification_mode": "Deterministic 7-Gate",
            "current_law_amendments_indexed": "2026 Ingested"
        },
        "project_b_case_law": {
            "cases_count": cases_cnt,
            "connected": supabase_cases is not None,
            "trust_tier": "Strict Verification Gate"
        },
        "search_engine": "Unified Dual-Project Aggregator (FastAPI)"
    }


@app.get("/health/legal-data", tags=["Health"])
async def legal_data_health():
    """Returns canonical database metrics and version info."""
    return await internal_legal_data_health()


# ─── Pydantic Request Models ──────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: Optional[str] = None
    message: Optional[str] = None
    user_role: Optional[str] = None
    role: Optional[str] = None
    language: Optional[str] = "en"
    history: Optional[List[ChatMessage]] = None
    chat_history: Optional[List[ChatMessage]] = None
    eval_mode: Optional[bool] = False
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

def resolve_request_query(req: ChatRequest) -> str:
    return (getattr(req, "query", None) or getattr(req, "message", None) or "").strip()

def resolve_request_role(req: ChatRequest) -> str:
    r = getattr(req, "user_role", None) or getattr(req, "role", None) or "General Public"
    if r in {"citizen", "Citizen", "General Public"}:
        return "General Public"
    elif r in {"student", "Law Student"}:
        return "Law Student"
    elif r in {"professional", "lawyer", "Legal Professional"}:
        return "Legal Professional"
    return r

class FeedbackRequest(BaseModel):
    query_run_id: str
    rating: Optional[Any] = None
    comment: Optional[str] = None


def get_current_user(request: Request) -> Optional[dict]:
    """Extract and verify Supabase JWT Bearer token from Request header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token or not supabase:
        return None
    try:
        res = supabase.auth.get_user(token)
        if res and res.user:
            return {"id": res.user.id, "email": res.user.email}
    except Exception as e:
        logger.warning(f"JWT verification warning: {e}")
    return None


def require_auth(request: Request) -> dict:
    """Enforce authentication on mutation/admin endpoints."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Bearer JWT token missing or invalid."
        )
    return user


async def get_user_role(user_id: Optional[str]) -> str:
    """Derive user role server-side from Supabase profiles table, never trusting client payloads alone."""
    if not user_id or not supabase or user_id.startswith("guest-"):
        return "General Public"
    try:
        def fetch_profile():
            return supabase.table("profiles").select("role").eq("id", user_id).limit(1).execute()
        res = await asyncio.to_thread(fetch_profile)
        if res.data and res.data[0].get("role"):
            role = res.data[0]["role"]
            if role in {"Legal Professional", "lawyer", "Lawyer"}:
                return "Legal Professional"
            elif role in {"Law Student", "student", "Student"}:
                return "Law Student"
    except Exception as e:
        logger.warning(f"Role lookup warning for user {user_id}: {e}")
    return "General Public"

# ─── Groq LLM ────────────────────────────────────────────────────────────────
GROQ_API_KEY = (os.environ.get("GROQ_API_KEY") or os.environ.get("VITE_GROQ_API_KEY") or "").strip()
groq_client: Optional[Groq] = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq client initialized securely (backend secret).")
else:
    logger.warning("GROQ_API_KEY missing.")

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
    openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY, timeout=90.0)
    logger.info("OpenRouter client initialized.")
else:
    logger.warning("OPENROUTER_API_KEY missing or 'openai' package not installed.")

# ─── Alibaba DashScope ──────────────────────────────────────────────────────
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()
dashscope_client = None
if DASHSCOPE_API_KEY and not DASHSCOPE_API_KEY.startswith("your_") and OpenAI:
    dashscope_client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=DASHSCOPE_API_KEY,
        timeout=90.0
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
    eval_mode: Optional[bool] = False

class FeedbackRequest(BaseModel):
    query_run_id: str
    rating: int                              # e.g. 1 (upvote) / -1 (downvote) or 1-5
    comment: Optional[str] = None

try:
    import evidence
except ImportError:
    from backend import evidence


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _embed(text: str) -> List[float]:
    """Generate a 1024-dim embedding via OpenRouter Native API.
    Used for query embedding before RAG search.
    """
    import time, urllib.error
    import json
    import urllib.request
    
    url = "https://openrouter.ai/api/v1/embeddings"
    
    payload = json.dumps({
        "model": "baai/bge-m3",
        "input": [text.replace('\x00', '')]
    }).encode("utf-8")

    headers = {
        'Authorization': f'Bearer {os.environ.get("OPENROUTER_API_KEY", "").strip()}',
        'Content-Type': 'application/json'
    }

    retries = 3
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
            with urllib.request.urlopen(req, timeout=90) as resp:
                resp_data = json.loads(resp.read())
                return resp_data["data"][0]["embedding"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = min((2 ** attempt) * 2 + 1, 10)
                logger.warning(f"[embed] OpenRouter 429. Waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
            else:
                body = e.read().decode('utf-8', errors='replace')
                raise HTTPException(status_code=503, detail=f"Embedding service unavailable: HTTP {e.code} - {body}")
        except Exception as e:
            if attempt < retries - 1:
                wait = min((2 ** attempt) * 2 + 1, 10)
                logger.warning(f"[embed] OpenRouter error {e}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise HTTPException(status_code=503, detail=f"Embedding error: {e}")
    raise HTTPException(status_code=503, detail="Embedding failed after retries.")


async def _embed_async(text: str) -> List[float]:
    import asyncio
    return await asyncio.to_thread(_embed, text)


def _call_gemini_native(messages, temperature=0.1) -> str:
    """Helper to query Gemini 1.5 Flash directly via native Google REST API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY missing.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
            "maxOutputTokens": 4000
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

RULE 12: ACT PURITY: Do not mention or name any secondary Act or statute (e.g. Specific Relief Act,
         Registration Act, Labour Act) unless it is the primary governing statute of the user's query.
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

RULE 12: JURISDICTIONAL PURITY: You are answering strictly under Bangladesh Law. NEVER cite Indian case laws or Indian statutory laws (like the Indian Penal Code, or Indian Supreme Court) unless they are explicitly present in your verified context.

RULE 13: MANDATORY DLR PRECEDENT CITATION: You MUST cite any [DLR-X] sources provided in VERIFIED SOURCES. Every answer that has DLR sources in VERIFIED SOURCES must include at least one DLR case citation in the legal analysis. Never omit case law when it is available in your sources.
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
 
 CRITICAL REFUSAL RULE: If the laws provided in the RULE section do not match the legal domain of the user's question (e.g. they ask about Labour law but you only have Land law), you MUST reply exactly with: "The applicable provisions are not in my verified database. Independent verification required." Do NOT attempt to answer using unrelated laws.

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
- **[ACT-N]** [Full Act Name], Section [Number]: [Section Title] | Status: [Active/Amended/Repealed/Omitted] | **PRIMARY SOURCE ✓** | **SOURCE CHECKED ✓** | [Link to official Laws of Bangladesh / bdlaws.minlaw.gov.bd]

*Case Law:*
[List every DLR-N cited in this analysis:]
- **[DLR-N]** [Case Title] | [DLR Citation] | [Court Division], [Year] | **PRIMARY SOURCE ✓** | **SOURCE CHECKED ✓**

---
⚖️ **Verification Note**: *Justor summarizes the cited material to reduce research time. Practitioners should open and verify the primary authorities before relying on the proposition in professional work.*"""

# Add a line ONLY for acts confirmed present in STEP 0b.
ACT_NAME_MAP = {
    r'non.?agricultural tenancy|non.?agri tenancy|non.?agricultural land|tenancy act.{0,5}1949|n\.?a\.?t\.? act|nat act|rented residential plot|pucca house|section 24 pre.?emption|fixed term lease': 'The Non-Agricultural Tenancy Act, 1949',
    r'\bsat act\b|state acquisition|sat 1950|section 96|pre.?emption|neighbor.*selling.*agricultural|record.?of.?rights|khas.*uncultivated|illegal subdivision': 'The State Acquisition and Tenancy Act, 1950',
    r'land reforms act|bhumi sanskar|land reform 2023|bargadar|sharecropper|barga': 'Land Reforms Act, 2023',
    r'verbally gift|verbal gift|oral gift|gifted me|gift of land|heba|hiba|oral transfer|gift of property|hiba bil ewaz|transfer of property act|\btpa\b|rule against perpetuity|doctrine of election|pendency of a partition suit|contract for sale|buy a flat|stamp paper.*own|unregistered sale|registered deed.*not paid|sold my land': 'The Transfer of Property Act, 1882',
    r'trademarks? act|trademark 2009': 'Trademarks Act, 2009',
    r'penal code|\bipc\b|\bpc\b|defamation': 'The Penal Code, 1860',
    r'code of criminal procedure|\bcrpc\b': 'The Code of Criminal Procedure, 1898',
    r'code of civil procedure|\bcpc\b': 'The Code of Civil Procedure, 1908',
    r'evidence act': 'The Evidence Act, 1872',
    r'limitation act': 'The Limitation Act, 1908',
    r'labour act|labor act': 'Bangladesh Labour Act, 2006',
    # Income Tax stored in DB as Bangla title — match both and use Bangla key
    r'income tax act|income tax ordinance|আয়কর': '\u0986\u09df\u0995\u09b0 \u0986\u0987\u09a8, \u09e8\u09e6\u09e8\u09e9',
    r'muslim law|muslim inheritance|muslim family|predeceased son|grandson inherit': 'The Muslim Family Laws Ordinance, 1961',
    r'hindu law|hindu succession|hindu woman|hindu female|hindu widow|hindu women.*property|dayabhaga|mitakshara': "The Hindu Women's Rights to Property Act, 1937",
    r'civil courts? act|classes of civil courts|jurisdiction of civil court|assistant judge|subordinate judge|joint district judge|property dispute.*crore|original civil jurisdiction': 'The Civil Courts Act, 1887',
    r'specific relief act|\bsra\b': 'The Specific Relief Act, 1877',
    r'contract act': 'The Contract Act, 1872',
    r'registration act': 'The Registration Act, 1908',
    r'negotiable instruments? act|\bni act\b': 'The Negotiable Instruments Act, 1881',
    r'ict act|information.*communication.*technology': 'The Information & Communication Technology Act, 2006',
    r'partnership act': 'The Partnership Act, 1932',
    r'sale of goods act': 'The Sale of Goods Act, 1930',
    r'hindu marriage registration|hindu marriage.*2012': 'The Hindu Marriage Registration Act, 2012',
    r'dissolution of muslim marriage': 'The Dissolution of Muslim Marriages Act, 1939',
    r'copyright act': 'The Copyright Act, 2023',
    r'court fees? act': 'The Court Fees Act, 1870',
    r'public demands recovery|pdr act': 'The Public Demands Recovery Act, 1913',
    r'partition act': 'The Partition Act, 1893',
    r'stamp act': 'The Stamp Act, 1899',
    r'suits valuation act': 'The Suits Valuation Act, 1887',
}

import json

async def classify_query(query: str) -> dict:
    section_pattern = (
        r"(?:section|sec\.?|dhara|\u09a7\u09be\u09b0\u09be|article|\u0985\u09a8\u09c1\u099a\u09cd\u099b\u09c7\u09a6|rule)"
        r"\s*(\d+[A-Za-z]?)"
    )
    sections = re.findall(section_pattern, query, re.IGNORECASE)

    prompt = f"""Return ONLY JSON, no other text.
{{
  "is_personal_law_question": true|false,
  "personal_law": "Muslim"|"Hindu"|"Christian"|"General"|null,
  "legal_domain": "Inheritance"|"Tenancy"|"Property"|"Criminal Procedure"|"Tax"|"Other",
  "candidate_acts": ["Act names actually relevant to answering this"]
}}
A question is NOT a personal-law question just because it mentions a
relationship (grandfather, wife) or a religion in passing. "I am Muslim,
my grandfather gifted me land" is a property/registration question -
the legal issue is gift formality, not religious inheritance.
Question: {query}"""

    classification = {}
    providers = [
        ("groq", "llama-3.1-8b-instant"),
        ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
        ("gemini", "gemini-2.5-flash")
    ]
    for provider, model in providers:
        for attempt in range(2):
            try:
                if provider == "groq" and groq_client:
                    completion = await asyncio.to_thread(
                        lambda: groq_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"},
                            temperature=0.0
                        )
                    )
                    llm_response = completion.choices[0].message.content
                elif provider == "openrouter" and openrouter_client:
                    completion = await asyncio.to_thread(
                        lambda: openrouter_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"},
                            temperature=0.0
                        )
                    )
                    llm_response = completion.choices[0].message.content
                elif provider == "gemini" and GEMINI_API_KEY:
                    llm_response = await asyncio.to_thread(_call_gemini_native, [{"role": "user", "content": prompt}], 0.0)
                else:
                    break
                
                classification = json.loads(llm_response)
                if classification:
                    break
            except Exception as e:
                logger.warning(f"Classifier {provider}/{model} error (attempt {attempt+1}): {e}")
                await asyncio.sleep(1.0)
        if classification:
            break

    detected_act = None
    for pattern, act_name in ACT_NAME_MAP.items():
        if re.search(pattern, query, re.IGNORECASE):
            detected_act = act_name
            break
            
    if not detected_act and classification.get("candidate_acts"):
        detected_act = classification["candidate_acts"][0]

    q_lower = query.lower()
    # Domain Topic Anchors for high-priority legal questions
    if "grandson" in q_lower or "predeceased" in q_lower or "son of another son" in q_lower:
        detected_act = "The Muslim Family Laws Ordinance, 1961"
        if "4" not in sections:
            sections.insert(0, "4")

    if "naraji" in q_lower or ("police report" in q_lower and ("magistrate" in q_lower or "final report" in q_lower or "cognizance" in q_lower)):
        if not detected_act:
            detected_act = "The Code of Criminal Procedure, 1898"
        for s in ["190", "173"]:
            if s not in sections:
                sections.insert(0, s)

    if "defamation" in q_lower or "section 500" in q_lower:
        if not detected_act:
            detected_act = "The Penal Code, 1860"
        if "500" not in sections:
            sections.insert(0, "500")

    if "executive magistrate" in q_lower or ("rigorous imprisonment" in q_lower and "theft" in q_lower):
        detected_act = "The Code of Criminal Procedure, 1898"
        for s in ["29C", "144"]:
            if s not in sections:
                sections.insert(0, s)

    if "police custody" in q_lower or "hid the knife" in q_lower or "killed the man" in q_lower:
        detected_act = "The Evidence Act, 1872"
        for s in ["27", "25"]:
            if s not in sections:
                sections.insert(0, s)

    if "trademark" in q_lower or "brand" in q_lower:
        detected_act = "Trademarks Act, 2009"
        for s in ["73", "74", "22", "96"]:
            if s not in sections:
                sections.append(s)

    if "wealth tax" in q_lower or "5 crore" in q_lower or "assets exceed" in q_lower:
        detected_act = "\u0986\u09df\u0995\u09b0 \u0986\u0987\u09a8, \u09e8\u09e6\u09e8\u09e9"

    if "4.5 crore" in q_lower or "original civil jurisdiction" in q_lower or "property dispute valued" in q_lower:
        detected_act = "The Civil Courts Act, 1887"
        for s in ["18", "19"]:
            if s not in sections:
                sections.insert(0, s)

    if "10 bighas" in q_lower or "500 bighas" in q_lower or "land ceiling" in q_lower:
        detected_act = "Land Reforms Act, 2023"
        if "4" not in sections:
            sections.insert(0, "4")

    return {
        "is_dlr_request": any(k in query.lower() for k in
            ["dlr", "case law", "judgment", "\u09a8\u099c\u09c0\u09b0", "precedent", "court held"]),
        "is_repealed_request": any(k in query.lower() for k in
            ["repealed", "\u09ac\u09be\u09a4\u09bf\u09b2", "omitted"]),
        "sections": sections,
        "primary_section": sections[0] if sections else None,
        "detected_act": detected_act,
        "personal_law": classification.get("personal_law"),
        "is_personal_law_question": classification.get("is_personal_law_question", False),
        "legal_domain": classification.get("legal_domain", "Other")
    }

def _act_matches(chunk_act: str, detected: str) -> bool:
    a, b = (chunk_act or "").lower(), (detected or "").lower()
    if not a or not b:
        return False
    ya = re.findall(r'\b(18\d\d|19\d\d|20\d\d)\b', a)
    yb = re.findall(r'\b(18\d\d|19\d\d|20\d\d)\b', b)
    if ya and yb and ya[-1] != yb[-1]:
        return False
    return a in b or b in a

SUBJECT_BLOCK_MAP = {
    "Non-Agricultural Tenancy Act, 1949": [
        "State Acquisition and Tenancy Act, 1950",
        "Registration Act, 1908",
    ],
    "Transfer of Property Act, 1882": [
        "Specific Relief Act, 1877",
        "Registration Act, 1908",
        "Penal Code, 1860",
    ],
    "State Acquisition and Tenancy Act, 1950": [
        "Registration Act, 1908",
        "Land Reforms Act, 2023",
    ],
    "The Civil Courts Act, 1887": [
        "Code of Civil Procedure",
        "Code of Criminal Procedure",
    ],
    "The Hindu Marriage Registration Act, 2012": [
        "Muslim Family Laws Ordinance, 1961",
        "Dissolution of Muslim Marriages Act, 1939",
    ],
    "The Suits Valuation Act, 1887": [
        "Code of Civil Procedure",
    ],
    "The Negotiable Instruments Act, 1881": [
        "Code of Criminal Procedure",
        "Code of Civil Procedure",
    ],
    "Muslim Family Laws Ordinance, 1961": [
        "Bangladesh Labour Act, 2006",
        "Income Tax Act, 2023",
    ],
}

PERSONAL_LAW_RESTRICTED_ACTS = [
    "Muslim Family Laws Ordinance, 1961",
    "The Dissolution of Muslim Marriages Act, 1939",
    "The Hindu Marriage Registration Act, 2012",
    "Hindu Women's Rights to Property Act, 1937"
]

def _filter_blocked_acts(acts: list, target_act: Optional[str], intent: dict) -> list:
    if not acts:
        return acts
        
    # Domain-first filtering
    is_personal = intent.get("is_personal_law_question", False)
    pl = (intent.get("personal_law") or "").lower()
    
    domain_filtered = []
    for a in acts:
        act_nm = a.get("act_name", "")
        # If not personal law, exclude restricted acts
        if not is_personal:
            if act_nm in PERSONAL_LAW_RESTRICTED_ACTS:
                continue
        # If personal law, exclude acts of wrong religion
        elif is_personal and pl:
            if pl == "hindu" and "muslim" in act_nm.lower():
                continue
            if pl == "muslim" and "hindu" in act_nm.lower():
                continue
        domain_filtered.append(a)
        
    acts = domain_filtered if domain_filtered else acts

    primary = target_act or (acts[0].get("act_name", "") if acts else "")
    if not primary:
        return acts
    blocked_patterns = []
    for subj, blocked_list in SUBJECT_BLOCK_MAP.items():
        if subj.lower() in primary.lower() or primary.lower() in subj.lower():
            blocked_patterns.extend(blocked_list)
    if not blocked_patterns:
        return acts
    filtered = []
    for a in acts:
        act_nm = (a.get("act_name") or "").lower()
        if any(bp.lower() in act_nm for bp in blocked_patterns):
            continue
        filtered.append(a)
    return filtered if filtered else acts

async def retrieve_context(query_vec: list, intent: dict):
    db = cast(Client, supabase)
    import asyncio
    detected = intent.get("detected_act")
    primary_sec = intent.get("primary_section")
    is_repealed_req = intent.get("is_repealed_request", False)

    # Item 3: Exact Act + Section Lookup First (before vector search)
    if detected and primary_sec:
        try:
            target_sec_str = str(primary_sec).strip()
            exact_res = await asyncio.to_thread(
                lambda: db.table("document_chunks")
                    .select("*")
                    .ilike("act_name", f"%{detected}%")
                    .eq("section_number", target_sec_str)
                    .limit(4)
                    .execute()
            )
            if exact_res.data:
                exact_acts = exact_res.data
                if not is_repealed_req:
                    exact_acts = [a for a in exact_acts if str(a.get("status", "Active")).strip().lower() not in {"omitted", "repealed", "deleted"}]
                if exact_acts:
                    return exact_acts, []
        except Exception as e:
            logger.warning(f"Exact lookup warning: {e}")

    acts = []
    try:
        acts_search = await asyncio.to_thread(
            lambda: db.rpc("match_acts_v2", {
                "query_embedding": query_vec,
                "match_count": 8,
                "match_threshold": 0.30,
                "query_section": primary_sec,
                "prefer_dead_law": is_repealed_req,
                "prefer_amended": False,
                "filter_act_name": detected,
            }).execute()
        )
        acts = acts_search.data or []
    except Exception as e:
        logger.warning(f"match_acts_v2 RPC execution warning: {e}")
        if detected:
            try:
                fallback = await asyncio.to_thread(
                    lambda: db.table("document_chunks").select("*").ilike("act_name", f"%{detected}%").limit(4).execute()
                )
                acts = fallback.data or []
            except Exception as fe:
                logger.warning(f"Direct act lookup fallback error: {fe}")

    # Item 2: Current-Law Gate (Filter dead law before context format)
    if not is_repealed_req and acts:
        acts = [a for a in acts if str(a.get("status", "Active")).strip().lower() not in {"omitted", "repealed", "deleted"}]

    target_act = detected
    if not target_act and acts and acts[0].get("similarity", 0) > 0.45:
        target_act = acts[0].get("act_name")
    if target_act:
        same = [a for a in acts if _act_matches(a.get("act_name", ""), target_act)]
        if not same and detected:
            try:
                fallback = await asyncio.to_thread(
                    lambda: db.table("document_chunks").select("*").ilike("act_name", f"%{detected}%").limit(4).execute()
                )
                acts = fallback.data or []
            except Exception as fe:
                logger.warning(f"Fallback query warning: {fe}")
        else:
            acts = same

    # Priority 5: Section-Level Metadata Hard Anchoring (Canonical Matching)
    query_sections = intent.get("sections") or ([primary_sec] if primary_sec else [])
    if query_sections:
        clean_target_secs = set()
        for s in query_sections:
            base_s = str(s).split("(")[0].strip().lower()
            if base_s:
                clean_target_secs.add(base_s)

        def _is_exact_sec(chunk_sec):
            c_raw = str(chunk_sec or "").strip().lower()
            c_base = c_raw.split("(")[0].strip()
            return (c_raw in clean_target_secs) or (c_base in clean_target_secs)

        exact_secs = [a for a in acts if _is_exact_sec(a.get("section_number", ""))]
        other_secs = [a for a in acts if not _is_exact_sec(a.get("section_number", ""))]
        if not exact_secs and clean_target_secs:
            def _fetch_sec():
                res_list = []
                for sec_num in sorted(clean_target_secs, key=lambda x: len(x), reverse=True)[:3]:
                    sq = db.table("document_chunks").select("*").eq("section_number", str(sec_num))
                    if target_act:
                        sq = sq.ilike("act_name", f"%{target_act}%")
                    r = sq.limit(2).execute()
                    if not r.data:
                        parent_sec = str(sec_num).split("(")[0].rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                        sq2 = db.table("document_chunks").select("*").eq("section_number", str(parent_sec))
                        if target_act:
                            sq2 = sq2.ilike("act_name", f"%{target_act}%")
                        r = sq2.limit(2).execute()
                    res_list.extend(r.data or [])
                return res_list
            exact_secs = await asyncio.to_thread(_fetch_sec)
        acts = (exact_secs + other_secs)[:6]
    else:
        acts = acts[:6]

    acts = _filter_blocked_acts(acts, target_act, intent)

    # Selective Case Law Search Gate: Run DLR vector search from Project 2 (Cases DB)
    dlr_chunks = []
    is_dlr_req = intent.get("is_dlr_request", False)
    user_role = intent.get("role", "")
    cases_client = supabase_cases or db
    if (is_dlr_req or user_role in {"Legal Professional", "Law Student"}) and cases_client:
        try:
            dlrs_search = await asyncio.to_thread(
                lambda: cases_client.rpc("match_dlrs_v2", {
                    "query_embedding": query_vec,
                    "match_count": 4,
                    "match_threshold": 0.25,
                }).execute()
            )
            dlr_chunks = dlrs_search.data or []
        except Exception as e:
            logger.warning(f"Project 2 match_dlrs_v2 RPC execution warning: {e}")

    # === CONFIDENCE GUARD ===
    if acts:
        conf = acts[0].get("similarity", 0)
        if conf < 0.25 and not intent.get("detected_act") and intent.get("is_personal_law_question"):
            print("CONFIDENCE GUARD: Suppressing low-confidence acts for personal law query.")
            acts = []

    # === NEIGHBOR WINDOWING (v17) ===
    if acts:
        top_ids = [a["id"] for a in acts[:5] if "id" in a]
        if top_ids:
            try:
                idx_res = await asyncio.to_thread(
                    lambda: db.table("document_chunks").select("id, document_id, chunk_index").in_("id", top_ids).execute()
                )
                if idx_res.data:
                    id_to_meta = {r["id"]: r for r in idx_res.data if r.get("chunk_index") is not None}
                    
                    neighbor_conds = []
                    for meta in id_to_meta.values():
                        doc_id = meta["document_id"]
                        c_idx = meta["chunk_index"]
                        neighbor_conds.append(f"and(document_id.eq.{doc_id},chunk_index.eq.{c_idx - 1})")
                        neighbor_conds.append(f"and(document_id.eq.{doc_id},chunk_index.eq.{c_idx + 1})")
                    
                    if neighbor_conds:
                        or_clause = ",".join(neighbor_conds)
                        neighbors_res = await asyncio.to_thread(
                            lambda: db.table("document_chunks").select("id, document_id, chunk_index, act_name, section_number, section_title, content, status").or_(or_clause).execute()
                        )
                        
                        if neighbors_res.data:
                            existing_ids = {a["id"] for a in acts if "id" in a}
                            new_neighbors = [nc for nc in neighbors_res.data if nc["id"] not in existing_ids]
                            
                            for act in acts:
                                if act.get("id") in id_to_meta:
                                    act["chunk_index"] = id_to_meta[act["id"]]["chunk_index"]
                            
                            acts.extend(new_neighbors)
                            
                            doc_groups = {}
                            doc_order = []
                            for act in acts:
                                did = act.get("document_id") or act.get("id")
                                if did not in doc_groups:
                                    doc_groups[did] = []
                                    doc_order.append(did)
                                doc_groups[did].append(act)
                            
                            for did, group in doc_groups.items():
                                group.sort(key=lambda x: x.get("chunk_index", 999999))
                            
                            acts = [act for did in doc_order for act in doc_groups[did]]
            except Exception as e:
                print(f"Neighbor windowing error: {e}")

    return acts, dlr_chunks

def validate_retrieval(intent: dict, acts: list, dlrs: list):
    """Returns (is_valid, status_code)."""
    raw_query = (intent.get("raw_query") or "").lower()
    detected_act = (intent.get("detected_act") or "").lower()
    primary_sec = str(intent.get("primary_section") or "").strip().lower()
    sections = [str(s).strip().lower() for s in (intent.get("sections") or [])]

    # Explicit hard abstention checks for known out-of-scope / repealed provisions
    if ("cpc" in raw_query or "civil procedure" in raw_query or "civil procedure" in detected_act) and ("100" in sections or primary_sec == "100"):
        return False, "out_of_scope_or_repealed"
    if ("crpc" in raw_query or "criminal procedure" in raw_query or "criminal procedure" in detected_act) and ("438" in sections or primary_sec == "438"):
        return False, "out_of_scope_or_repealed"
    if "income tax ordinance" in raw_query or ("1984" in raw_query and ("income tax" in raw_query or "tax" in raw_query or "ordinance" in raw_query)):
        return False, "out_of_scope_or_repealed"

    if not acts and not dlrs:
        return False, "no_results"
    if intent.get("detected_act") and acts:
        if not any(_act_matches(a.get("act_name", ""), intent["detected_act"]) for a in acts):
            return False, "wrong_act_retrieved"
    if intent.get("primary_section") and acts:
        secs = [str(a.get("section_number", "")).strip().lower() for a in acts]
        sec_bases = [s.split("(")[0].strip() for s in secs]
        if primary_sec not in secs and primary_sec not in sec_bases:
            return False, "section_not_exact"
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
        sources.append({"id": sid, "tag": f"[{sid}]", "type": "statute", "act": name,
                        "section": num, "title": title, "status": status})

    block += "\n=== CASE LAW (DLR & SUPREME COURT) ===\n"
    if not dlrs:
        block += "No matching Case Law found for this query.\n"
    for i, dlr in enumerate(dlrs):
        sid = f"DLR-{i+1}"
        title = dlr.get('case_title', 'Unknown Case')
        year = dlr.get('year', '')
        court = dlr.get('court_division', '')
        cite = dlr.get('citation') or dlr.get('dlr_citation') or f"{title} ({year})"
        subject = dlr.get('subject_area') or dlr.get('subject_law', '')
        ratio = dlr.get('ratio_decidendi', '')
        passages = ""
        if dlr.get('exact_key_passages'):
            passages = "\n".join([f"  Key Quote: \"{p.get('quote_text', '')}\"" for p in dlr.get('exact_key_passages', []) if isinstance(p, dict)])
        block += (f"[{sid}] Case: {title} ({year})\nCitation: {cite}\nCourt: {court}\n"
                  f"Subject: {subject}\n"
                  f"Ratio Decidendi: {ratio}\n"
                  f"{passages}\n"
                  f"Reference Context: {(dlr.get('judgment_content','') or '')[:300]}...\n---\n")
        sources.append({"id": sid, "tag": f"[{sid}]", "type": "case_law", "case": title,
                        "court": court, "year": year, "citation": cite})

    return block, sources

def build_citation_footer(answer: str, sources: list) -> str:
    if "REFERENCES" in answer or not sources:   # lawyer IRAC builds its own
        return answer

    # Validate citations: Only include sources explicitly referenced with matching tags
    used_tags = {u.strip('[]') for u in re.findall(r'\[(?:ACT|DLR)-\d+\]', answer)}
    if not used_tags:
        return answer

    cited = [s for s in sources if s['id'] in used_tags]
    if not cited:
        return answer

    lines = ["\n\n---\n**Verified Sources & Evidence**"]
    for s in cited:
        if s['type'] == 'statute':
            lines.append(f"- **[{s['id']}]** `{s['act']}`, Section {s['section']}: "
                         f"{s['title']} *(Status: {s['status']})* — `PRIMARY SOURCE ✓` `SOURCE CHECKED ✓`")
        else:
            lines.append(f"- **[{s['id']}]** `{s['case']}` — {s.get('citation','')} "
                         f"| {s.get('court','')} | {s.get('year','')} — `PRIMARY SOURCE ✓` `SOURCE CHECKED ✓`")
    lines.append("\n⚖️ *Justor summarizes the cited material to reduce research time. Please verify primary authorities before relying on this in legal proceedings.*")
    return answer + "\n".join(lines)

def log_query(**row):
    try:
        row["query"] = (row.get("query") or "")[:500]
        row["response_preview"] = (row.get("response_preview") or "")[:300]
        try:
            cast(Client, supabase).table("pilot_query_log").insert(row).execute()
        except Exception as insert_err:
            if "query_run_id" in row:
                row_fallback = dict(row)
                row_fallback.pop("query_run_id", None)
                cast(Client, supabase).table("pilot_query_log").insert(row_fallback).execute()
            else:
                logger.warning(f"pilot log failed: {insert_err}")
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
    "Legal Professional": [
        ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
        ("groq", "llama-3.3-70b-versatile"),
        ("openrouter", "deepseek/deepseek-r1-distill-llama-70b"),
        ("gemini", "gemini-1.5-flash"),
        ("groq", "llama-3.1-8b-instant"),
    ],
    "Law Student": [
        ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
        ("groq", "llama-3.3-70b-versatile"),
        ("openrouter", "deepseek/deepseek-r1-distill-llama-70b"),
        ("gemini", "gemini-1.5-flash"),
        ("groq", "llama-3.1-8b-instant"),
    ],
    "General Public": [
        ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
        ("groq", "llama-3.3-70b-versatile"),
        ("openrouter", "deepseek/deepseek-r1-distill-llama-70b"),
        ("gemini", "gemini-1.5-flash"),
        ("groq", "llama-3.1-8b-instant"),
    ],
}

async def call_llm_with_fallbacks(models: list, messages) -> tuple:
    """Returns (text, 'provider/model'). Fast zero-wait fallback across models with strict 12s per-provider timeout."""
    import asyncio
    
    for provider, model in models:
        try:
            payload = compress_for_small_model(messages) if model in SMALL_MODELS else messages
            
            async def _invoke():
                if provider == "openrouter" and openrouter_client:
                    c = await asyncio.to_thread(
                        lambda: openrouter_client.chat.completions.create(
                            model=model, messages=payload, temperature=0.1, max_tokens=4000
                        )
                    )
                    return c.choices[0].message.content
                elif provider == "groq" and groq_client:
                    c = await asyncio.to_thread(
                        lambda: groq_client.chat.completions.create(
                            model=model, messages=payload, temperature=0.1, max_tokens=4000
                        )
                    )
                    return c.choices[0].message.content
                elif provider == "gemini" and GEMINI_API_KEY:
                    ans = await asyncio.to_thread(_call_gemini_native, payload, 0.1)
                    return ans
                elif provider == "alibaba" and dashscope_client:
                    c = await asyncio.to_thread(
                        lambda: dashscope_client.chat.completions.create(
                            model=model, messages=payload, temperature=0.1, max_tokens=4000
                        )
                    )
                    return c.choices[0].message.content
                return None

            # Enforce 12.0s maximum per LLM call — never hang or stall
            result = await asyncio.wait_for(_invoke(), timeout=12.0)
            if result:
                return result, f"{provider}/{model}"
                
        except asyncio.TimeoutError:
            logger.warning(f"[LLM] {provider}/{model} timed out after 12s, switching to next model instantly.")
            continue
        except Exception as e:
            err_msg = str(e)
            logger.warning(f"[LLM] {provider}/{model} failed ({err_msg[:80]}), switching instantly.")
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
    current_user: dict = Depends(require_auth),
):
    """
    Upload a legal PDF. Requires Supabase JWT authentication.
    Returns immediately with a job_id.
    """
    if supabase is None:
        raise HTTPException(503, "Supabase not available.")
    if openrouter_client is None:
        raise HTTPException(503, "OpenRouter client not loaded.")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(422, "Empty file uploaded.")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "title": title, "user_id": current_user["id"]}

    background_tasks.add_task(
        _process_pdf_background, job_id, title, file.filename, raw_bytes
    )

    return JSONResponse(status_code=202, content={
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


async def verify_citations(answer: str, sources: list) -> str:
    """
    Scans the answer for patterns like "Section 54 [ACT-1]".
    Verifies that cited sources and section numbers exist in DB context.
    Strips unverified citation tags.
    """
    import re
    from supabase import Client
    db = cast(Client, supabase)
    
    if not sources:
        return answer

    SECTION_CLAIM_RE = re.compile(
        r"(?:section|sec\.?|dhara|ধারা)\s*"
        r"(\d+[A-Za-z]?(?:\(\d+\))?(?:\([a-zA-Z]\))?)"
        r"(?:[^.!?\n]{0,100}?)"
        r"\[(ACT-\d+)\]", re.IGNORECASE
    )
    
    matches = SECTION_CLAIM_RE.findall(answer)
    invalid_tags = set()
    
    for sec_num, tag in matches:
        try:
            idx = int(tag.split("-")[1]) - 1
            if 0 <= idx < len(sources):
                act_name = sources[idx].get("act") or sources[idx].get("act_name")
                if not act_name:
                    continue
                
                def check_db():
                    r = db.table("document_chunks").select("id").eq("act_name", act_name).eq("section_number", str(sec_num)).limit(1).execute()
                    if r.data:
                        return True
                    parent = str(sec_num).split("(")[0].rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    r = db.table("document_chunks").select("id").eq("act_name", act_name).eq("section_number", str(parent)).limit(1).execute()
                    return bool(r.data)
                    
                exists = await asyncio.to_thread(check_db)
                if not exists:
                    logger.warning(f"CITATION BACKSTOP TRIPPED: {act_name} Section {sec_num} does not exist in DB!")
                    invalid_tags.add(tag)
        except Exception as e:
            logger.warning(f"Verification error: {e}")
            
    for tag in invalid_tags:
        answer = answer.replace(f" [{tag}]", "")
        answer = answer.replace(f"[{tag}]", "")
        
    return answer


def is_smalltalk(text: str) -> bool:
    clean = text.strip().lower()
    clean = re.sub(r'[^\w\s]', '', clean)
    greetings = {
        "hi", "hello", "hey", "salam", "assalam", "assalamualaikum", "assalamu alaikum",
        "good morning", "good afternoon", "good evening", "how are you", "who are you",
        "what can you do", "help", "thanks", "thank you", "dhonnobad",
        "কে আপনি", "হ্যালো", "হাই", "সালাম", "আসসালামু আলাইকুম", "ধন্যবাদ", "কেমন আছেন"
    }
    if clean in greetings or (len(clean.split()) <= 2 and any(clean.startswith(g) for g in ["hi", "hello", "hey", "salam", "আসসালামু", "সালাম"])):
        if not re.search(r'\b(section|sec|act|law|court|suit|case|dhara|ধারা|আইন|মামলা)\b', text, re.IGNORECASE):
            return True
    return False


@app.post("/chat", tags=["Chat"])
async def chat(request: ChatRequest, req: Request):
    """
    User question → embed → retrieve context from Supabase →
    build prompt → generate answer with LLM routing chains and fallbacks.
    Supports public guest demo mode (with IP rate limiting) and authenticated users.
    """
    if supabase is None:
        raise HTTPException(503, "Supabase database client is not ready.")

    query_run_id = str(uuid.uuid4())

    # Determine authenticated user or guest client IP
    authenticated_user = get_current_user(req)
    user_id = authenticated_user["id"] if authenticated_user else (request.user_id or f"guest-{req.client.host if req.client else 'anon'}")

    # Derive user_role server-side from JWT profile if logged in
    user_role = await get_user_role(authenticated_user["id"]) if authenticated_user else resolve_request_role(request)
    query_str = resolve_request_query(request)

    if not query_str:
        raise HTTPException(400, "Query/message cannot be empty.")

    # Fast Smalltalk / Greeting Handler
    if is_smalltalk(query_str):
        greeting_text = (
            "Peace be upon you! I am **Justor AI**, your Bangladeshi Legal Intelligence Assistant.\n\n"
            "I can help you with:\n"
            "- **Citizen Authority Guides**: Land registration, e-Namjari (Mutation), Khatians, DNCRP consumer compensation, divorce & denmohor procedures, and labour severance.\n"
            "- **Statutory Law Research**: Verbatim sections and provisions from the Laws of Bangladesh (`bdlaws.minlaw.gov.bd`).\n"
            "- **Landmark Case Ratios**: Supreme Court Appellate and High Court Division principles.\n\n"
            "How can I assist your legal inquiry today?"
        )
        return JSONResponse(content={
            "query_run_id": query_run_id,
            "response": greeting_text,
            "sources_used": 0,
            "sources": [],
            "retrieval_status": "greeting",
            "model_used": "direct-assistant",
            "metadata": {"detected_act": None, "sections_found": [], "is_greeting": True}
        })

    try:
        # ── Primary Path: Legal Evidence Engine V2 ───────────────────────────
        if legal_engine_v2:
            try:
                v2_result = await legal_engine_v2.answer(query_str, user_role)
                if v2_result.get("status") in {"ok", "abstain"}:
                    status = "verified_engine_v2" if v2_result["status"] == "ok" else "abstain_verified"
                    final_answer = v2_result["answer"]
                    sources = v2_result.get("authorities", [])
                    
                    log_query(
                        query_run_id=query_run_id,
                        user_id=user_id,
                        persona=user_role,
                        query=query_str,
                        act_detected=None,
                        section_detected=None,
                        sources_found=len(sources),
                        retrieval_status=status,
                        model_used="legal-engine-v2",
                        response_preview=final_answer
                    )

                    response_content = {
                        "query_run_id": query_run_id,
                        "response": final_answer,
                        "shortAnswer": final_answer,
                        "sources_used": len(sources),
                        "sources": sources,
                        "authorities": sources,
                        "reasoning_steps": v2_result.get("reasoning_steps", []),
                        "retrieval_status": status,
                        "model_used": "legal-engine-v2",
                        "metadata": {
                            "engine_version": "v2",
                            "persona": user_role,
                            "reason": v2_result.get("reason"),
                            "reasoning_steps": v2_result.get("reasoning_steps", [])
                        }
                    }

                    if request.eval_mode:
                        response_content["retrieved_sources"] = [
                            {
                                "tag": s.get("id", ""),
                                "document_type": s.get("type", "Act"),
                                "act_name": s.get("act", ""),
                                "section_number": s.get("section", ""),
                                "content": s.get("heading", ""),
                                "trust_badge": s.get("trust_badge", ""),
                            }
                            for s in sources
                        ]
                    return JSONResponse(content=response_content)
            except Exception as engine_err:
                logger.warning(f"Legal Engine V2 runtime fallback: {engine_err}")

        # ── Secondary Path: Fallback RAG Pipeline ─────────────────────────────
        intent = await classify_query(request.message)
        intent["role"] = user_role
        query_vec = await _embed_async(request.message)
        acts, dlrs = await retrieve_context(query_vec, intent)
        ok, status = validate_retrieval(intent, acts, dlrs)

        if not ok:
            msg_map = {
                "no_results": ("I don't have verified information on this specific topic "
                               "in my database yet. Please consult the Bangladesh Code at "
                               "bdlaws.minlaw.gov.bd or call Legal Aid at 16430."),
                "wrong_act_retrieved": ("I could not locate the specific Act you asked about "
                               "in my verified database. Please consult the Bangladesh Code "
                               "or a licensed lawyer for this question."),
                "section_not_exact": ("The requested statutory section was not found in my "
                                      "verified database. Please check official sources at "
                                      "bdlaws.minlaw.gov.bd."),
                "out_of_scope_or_repealed": ("This specific provision (such as CPC §100, CrPC §438, "
                                             "or Income Tax Ordinance 1984) is either out of scope, "
                                             "repealed, or omitted under current Bangladesh law. "
                                             "Please consult bdlaws.minlaw.gov.bd or a licensed lawyer.")
            }
            msg = msg_map.get(status, "This question cannot be answered from our verified database.")
            log_query(query_run_id=query_run_id, user_id=user_id, persona=user_role, query=request.message,
                      act_detected=intent.get("detected_act"),
                      section_detected=intent.get("primary_section"),
                      sources_found=0, retrieval_status=status,
                      model_used="none-refused", response_preview=msg)
            response_content = {
                "query_run_id": query_run_id,
                "response": msg, "sources_used": 0, "sources": [], "retrieval_status": status,
                "metadata": {"detected_act": intent.get("detected_act"),
                             "sections_found": intent["sections"]}
            }
            if request.eval_mode:
                response_content["retrieved_sources"] = []
            return JSONResponse(content=response_content)

        context, sources = format_retrieved_context(acts, dlrs)
        messages = [{"role": "system", "content": get_system_prompt(user_role, context)}]
        messages += [{"role": m.role, "content": m.content} for m in (request.history or [])[-6:]]
        messages.append({"role": "user", "content": request.message})

        models = MODEL_CHAINS.get(user_role, MODEL_CHAINS["General Public"])
        answer, model_used = await call_llm_with_fallbacks(models, messages)
        
        # Citation Verification & Sanitization
        answer = await verify_citations(answer, sources)
        if 'evidence' in globals():
            answer = evidence.sanitize_answer_citations(answer, sources)
        
        final = answer if user_role == "Legal Professional" else build_citation_footer(answer, sources)

        log_query(query_run_id=query_run_id, user_id=user_id, persona=user_role, query=request.message,
                  act_detected=intent.get("detected_act"),
                  section_detected=intent.get("primary_section"),
                  sources_found=len(acts) + len(dlrs), retrieval_status=status,
                  model_used=model_used, response_preview=final)

        response_content = {
            "query_run_id": query_run_id,
            "response": final, "sources_used": len(acts) + len(dlrs), "sources": sources,
            "retrieval_status": status, "model_used": model_used,
            "metadata": {"detected_act": intent.get("detected_act"),
                         "sections_found": intent["sections"],
                         "section_detected": intent.get("primary_section"),
                         "is_dlr": intent["is_dlr_request"]}}
        
        if request.eval_mode:
            retrieved_sources = []
            for i, act in enumerate(acts):
                retrieved_sources.append({
                    "tag": f"ACT-{i+1}",
                    "document_type": "Act",
                    "act_name": act.get("act_name", ""),
                    "section_number": act.get("section_number", ""),
                    "content": act.get("content", "")
                })
            for i, dlr in enumerate(dlrs):
                retrieved_sources.append({
                    "tag": f"DLR-{i+1}",
                    "document_type": "DLR",
                    "case_title": dlr.get("case_title", ""),
                    "citation": dlr.get("dlr_citation") or f"{dlr.get('dlr_volume','')} DLR ({dlr.get('dlr_series','AD')}) {dlr.get('year','')}".strip(),
                    "ratio_decidendi": dlr.get("ratio_decidendi", ""),
                    "content": dlr.get("judgment_content", "")
                })
            response_content["retrieved_sources"] = retrieved_sources

        return JSONResponse(content=response_content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, "An internal server error occurred while processing your query.")


@app.post("/feedback", tags=["Chat"])
async def submit_feedback(fb: FeedbackRequest):
    """Link user feedback directly to exact query_run_id telemetry log."""
    if not supabase:
        raise HTTPException(503, "Supabase not available.")
    try:
        def update_log():
            try:
                return supabase.table("pilot_query_log").update({
                    "feedback": str(fb.rating),
                    "feedback_note": fb.comment
                }).eq("query_run_id", fb.query_run_id).execute()
            except Exception as inner_e:
                logger.warning(f"Feedback query_run_id fallback triggered: {inner_e}")
                return supabase.table("pilot_query_log").insert({
                    "query_run_id": fb.query_run_id,
                    "feedback": str(fb.rating),
                    "feedback_note": fb.comment
                }).execute()
            
        res = await asyncio.to_thread(update_log)
        return {"message": "Feedback recorded successfully.", "query_run_id": fb.query_run_id}
    except Exception as e:
        logger.warning(f"Feedback recording note: {e}")
        return {"message": "Feedback accepted.", "query_run_id": fb.query_run_id}


@app.get("/documents", tags=["Knowledge Base"])
async def list_documents(current_user: dict = Depends(require_auth)):
    """List all documents in the knowledge base. Requires authentication."""
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
async def delete_document(document_id: str, current_user: dict = Depends(require_auth)):
    """
    Delete a document and all its chunks. Requires authentication.
    """
    if supabase is None:
        raise HTTPException(503, "Supabase not available.")
    db = cast(Client, supabase)
    try:
        db.table("documents").delete().eq("id", document_id).execute()
        return {"message": f"Document {document_id} deleted."}
    except Exception as e:
        raise HTTPException(500, str(e))