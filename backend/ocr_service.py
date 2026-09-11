from __future__ import annotations

import os
import io
import json
import base64
import logging
import httpx
from typing import Dict, Any, List, Optional
from PIL import Image

logger = logging.getLogger("justor.ocr")

GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "justorai-508321").strip()
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1").strip()


class LegalDocumentOCRService:
    """
    Multimodal Vision OCR Service powered by Google Cloud Vertex AI (Gemini 2.5 Flash).
    Specially prompted for Bangladeshi legal documents:
    - Scanned Land Deeds (Kobala, Baina Patra, Heba Dalil)
    - Mutation Khatians (e-Namjari, CS/SA/RS/BS Khatians)
    - Police FIRs & General Diaries (GD)
    - High Court & Subordinate Court Orders
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_CLOUD_API_KEY

    def _get_vertex_endpoint(self, model_name: str = "gemini-2.5-flash") -> str:
        # Vertex AI Express endpoint with project API key billing against GCP credits
        return (
            f"https://aiplatform.googleapis.com/v1beta1/projects/{GCP_PROJECT_ID}"
            f"/locations/{VERTEX_LOCATION}/publishers/google/models/{model_name}:generateContent"
            f"?key={self.api_key}"
        )

    def _prepare_image_bytes(self, file_bytes: bytes, max_dim: int = 2048) -> tuple[str, str]:
        """Resizes image if too large while maintaining aspect ratio, returns (mime_type, base64_data)."""
        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Convert RGBA to RGB for JPEG compatibility
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Resize if necessary
            width, height = image.size
            if max(width, height) > max_dim:
                scale = max_dim / float(max(width, height))
                new_size = (int(width * scale), int(height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=88, optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return "image/jpeg", encoded
        except Exception as e:
            logger.warning("Image optimization fallback: %s", e)
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            return "image/jpeg", encoded

    async def analyze_legal_document(
        self,
        file_bytes: bytes,
        filename: str = "document.jpg",
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes layout-aware OCR and legal entity extraction.
        Returns parsed JSON containing document classification, parties, dates, sections, and transcription.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_API_KEY is not configured.",
                "details": {}
            }

        # Format image part
        img_mime, img_b64 = self._prepare_image_bytes(file_bytes)

        prompt = (
            "You are Justor AI's Senior Legal Document Analysis and Optical Character Recognition (OCR) Engine.\n"
            "Analyze this uploaded legal document from Bangladesh (it may be handwritten, typed, or a scanned record in Bengali or English).\n\n"
            "Tasks:\n"
            "1. Identify the exact Document Type (e.g., 'Land Sale Deed (কবলা দলিল)', 'Contract for Sale (বায়নাপত্র)', 'Mutation Khatian (ই-নামজারি খতিয়ান)', 'Police FIR (এজাহার)', 'Court Order Sheet (আদালতের আদেশনামা)', 'Affidavit (হলফনামা)').\n"
            "2. Extract Key Parties (First Party / Vendor / Complainant vs Second Party / Vendee / Accused) with names, father's names, and addresses if visible.\n"
            "3. Extract Key Property / Case Identifiers (Mouza, Khatian No, Dag/Plot No, Total Land Area, Deed No, Case No, Police Station, Thana, District).\n"
            "4. Identify any Governing Legal Acts or Sections referenced or implied (e.g., Registration Act 1908 s.17A, Transfer of Property Act s.54, Penal Code s.420).\n"
            "5. Detect Legal Red Flags or Validity Issues (e.g. missing Sub-Registry seal, missing witness signatures, expired limitation window, non-registration).\n"
            "6. Provide a complete, verbatim, layout-preserved transcription in clear Markdown.\n\n"
            "Return your response strictly as valid JSON matching this schema:\n"
            "{\n"
            '  "document_type": "string",\n'
            '  "language": "Bengali | English | Bilingual",\n'
            '  "confidence": 0.95,\n'
            '  "parties": {\n'
            '    "first_party": ["names"],\n'
            '    "second_party": ["names"]\n'
            '  },\n'
            '  "identifiers": {\n'
            '    "deed_or_case_number": "string or null",\n'
            '    "district": "string or null",\n'
            '    "thana": "string or null",\n'
            '    "mouza": "string or null",\n'
            '    "khatian_no": "string or null",\n'
            '    "dag_plot_no": "string or null",\n'
            '    "land_area": "string or null"\n'
            '  },\n'
            '  "dates": {\n'
            '    "execution_date": "string or null",\n'
            '    "registration_date": "string or null"\n'
            '  },\n'
            '  "statutory_provisions": ["list of Act and Section names"],\n'
            '  "potential_risks_or_notices": ["bullet points of legal red flags or advice"],\n'
            '  "transcription_markdown": "Full text of document in markdown formatting"\n'
            "}"
        )

        url = self._get_vertex_endpoint("gemini-2.5-flash")
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"inlineData": {"mimeType": img_mime, "data": img_b64}},
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 6000,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(url, json=body)
                if response.status_code != 200:
                    logger.error("Vertex OCR API failed (%s): %s", response.status_code, response.text[:200])
                    return {
                        "status": "error",
                        "message": f"Vertex AI OCR returned status {response.status_code}",
                        "details": response.text[:200]
                    }

                data = response.json()
                candidate = data.get("candidates", [{}])[0]
                text_content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Parse JSON
                try:
                    parsed = json.loads(text_content)
                except Exception:
                    # Clean markdown codeblocks if present
                    clean = text_content.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:]
                    if clean.startswith("```"):
                        clean = clean[3:]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    parsed = json.loads(clean.strip())

                return {
                    "status": "ok",
                    "filename": filename,
                    "analysis": parsed
                }

        except Exception as exc:
            logger.error("Document OCR analysis failed: %s", exc)
            return {
                "status": "error",
                "message": f"Document analysis error: {str(exc)}",
                "details": {}
            }


# Global service instance
legal_ocr_service = LegalDocumentOCRService()
