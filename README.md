**# Suchi: Advanced Claim Verification & Bytecode Static Analysis Framework**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red.svg)](https://qdrant.tech/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Suchi is an advanced automated claim verification framework that bridges high-throughput natural language processing (NLP) layers with rigorous static analysis of Java bytecode. By executing Reverse Retrieval-Augmented Generation (Reverse RAG), the platform decomposes dense assertions, vectorizes code semantic structures, and performs deterministic static verification against target compiled binaries.

---

## 🏛️ System Architecture & Core Team

### Engineering Leadership
* **Ankit Thakur:** RAG and Bacckend Expert
  * *Responsibilities:* Architected the Reverse RAG processing pipeline, designed the vector database schema, implemented the FastAPI routing layer, and orchestrated the embedding integration pipeline.
* **B.P.S. Rajora** — Static Analysis & Core Research Engineer
  * *Responsibilities:* Designed the Java bytecode parsing engine, handled static analysis control-flow logic, and managed structural rule definitions.

---

## 🎯 System Capabilities

Modern validation systems struggle to reconcile natural language documentation or structural claims with the actual underlying compiled logic. Suchi resolves this disconnect through a dual-engine architecture:

1. **Reverse RAG Engine:** Instead of pulling text documents to answer a prompt, the system ingests natural language claims, isolates verifiable predicates, translates them into semantic vector spaces, and queries cross-referenced codebase components.
2. **Bytecode Static Analysis Layer:** Extracts structural properties, method invocation graphs, and variable states directly from Java bytecode, delivering mathematical certainty where semantic AI models face ambiguity.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **API Framework** | FastAPI | High-performance, asynchronous REST backend engine. |
| **Vector Database** | Qdrant | Distributed, highly available vector search engine for codebase embeddings. |
| **Parsing Layer** | ASM / Native Java Parser | Deep structural static inspection of compiled Java class structures. |
| **NLP Pipeline** | LangChain / Sentence-Transformers | Semantic chunking, claim breakdown, and multi-stage retrieval abstraction. |

---

## 🧠 Core Processing Pipeline

The verification framework operates as a linear pipeline mapping natural language constraints directly to compiled class behaviors:

```text
  [ Input Claim ] 
         │
         ▼
  [ NLP Decomposition Layer ] ──► Extracts Core Assertions & Verifiable Predicates
         │
         ▼
  [ Vector Generation Engine ] ──► Encodes Claims into High-Dimensional Semantic Vectors
         │
         ▼
  [ Qdrant Vector Index ] ───────► Queries Codebase Embeddings for Target Subroutines
         │
         ▼
  [ Static Analysis Engine ] ────► Audits Java Bytecode / Verifies Architectural Constraints
         │
         ▼
  [ Verification Verdict ] ──────► Emits Final Validation Proof (Pass / Fail / Flagged)

📁 Repository Structure
Plaintext
Reverse-RAG-Suchi/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/              # API router implementations
│   │       └── router.py               # Central routing configuration
│   ├── core/
│   │   ├── config.py                   # Global environment and service settings
│   │   └── security.py                 # Authorization and validation utils
│   ├── services/
│   │   ├── rag_engine.py               # Reverse RAG text-to-vector processing logic
│   │   ├── vector_store.py             # Qdrant abstraction layer and index handlers
│   │   └── static_analyzer.py          # Java bytecode decomposition interface
│   └── main.py                         # Application initialization entry point
├── static_core/                        # Compiled Java static analysis components (JARs/Sources)
├── requirements.txt                    # Python environment configuration
└── README.md                           # Documentation
🚀 Installation & Setup
1. Clone the Standalone Repository
Initialize the repository environment locally:


git clone [https://github.com/NeuralImprint/Reverse-RAG-Suchi.git](https://github.com/NeuralImprint/Reverse-RAG-Suchi.git)
cd Reverse-RAG-Suchi
2. Configure Local Environment
Install required dependencies into a virtual environment:


pip install -r requirements.txt
3. Initialize Dependent Infrastructures
Ensure you have a local instance of Qdrant running (e.g., via Docker):


docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
4. Boot the FastAPI Server
Run the asynchronous application server locally:


uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
The interactive API documentation will be available immediately at http://localhost:8000/docs.
