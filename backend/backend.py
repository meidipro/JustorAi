import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# RAG imports
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import PyPDF2
from groq import Groq

# Load environment variables
load_dotenv(".env")
load_dotenv(".env.local")

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Legal AI RAG Backend",
    description="Custom RAG backend using Supabase pgvector, FastAPI, and Groq.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-vercel-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration & Setup ---

# Initialize Supabase
# NOTE: To bypass Row Level Security when inserting data, ensure you are using the SERVICE_ROLE_KEY
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase URL or Key is missing. RAG functionality will fail.")

# In a real app, you might lazily initialize this to speed up API startup
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

# Initialize Groq for LLM Generation
GROQ_API_KEY = os.getenv("VITE_GROQ_API_KEY")
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    logger.warning("VITE_GROQ_API_KEY is not set.")
    groq_client = None

# Initialize Sentence Transformer for Embeddings
# 'all-MiniLM-L6-v2' is fast and creates 384-dimensional vectors.
# If you used 1024 dimension in SQL, you might want 'bge-large-en-v1.5' or similar,
# but for speed and demonstration we'll stick to a standard smaller model here.
# IMPORTANT: Adjust your SQL schema vector(384) to match this model's output dimension if needed!
logger.info("Loading embedding model...")
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 
    VECTOR_DIMENSION = 384 
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    embedding_model = None

# --- Pydantic Models for API Requests ---

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    role: Optional[str] = "General Public" # Law Student, Legal Professional, etc.

# --- Helper Functions ---

def generate_embedding(text: str) -> List[float]:
    if not embedding_model:
        raise ValueError("Embedding model not loaded")
    return embedding_model.encode(text).tolist()

def extract_text_from_pdf(pdf_file) -> str:
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def root():
    return {"message": "Legal AI RAG Backend is running!", "status": "OK"}

@app.post("/upload", tags=["Document ingestion"])
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Uploads a document, chunks it, generates embeddings, and saves to Supabase.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are currently supported")

    try:
        # 1. Extract text
        text_content = extract_text_from_pdf(file.file)
        
        # 2. Save document metadata
        doc_response = supabase.table('documents').insert({
            "title": title,
            "content": text_content[:500] + "...(truncated)" # Don't store massive raw text in DB unless needed
        }).execute()
        
        document_id = doc_response.data[0]['id']

        # 3. Chunk text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text_content)

        # 4. Generate embeddings and save chunks
        records = []
        for i, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            records.append({
                "document_id": document_id,
                "content": chunk,
                "embedding": embedding,
                "chunk_index": i,
                "metadata": {"source": file.filename}
            })
            
            # Batch insert every 100 chunks to avoid payload limits
            if len(records) >= 100:
                supabase.table('document_chunks').insert(records).execute()
                records = []
                
        # Insert remaining
        if records:
            supabase.table('document_chunks').insert(records).execute()

        return JSONResponse(status_code=200, content={
            "message": f"Successfully processed '{title}'",
            "document_id": document_id,
            "chunks_created": len(chunks)
        })

    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", tags=["Chat"])
async def chat_endpoint(chat_request: ChatMessage):
    """
    Retrieves context using RAG and generates an answer using Groq.
    """
    if not supabase or not groq_client or not embedding_model:
         return JSONResponse(status_code=500, content={"error": "Backend services not fully initialized"})

    try:
        # 1. Generate embedding for user query
        query_embedding = generate_embedding(chat_request.message)

        # 2. Perform similarity search via Supabase RPC
        # Ensure 'match_document_chunks' RPC exists handling the correct vector dimension
        search_results = supabase.rpc(
            'match_document_chunks',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.7, # Cosine similarity threshold (0 to 1)
                'match_count': 5        # Number of chunks to retrieve
            }
        ).execute()

        retrieved_chunks = search_results.data
        context_text = "\n\n---\n\n".join([chunk['content'] for chunk in retrieved_chunks]) if retrieved_chunks else "No specific legal documents found in knowledge base."

        # 3. Construct prompt (Based on dify_prompt_instruction.md)
        system_prompt = f"""
You are LegalAI.bd, a world-class legal information assistant specializing in Bangladeshi law.

Tone/Role Focus: {chat_request.role}

Using the following retrieved context from our legal knowledge base, answer the user's question.
If the context does not contain the answer, rely on your general knowledge but clearly state a disclaimer that it's not from the verified knowledge base.

RETRIEVED CONTEXT:
{context_text}
"""

        # 4. Generate response via Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": chat_request.message,
                }
            ],
            model="llama3-70b-8192", 
            temperature=0.3,
            max_tokens=2048
        )

        response_text = chat_completion.choices[0].message.content

        return JSONResponse(content={
            "response": response_text,
            "context_used": len(retrieved_chunks),
            "user_id": chat_request.user_id
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))