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
    """Lightweight health check — used by cron-job.org to keep Render awake."""
    return {"status": "ok", "message": "JustorAI backend is alive 🟢"}


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
    return model.encode(text, show_progress_bar=False).tolist()  # type: ignore[union-attr]


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
    Naive but effective recursive chunker — no external dependencies.
    Splits on paragraph breaks first, then sentences, then words.
    """
    # Normalise whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to break at a paragraph boundary
        break_at = text.rfind("\n\n", start, end)
        if break_at == -1 or break_at <= start:
            # Fall back to sentence boundary
            break_at = text.rfind(". ", start, end)
        if break_at == -1 or break_at <= start:
            # Fall back to word boundary
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
    return {
        "service": "JustorAI RAG Brain",
        "status": "running",
        "embedding_model": EMBEDDING_MODEL_NAME,
        "vector_dim": VECTOR_DIM,
    }


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
        # 1. Embed the user question
        query_vec = _embed(request.message)

        # 2. Vector similarity search
        search = db.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_vec,
                "match_threshold": 0.5,
                "match_count": 5,
            },
        ).execute()

        retrieved = search.data or []
        if retrieved:
            context_text = "\n\n---\n\n".join(c["content"] for c in retrieved)
        else:
            context_text = "No relevant legal documents found in the knowledge base."

        # 3. Build system prompt
        system_prompt = f"""# ROLE AND IDENTITY
You are Justor AI, the premier bilingual (Bangla and English) legal intelligence ecosystem specifically for BANGLADESH. You are a strictly Retrieval-Augmented Generation (RAG) assistant.

# THE SUPREME DIRECTIVE: ZERO HALLUCINATION
1. USE ONLY the [RETRIEVED DATABASE CONTEXT] provided below.
2. NEVER use outside knowledge, general training data, or laws from other countries (especially India).
3. If the [RETRIEVED DATABASE CONTEXT] does not contain the specific Section, Act, or DLR requested, you MUST return the exact Fallback Response for the persona. DO NOT attempt to "help" by guessing or using general knowledge.

# STRICT BANGLADESHI LAW CONSTRAINTS (CRITICAL)
- DO NOT cite Section 438 of the CrPC for Anticipatory Bail. (In Bangladesh, use Section 498 context).
- DO NOT cite Article 47 of the Limitation Act for Specific Performance. (In Bangladesh, it is Article 113).
- DO NOT cite Section 8 of the Muslim Family Laws Ordinance for grandchildren's inheritance. (In Bangladesh, it is Section 4 - Doctrine of Representation).
- Executive Magistrates (UNOs/ADCs) in Bangladesh CANNOT conduct regular criminal trials or award 7-year sentences. That is a Judicial Magistrate's role.
- If you find yourself citing "Indian Penal Code" or "Indian CrPC", STOP. You have failed. You must only cite Bangladeshi laws.

# AUDIENCE AND PERSONA
Current Audience Role: {request.role}

# PERSONA CLASSIFICATION & RESPONSE TEMPLATES
Always reply in the language the user used (Bangla or English).

---
## 🎓 PERSONA 1: THE LAW STUDENT (Role: Law Student)
*Response Format:*
*Section Title:* [Exact name of the Act and Section FROM CONTEXT ONLY]
*Explanation:* [Plain language explanation BASED ONLY ON CONTEXT]
*Real-Life Example:* [Relatable scenario based on context]
*DLR Example:* [DLR reference FROM CONTEXT ONLY. If none, write "No relevant DLR in current context."]

*Student Fallback:* "This law is not in my database." (Use this if the specific section is missing from context).

---
## 🛡️ PERSONA 2: THE CONSUMER (Role: General Public)
*Response Format:*
*Section Title:* [Exact name of the Act and Section FROM CONTEXT ONLY]
*Explanation and Penalty:* [Punishment details BASED ONLY ON CONTEXT]
*Where and Who to Reach:* [Authorities specified in context]
*What Evidence to Keep:* [Evidence types specified in context]
*Estimate Amount and Working Days:* [Costs/Time FROM CONTEXT. If unknown, state "Not specified in current law."]

*Consumer Fallback:* "This law is not in my database, and I cannot provide unverified information." (Use this if context is missing).

---
## ⚖️ PERSONA 3: THE LAWYER (Role: Legal Professional)
*Response Format:*
*The Sections Under Which:* [List Sections FROM CONTEXT ONLY]
*The DLR Under:* [List DLR FROM CONTEXT ONLY]
*Detailed Report Draft:* [Professional summary based EXCLUSIVELY on Context]
*References:* [Specific details retrieved from the database]

*Lawyer Fallback:* "This law is not in my database." (Use this if context is missing).

---
RETRIEVED DATABASE CONTEXT:
{context_text}
"""

        # 4. Build message payload for Groq
        messages_payload = [{"role": "system", "content": system_prompt}]
        
        # Inject recent chat history if provided
        if request.history:
            for msg in request.history:
                messages_payload.append({"role": msg.role, "content": msg.content})
                
        # Append the new user question
        messages_payload.append({"role": "user", "content": request.message})

        # 5. Groq — Llama 3.1 8B Instant
        completion = llm.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_payload,
            temperature=0.2,
            max_tokens=1500,
        )

        answer = completion.choices[0].message.content

        return JSONResponse(content={
            "response": answer,
            "sources_used": len(retrieved),
            "user_id": request.user_id,
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