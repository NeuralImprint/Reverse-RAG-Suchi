import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import httpx
from main import state
import uuid
from typing import List
import PyPDF2
from io import BytesIO

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"

async def get_embedding(text: str) -> List[float]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={"model": EMBEDDING_MODEL, "prompt": text}
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ollama embedding failed: {str(e)}")

def extract_text(file: UploadFile, content: bytes) -> str:
    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
        return text
    elif file.filename.endswith(".txt"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("utf-16")
            except UnicodeDecodeError:
                return content.decode("windows-1252", errors="replace")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use txt or pdf.")

def chunk_text(text: str) -> List[str]:
    # Paragraph-based chunking
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        if len(p) > 2000:
            # Fallback for very long paragraphs: naive length chunking
            # split by sentences approximated or naive length
            for i in range(0, len(p), 1500):
                chunks.append(p[i:i+1500])
        else:
            chunks.append(p)
    return chunks

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = extract_text(file, content)
        chunks = chunk_text(text)
        
        if not chunks:
            return {"detail": "No text extracted."}

        # Upsert to Qdrant
        points = []
        for chunk in chunks:
            # Embedding
            vector = await get_embedding(chunk)
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "source": file.filename,
                    "text": chunk
                }
            })
        
        from qdrant_client.http.models import PointStruct
        qdrant_points = [PointStruct(**p) for p in points]
        state.qdrant.upsert(
            collection_name="ground_truth",
            points=qdrant_points
        )
            
        return {"status": "success", "chunks_processed": len(chunks), "filename": file.filename}
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        print(err_detail)
        raise HTTPException(status_code=500, detail=str(e))
