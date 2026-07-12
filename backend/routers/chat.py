import os
import json
import re
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from main import state

router = APIRouter()

OLLAMA_URL_CHAT = "http://localhost:11434/api/generate"
OLLAMA_URL_EMBED = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"
PRIMARY_MODEL = "llama3.2"

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
CEREBRAS_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = "llama3.1-8b"

class ChatRequest(BaseModel):
    prompt: str

async def get_embedding(text: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(OLLAMA_URL_EMBED, json={"model": EMBEDDING_MODEL, "prompt": text})
        res.raise_for_status()
        return res.json()["embedding"]

async def find_context(text: str):
    try:
        vector = await get_embedding(text)
        search_result = state.qdrant.query_points(
            collection_name="ground_truth",
            query=vector,
            limit=1
        )
        if search_result and search_result.points:
            return search_result.points[0]
    except Exception as e:
        print("Vector search error:", e)
    return None

async def rewrite_claim(claim: str, context_text: str):
    if not CEREBRAS_API_KEY:
        print("CEREBRAS_API_KEY not set. Skipping rewrite.")
        return claim
    
    prompt = f"""Compare this claim to the provided context. If it is a hallucination, rewrite it to be factually correct using the context. If correct, return the original text. Return ONLY the corrected sentence. Do not include preambles, explanations, or conversational filler.
    
Context: {context_text}
Claim: {claim}"""

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                CEREBRAS_URL,
                headers={"Authorization": f"Bearer {CEREBRAS_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": CEREBRAS_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0
                },
                timeout=10.0
            )
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Cerebras rewrite failed: {e}")
            return claim

async def process_sentence(sentence: str):
    # Detect claims using spacy
    doc = state.nlp(sentence)
    has_claim = any(ent.label_ in {"ORG", "GPE", "DATE", "MONEY", "CARDINAL"} for ent in doc.ents)
    
    if not has_claim:
        return sentence

    # Pause and fact check
    context = await find_context(sentence)
    if not context:
        return sentence
    
    context_text = context.payload.get("text", "")
    source_name = context.payload.get("source", "unknown")
    
    rewritten = await rewrite_claim(sentence, context_text)
    
    # Exact string comparison
    if sentence.strip() != rewritten.strip():
        # Keep punctuation
        # Assuming punctuation is at the end of the original sentence.
        original_punct = sentence[-1] if sentence and sentence[-1] in ".!?" else ""
        rewritten_clean = rewritten.strip()
        if rewritten_clean and rewritten_clean[-1] in ".!?":
            rewritten_clean = rewritten_clean[:-1] # Remove model's punctuation if any
        
        # Preserve trailing spaces in yields
        trailing_spaces_match = re.search(r'(\s+)$', sentence)
        trailing_spaces = trailing_spaces_match.group(1) if trailing_spaces_match else ""
        
        final_text = f'{rewritten_clean}{original_punct}'
        return f'<correction source="{source_name}">{final_text}</correction>{trailing_spaces}'

    return sentence

@router.post("/chat")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        client = httpx.AsyncClient(timeout=120.0)
        buffer = ""
        try:
            async with client.stream("POST", OLLAMA_URL_CHAT, json={"model": PRIMARY_MODEL, "prompt": req.prompt}) as response:
                response.raise_for_status()
                async for chunk in response.aiter_lines():
                    if not chunk: continue
                    try:
                        data = json.loads(chunk)
                        token = data.get("response", "")
                        buffer += token
                        
                        # Sentence detection (very basic)
                        match = re.search(r'(?<=[.!?])\s', buffer)
                        if match:
                            split_idx = match.start() + 1 # Include the space
                            sentence = buffer[:split_idx]
                            buffer = buffer[split_idx:]
                            
                            processed = await process_sentence(sentence)
                            yield f"data: {json.dumps({'text': processed})}\n\n"
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
             yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            if buffer.strip():
                processed = await process_sentence(buffer)
                yield f"data: {json.dumps({'text': processed})}\n\n"
            yield "data: [DONE]\n\n"
            await client.aclose()
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
