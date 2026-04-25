import os
import re
import logging
import asyncio
from typing import List, Optional, Dict, Any, cast

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import PyPDF2
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

# ─── Embedding Model ──────────────────────────────────────────────────────────
# all-MiniLM-L6-v2 → 384-dim, ~80 MB on disk, CPU-only, ideal for Render free tier
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIM = 384

embedding_model: Optional[SentenceTransformer] = None
try:
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info(f"Embedding model '{EMBEDDING_MODEL_NAME}' loaded ({VECTOR_DIM}-dim).")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")

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
    """Generate a 384-dim embedding. Caller must ensure embedding_model is not None."""
    model = cast(SentenceTransformer, embedding_model)
    # Strip null bytes — PostgreSQL cannot store \u0000
    clean_text = text.replace('\x00', '').replace('\u0000', '')
    return model.encode(clean_text, show_progress_bar=False).tolist()  # type: ignore[union-attr]


def classify_query(query: str):
    """
    Classifies legal intent of the query and extracts section numbers.
    """
    # Regex to find sections (e.g., "Section 302", "Dhara 302", "Sec 302")
    section_pattern = r"(?:section|sec|dhara|ধারা)\s*(\d+[A-Z]?)"
    sections = re.findall(section_pattern, query, re.IGNORECASE)
    
    # Detect intent
    intent = {
        "is_dlr_request": any(curr in query.lower() for curr in ["dlr", "case law", "judgment", "নজীর"]),
        "is_repealed_request": any(curr in query.lower() for curr in ["repealed", "বাতil", "বাতিল", "omitted"]),
        "sections": sections,
        "primary_section": sections[0] if sections else None
    }
    return intent


async def retrieve_context(query_vec: list, intent: dict):
    """
    Multi-lane retrieval for statutory law and case law.
    """
    db = cast(Client, supabase)
    
    # Acts Lane
    acts_search = db.rpc("match_acts_v2", {
        "query_embedding": query_vec,
        "match_count": 6,
        "match_threshold": 0.4,
        "query_section": intent['primary_section'],
        "prefer_dead_law": intent['is_repealed_request']
    }).execute()
    
    # DLR Lane
    dlrs_search = db.rpc("match_dlrs_v2", {
        "query_embedding": query_vec,
        "match_threshold": 0.4,
        "match_count": 3
    }).execute()
    
    return acts_search.data or [], dlrs_search.data or []


def format_retrieved_context(acts: list, dlrs: list):
    """
    Formats the context into a rigid, structured prompt block.
    """
    context_block = "=== STATUTORY LAW (ACTS) ===\n"
    if not acts:
        context_block += "No matching Acts found.\n"
    for i, act in enumerate(acts):
        status_suffix = f" [STATUS: {act['status']}]" if act['status'].lower() != 'active' else ""
        context_block += f"[{i+1}] {act['act_name']} - Section {act['section_number']}: {act['section_title']}{status_suffix}\n"
        context_block += f"Content: {act['content']}\n"
        if act['repealed_clauses'] and act['repealed_clauses'] != []:
            context_block += f"Note: The following clauses are Repealed: {act['repealed_clauses']}\n"
        if act['amendment_notes'] and act['amendment_notes'] != []:
            context_block += f"Amendments: {act['amendment_notes']}\n"
        context_block += "---\n"

    context_block += "\n=== CASE LAW (DLR) ===\n"
    if not dlrs:
        context_block += "No matching Case Law found.\n"
    for i, dlr in enumerate(dlrs):
        context_block += f"[{i+1}] Case: {dlr['case_title']} ({dlr['year']})\n"
        context_block += f"Subject: {dlr['subject_law']}\n"
        context_block += f"Ratio Decidendi: {dlr['ratio_decidendi']}\n"
        context_block += f"Reference Context: {dlr['judgment_content'][:1000]}...\n"
        context_block += "---\n"
        
    return context_block


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
        "embedding_model_ready": embedding_model is not None,
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
    if embedding_model is None:
        raise HTTPException(503, "Embedding model not loaded.")
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
    build prompt → generate answer with Llama 3.1 8B Instant via Groq.
    """
    if supabase is None or groq_client is None or embedding_model is None:
        raise HTTPException(503, "One or more backend services are not ready.")

    db = cast(Client, supabase)
    llm = cast(Groq, groq_client)

    try:
        # 1. Classify Query Intent
        intent = classify_query(request.message)
        
        # 2. Embed the user question
        query_vec = _embed(request.message)

        # 3. Multi-lane Retrieval
        acts, dlrs = await retrieve_context(query_vec, intent)
        
        # 4. Format Structured Context
        context_text = format_retrieved_context(acts, dlrs)

        # 5. Build System Prompt (Zero Hallucination)
        system_prompt = f"""# ROLE AND IDENTITY
You are Justor AI, a bilingual (Bangla and English) legal intelligence assistant for BANGLADESH.
You are a STRICT Retrieval-Augmented Generation (RAG) system.
You are NOT a general legal chatbot.
You are NOT allowed to answer from pretraining memory.
You must answer ONLY from the retrieved Bangladesh-law database context.

# THE SUPREME DIRECTIVE: ZERO HALLUCINATION
1. USE ONLY the [RETRIEVED DATABASE CONTEXT].
2. NEVER use outside knowledge, general training data, web memory, or laws from other countries.
3. NEVER guess a Section, Article, Rule, Act name.
4. If you cannot find the answer in the provided context, you MUST use the exact fallback response provided below.

# THE LANGUAGE RULE
1. Answer in the language the user asked in (Bangla or English).
2. If the user asks in "Banglish" (Bangla in Roman script), you MUST reply in pure Bangla script (Bengali).

# BANGLADESH-SPECIFIC LEGAL CONSTRAINTS (MANDATORY)
- Bangladesh CrPC 498 is for bail/anticipatory bail (NOT 438).
- Specific Performance (Limitation Act) for Bangladesh is 1 year (Article 113).
- Punishment for Murder in Bangladesh is Section 302 of the Penal Code.
- Citing "Indian" or "Pakistani" cases is a failure unless they are specifically mentioned in my database.

# AUDIENCE AND PERSONA (Context: {request.role})
Current Persona: {request.role}

---
## 🎓 PERSONA 1: THE LAW STUDENT
- Output Format:
  Section Title: [Act and Section Name]
  Explanation: [Plain language summary]
  Real-Life Example: [Relatable scenario]
  DLR Reference: [Reference case if present, else "No DLR found"]
- Fallback: "This law is not in my database, and I cannot provide unverified information."

---
## 🛡️ PERSONA 2: THE CONSUMER (General Public)
- Output Format:
  Section Title: [Act and Section Name]
  Explanation and Penalty: [Simple summary of law and punishment]
  Where to Reach: [Authorities mentioned]
  Evidence to Keep: [List evidence types]
  Estimate Cost/Time: [From context, else "Not specified"]
- Fallback: "আমি দুঃখিত, এই আইনটি আমার ডাটাবেসে নেই। ভুল তথ্য দেওয়া আইনত দণ্ডনীয় হতে পারে।"

---
## ⚖️ PERSONA 3: THE LAWYER (Legal Professional)
- Output Format: 
  Sections: [Exact section references]
  Case Law Highlights: [Important DLR point]
  Legal Drafting Summary: [Professional advice fragment]
- Fallback: "Query out of database bounds. Cannot provide legal guidance without source."

---
RETRIEVED DATABASE CONTEXT:
{context_text}
"""

        # 6. Build message payload for Groq
        messages_payload = [{"role": "system", "content": system_prompt}]
        
        # Inject recent chat history if provided
        if request.history:
            history_list = cast(List[ChatMessage], request.history)
            for msg in history_list:
                messages_payload.append({"role": msg.role, "content": msg.content})
                
        # Append the new user question
        messages_payload.append({"role": "user", "content": request.message})

        # 7. Groq — Llama 3.1 8B Instant
        completion = llm.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_payload,
            temperature=0.1, # Focused/deterministic
            max_tokens=2000,
        )

        answer = completion.choices[0].message.content

        return JSONResponse(content={
            "response": answer,
            "sources_used": len(acts) + len(dlrs),
            "user_id": request.user_id,
            "metadata": {
                "sections_found": intent['sections'],
                "is_dlr": intent['is_dlr_request']
            }
        })

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