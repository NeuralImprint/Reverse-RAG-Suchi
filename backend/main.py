import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import spacy
from spacy.cli import download
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Load environment variables
load_dotenv()

# Initialize global state
class AppState:
    nlp = None
    qdrant = None

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load spacy model
    try:
        state.nlp = spacy.load("en_core_web_sm")
    except OSError:
        download("en_core_web_sm")
        state.nlp = spacy.load("en_core_web_sm")
    
    # Initialize Qdrant Client (local file storage)
    os.makedirs("./qdrant_storage", exist_ok=True)
    state.qdrant = QdrantClient(path="./qdrant_storage")
    
    # Ensure collection exists
    collection_name = "ground_truth"
    try:
        state.qdrant.get_collection(collection_name)
    except Exception:
        # Create collection if it doesn't exist
        # nomic-embed-text uses 768 dimensions usually
        try:
            state.qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
        except Exception as e:
            print(f"Error creating collection: {e}")
    
    yield
    # Cleanup
    pass

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import upload, chat

@app.get("/")
def read_root():
    return {"status": "Project Suchi backend is running"}

app.include_router(upload.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
