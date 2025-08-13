# backend.py (Simplified Version without Document Upload)

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Legal AI Backend",
    description="API for legal AI chat without document upload functionality.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-vercel-domain.vercel.app"],  # Add your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Requests ---

# Basic chat model for future use
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint to check if the service is running."""
    return {
        "message": "Legal AI Backend is running!",
        "status": "OK",
        "version": "2.0.0",
        "features": ["chat", "legal-ai"]
    }

@app.get("/health", tags=["Status"])
async def health_check():
    """Health check endpoint."""
    return JSONResponse(content={
        "status": "healthy",
        "message": "All systems operational",
        "timestamp": "2025-01-01T00:00:00Z"
    })

@app.post("/chat", tags=["Chat"])
async def chat_endpoint(message: ChatMessage):
    """
    Simple chat endpoint placeholder.
    This is where you would integrate with your chosen AI service.
    """
    return JSONResponse(content={
        "response": "Document upload and analysis features are coming soon! For now, you can chat with our general AI assistant.",
        "user_id": message.user_id,
        "feature_status": "coming_soon"
    })

@app.get("/features", tags=["Info"])
async def get_features():
    """
    Returns information about available and upcoming features.
    """
    return JSONResponse(content={
        "available_features": [
            "Basic chat functionality",
            "Health monitoring"
        ],
        "coming_soon": [
            "Document upload and analysis",
            "Legal document review",
            "Multi-format file support",
            "Advanced AI responses"
        ],
        "message": "Stay tuned for exciting updates!"
    })