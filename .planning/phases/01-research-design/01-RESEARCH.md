# Phase 1: Research & Design - Research

**Researched:** 2026-05-11
**Domain:** RAG (Retrieval-Augmented Generation) Knowledge Base Integration
**Confidence:** HIGH

## Summary

This research covers the technical decisions required for integrating RAG knowledge base functionality into LiveTalking, a real-time streaming digital human system. The key decisions involve selecting a vector database, embedding model, and document chunking strategy that balance performance, ease of integration, and Chinese language support.

**Primary recommendation:** ChromaDB for vector storage (ease of integration), DashScope Embedding API for consistency with existing LLM stack, and LangChain's RecursiveCharacterTextSplitter with Chinese-optimized separators for document chunking.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Document ingestion | Backend/API | - | One-time processing, CPU-bound |
| Embedding generation | Backend/API | External Service | API calls or local model inference |
| Vector storage | Backend/API | - | Persistent storage layer |
| Semantic retrieval | Backend/API | - | Query-time operation, <500ms requirement |
| Context injection | LLM Module (llm.py) | - | Prompt construction before streaming |
| Configuration | CLI (config.py) | - | User-facing interface |

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TD-1 | Vector Database Selection (ChromaDB/FAISS/Milvus) | Section: Standard Stack - Vector Database |
| TD-2 | Embedding Model Selection (DashScope/OpenAI/text2vec) | Section: Standard Stack - Embedding Models |
| TD-3 | Document Chunking Strategy Selection | Section: Standard Stack - Document Processing |

## Standard Stack

### Core: Vector Database

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| chromadb | 0.5.x+ [VERIFIED: PyPI] | Vector storage and retrieval | Best balance of ease-of-use, performance, and Python integration. Built-in persistence, no external service required. |

**Installation:**
```bash
pip install chromadb
```

**Recommendation rationale:**

ChromaDB is recommended as the primary vector database for this project based on the following analysis:

| Criteria | ChromaDB | FAISS | Milvus |
|----------|----------|-------|--------|
| **Ease of integration** | HIGH - Pure Python, pip install | MEDIUM - Requires index management | LOW - Requires server deployment |
| **Setup complexity** | Minimal - embedded mode | Low - library only | High - server infrastructure |
| **Persistence** | Built-in SQLite/Parquet | Manual serialization | Built-in distributed storage |
| **Memory efficiency** | Good - can page to disk | Excellent - GPU optimized | Good - distributed |
| **Chinese support** | Via embedding model | Via embedding model | Via embedding model |
| **Metadata filtering** | Yes | No (basic) | Yes |
| **Community/Docs** | Active, LangChain integration | Facebook maintainers | Zilliz commercial backing |
| **Best for** | Prototyping to production | Large-scale pure vector search | Enterprise distributed deployments |

**Decision:** ChromaDB wins for this use case because:
1. No external server required (fits LiveTalking's self-contained architecture)
2. Built-in persistence simplifies deployment
3. Native LangChain integration
4. Metadata filtering supports future filtering by document source/type
5. Performance targets (<500ms P95) are achievable with <1M vectors

**Alternatives Considered:**

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ChromaDB | FAISS | Better raw performance at scale, but no built-in metadata filtering or persistence - requires more code |
| ChromaDB | Milvus | Enterprise scalability, but requires server infrastructure - overkill for current scale |

### Core: Embedding Models

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| dashscope (via openai-compatible) | - [ASSUMED: DashScope API] | Embedding API | Consistent with existing LLM setup (DashScope Qwen), no additional authentication |

**Recommended: DashScope Embedding API**

**Comparison:**

| Criteria | DashScope | OpenAI text-embedding-3 | text2vec-base-chinese |
|----------|-----------|-------------------------|----------------------|
| **Chinese quality** | HIGH - optimized for Chinese | MEDIUM - multilingual | HIGH - Chinese-specific |
| **Latency** | LOW - API call, China-based | MEDIUM - API call, may need proxy | VARIABLE - local inference |
| **Cost** | Pay-per-use | Pay-per-use | Free (compute only) |
| **Setup** | Same API key as LLM | Separate API key | Model download + GPU |
| **Dimensions** | 1536 | 1536/3072 | 768 |
| **Consistency with LLM** | HIGH - same provider | LOW | N/A |

**Decision:** DashScope Embedding API is recommended because:
1. Uses same `DASHSCOPE_API_KEY` already configured for LLM
2. Low latency from China-based servers
3. Optimized for Chinese text (primary language for LiveTalking)
4. No additional infrastructure or model management

**Implementation approach:**
```python
# Similar to existing llm.py pattern
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

response = client.embeddings.create(
    model="text-embedding-v2",  # DashScope embedding model
    input=text_chunks
)
```

**Alternatives Considered:**

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| DashScope API | OpenAI text-embedding-3 | Higher quality multilingual, but requires separate API key and may have latency issues from China |
| DashScope API | text2vec-base-chinese | Free and private, but adds GPU memory pressure and model management complexity |

### Core: Document Processing

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| langchain-text-splitters | 0.3.x [VERIFIED: PyPI] | Document chunking | Battle-tested implementations, Chinese-aware splitters |
| langchain-community | 0.3.x [VERIFIED: PyPI] | Document loaders | Unified interface for multiple formats |

**Installation:**
```bash
pip install langchain-text-splitters langchain-community langchain-core
pip install pypdf unstructured markdown
```

**Recommended: RecursiveCharacterTextSplitter with Chinese separators**

**Chunking Strategy Comparison:**

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Fixed size** | Simple, predictable | May cut sentences mid-way | Quick prototyping |
| **Recursive** | Respects sentence/paragraph boundaries | Requires separator tuning | General purpose |
| **Semantic** | Content-aware chunks | Requires embedding model, slower | High-precision retrieval |
| **Sliding window** | Preserves context across boundaries | Creates redundant chunks | Narrative documents |

**Decision:** RecursiveCharacterTextSplitter with Chinese-optimized separators:
- Respects sentence boundaries (no mid-sentence cuts)
- Works without additional embedding calls (unlike semantic chunking)
- Chinese separator priority: `["\n\n", "\n", "。", "！", "？", "；", "，", " "]`
- Configurable chunk size (recommend 500-1000 characters) and overlap (recommend 50-100 characters)

**Example implementation:**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " "],
    length_function=len,
)
```

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pypdf | 4.x | PDF parsing | When PDF documents in knowledge base |
| python-docx | - | Word document parsing | When DOCX files in knowledge base |
| unstructured | - | Multi-format document parsing | Advanced document processing needs |

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Base Pipeline                       │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   PDF/TXT   │    │  Database   │    │  REST API   │
   │   Loader    │    │   Loader    │    │   Loader    │
   └─────────────┘    └─────────────┘    └─────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                    ┌─────────────────┐
                    │ Document Splitter│
                    │ (RecursiveChar)  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Embedding Client│
                    │ (DashScope API) │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   ChromaDB      │
                    │ Vector Store    │
                    └─────────────────┘
                              │
                              │ Query + Top-K
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Integration Layer                         │
└─────────────────────────────────────────────────────────────────┘
                              │
    User Query ──────────────►│
                              ▼
                    ┌─────────────────┐
                    │  RAG Retriever  │
                    │  (similarity)   │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Context Builder │
                    │ (prompt inject) │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   LLM Stream    │◄── Existing llm.py
                    │   (DashScope)   │
                    └─────────────────┘
                              │
                              ▼
                    TTS → Avatar → Output
```

### Recommended Project Structure

```
LiveTalking/
├── rag/                          # RAG module (NEW)
│   ├── __init__.py
│   ├── embeddings.py             # DashScope embedding client
│   ├── vector_store.py           # ChromaDB wrapper
│   ├── document_processor.py     # Chunking and indexing
│   ├── retriever.py              # Similarity search
│   └── loaders/                  # Data source connectors
│       ├── __init__.py
│       ├── file_loader.py        # PDF/TXT/MD/DOCX
│       ├── db_loader.py          # SQLite/MySQL/PostgreSQL
│       └── api_loader.py         # REST API fetcher
├── llm.py                        # MODIFY: add RAG integration
├── config.py                     # MODIFY: add RAG CLI args
└── registry.py                   # EXTEND: add "rag" category
```

### Pattern 1: RAG Context Injection

**What:** Inject retrieved knowledge into LLM prompt before streaming

**When to use:** Chat mode with knowledge base enabled

**Example:**
```python
# Source: [ASSUMED - standard RAG pattern]
def build_rag_prompt(query: str, retrieved_chunks: list[str]) -> str:
    context = "\n\n".join([f"[知识库]: {chunk}" for chunk in retrieved_chunks])
    return f"""你是一个知识助手。根据以下知识库内容回答用户问题。
如果知识库中没有相关信息，请根据你的知识回答，但要说明这是你的理解。

知识库内容:
{context}

用户问题: {query}

请用简短、口语化的方式回答:"""

# Integration point in llm.py
def llm_response_with_rag(message, avatar_session, rag_enabled=False, rag_store=None):
    if rag_enabled and rag_store:
        relevant_chunks = rag_store.query(message, top_k=3)
        enhanced_message = build_rag_prompt(message, relevant_chunks)
    else:
        enhanced_message = message
    # ... existing streaming logic
```

### Pattern 2: Plugin Registration for RAG

**What:** Extend existing registry pattern for RAG components

**Example:**
```python
# Extend registry.py categories
_REGISTRY: Dict[str, Dict[str, Type]] = {
    "stt": {},
    "llm": {},
    "tts": {},
    "avatar": {},
    "output": {},
    "rag": {},          # NEW: RAG retrievers
    "embedding": {},    # NEW: Embedding providers
}

# Usage in rag/__init__.py
from registry import register

@register("rag", "chromadb")
class ChromaDBRetriever: ...
```

### Anti-Patterns to Avoid

- **Anti-pattern:** Blocking the main thread with embedding calls
  - Why it's bad: Embedding API calls can take 100-500ms, blocking real-time streaming
  - What to do instead: Use async or pre-compute embeddings during ingestion

- **Anti-pattern:** Loading entire vector store into memory on each request
  - Why it's bad: ChromaDB loads lazily, but repeatedly creating clients is wasteful
  - What to do instead: Create singleton ChromaDB client at session initialization

- **Anti-pattern:** Large context window injection without truncation
  - Why it's bad: May exceed LLM token limit, waste tokens, slow streaming
  - What to do instead: Limit total context length, use top-k with relevance threshold

- **Anti-pattern:** Re-embedding unchanged documents
  - Why it's bad: Wastes API calls and time
  - What to do instead: Hash document content, check if embedding exists before computing

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vector similarity search | Custom cosine similarity on numpy arrays | ChromaDB | Handles indexing, persistence, metadata filtering |
| PDF text extraction | Custom PDF parser | pypdf or unstructured | Handles encoding, layout, embedded fonts |
| Document chunking | Manual string slicing | langchain-text-splitters | Respects sentence boundaries, configurable overlap |
| Embedding caching | Dictionary with timestamps | ChromaDB built-in persistence | Atomic updates, crash recovery |
| Chinese text segmentation | Split on punctuation | RecursiveCharacterTextSplitter with Chinese separators | Handles edge cases, configurable |

**Key insight:** The RAG ecosystem has mature solutions for all core problems. Focus effort on integration with LiveTalking's streaming architecture, not rebuilding standard RAG components.

## Common Pitfalls

### Pitfall 1: Streaming Incompatibility

**What goes wrong:** RAG retrieval adds latency that breaks the real-time streaming expectation. Users see noticeable delay between input and first audio output.

**Why it happens:** Vector similarity search + embedding API call can add 200-800ms before LLM call even starts.

**How to avoid:**
1. Pre-compute and cache query embeddings for common questions
2. Use async embedding calls (don't block on retrieval)
3. Set aggressive timeout on retrieval (skip if >300ms)
4. Log retrieval latency and alert if P95 > 400ms

**Warning signs:**
- "llm Time to first chunk" exceeds 2 seconds
- Users report "laggy" responses
- Streaming starts mid-sentence

### Pitfall 2: Context Window Overflow

**What goes wrong:** Retrieved chunks + conversation history + system prompt exceed LLM context limit (Qwen-plus: 32K tokens, but practical limit lower for quality).

**Why it happens:** Each retrieved chunk adds tokens; long documents or many chunks quickly consume budget.

**How to avoid:**
1. Limit top-k to 3-5 chunks
2. Truncate chunks to max 500 characters each
3. Implement token counting before LLM call
4. Prioritize recent conversation history over older retrieved chunks

**Warning signs:**
- LLM returns truncated or confused responses
- Token usage warnings in logs
- Responses ignore context

### Pitfall 3: Knowledge Base Staleness

**What goes wrong:** Users ask questions about updated information, but RAG retrieves outdated chunks.

**Why it happens:** Document ingestion is one-time; no update mechanism.

**How to avoid:**
1. Add document timestamp metadata
2. Implement periodic re-ingestion (configurable)
3. Support manual "refresh knowledge base" command
4. Log last update time, warn if > 7 days

**Warning signs:**
- Answers reference outdated information
- Users complain about "old knowledge"
- Document timestamps older than business cycle

### Pitfall 4: Chinese Encoding Issues

**What goes wrong:** PDF/document parsing corrupts Chinese characters, embedding quality suffers, retrieval fails.

**Why it happens:** Mixed encodings (GBK, UTF-8), font embedding, or OCR errors in source documents.

**How to avoid:**
1. Explicitly specify UTF-8 encoding when reading text files
2. Use `unstructured` library for robust PDF parsing
3. Validate embedding quality on sample documents before full ingestion
4. Log and skip documents that fail encoding validation

**Warning signs:**
- Gibberish in retrieved chunks
- Low similarity scores for relevant queries
- Embedding API errors

## Code Examples

### Vector Store Initialization

```python
# Source: [ASSUMED - ChromaDB pattern]
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, persist_dir: str = "./data/chromadb"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: list[str], embeddings: list[list[float]], metadatas: list[dict]):
        ids = [f"doc_{i}_{hash(chunk)}" for i, chunk in enumerate(chunks)]
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
```

### Embedding Client (DashScope)

```python
# Source: [ASSUMED - DashScope API pattern, similar to existing llm.py]
import os
from openai import OpenAI

class DashScopeEmbedding:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "text-embedding-v2"  # DashScope embedding model
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def embed_query(self, query: str) -> list[float]:
        return self.embed([query])[0]
```

### Document Processor

```python
# Source: [ASSUMED - LangChain pattern]
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " "],
            length_function=len,
        )
    
    def process_text(self, text: str, metadata: dict = None) -> list[dict]:
        chunks = self.splitter.split_text(text)
        return [
            {"text": chunk, "metadata": metadata or {}}
            for chunk in chunks
        ]
    
    def process_file(self, file_path: str) -> list[dict]:
        # Detect file type and use appropriate loader
        ext = file_path.lower().split(".")[-1]
        if ext in ("txt", "md"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == "pdf":
            # Use pypdf or unstructured
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() for page in reader.pages])
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        metadata = {"source": file_path, "type": ext}
        return self.process_text(text, metadata)
```

### LLM Integration

```python
# Source: [ASSUMED - integration pattern based on existing llm.py]
def llm_response_with_rag(
    message: str,
    avatar_session: 'BaseAvatar',
    datainfo: dict = {},
    rag_enabled: bool = False,
):
    """Enhanced LLM response with optional RAG context."""
    opt = avatar_session.opt
    
    # Get RAG components from session (if available)
    rag_store = getattr(avatar_session, 'rag_store', None)
    
    if rag_enabled and rag_store:
        # Retrieve relevant context
        query_embedding = rag_store.embedder.embed_query(message)
        results = rag_store.query(query_embedding, top_k=3)
        
        # Build enhanced prompt
        context = "\n\n".join([r["text"] for r in results])
        enhanced_message = f"""根据以下知识库内容回答用户问题。如果知识库中没有相关信息，请根据你的知识回答。

知识库内容:
{context}

用户问题: {message}

请用简短、口语化的方式回答:"""
        prompt = enhanced_message
    else:
        prompt = message
    
    # Existing LLM logic with streaming
    from openai import OpenAI
    import os
    import time
    
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {'role': 'system', 'content': '你是一个知识助手，尽量以简短、口语化的方式输出'},
            {'role': 'user', 'content': prompt}
        ],
        stream=True,
        stream_options={"include_usage": True}
    )
    
    # ... rest of existing streaming logic
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| FAISS as primary vector store | ChromaDB for simplicity | 2023-2024 | Reduced setup complexity, added metadata support |
| OpenAI embeddings default | Multiple providers (DashScope, local models) | 2024 | Better Chinese support, cost optimization |
| Fixed-size chunking | Recursive/semantic chunking | 2023-2024 | Improved retrieval precision |
| Manual prompt engineering | RAG frameworks (LangChain, LlamaIndex) | 2023-2024 | Faster development, standardized patterns |

**Deprecated/outdated:**
- Elasticsearch as primary vector store: ChromaDB/Milvus better for pure vector search
- Sentence-BERT for embeddings: Modern APIs (DashScope, OpenAI) provide better quality per cost

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | DashScope provides embedding API compatible with OpenAI format | Embedding Models | Need to use DashScope SDK directly if not compatible |
| A2 | ChromaDB performance meets <500ms P95 latency for 1M vectors | Vector Database | May need FAISS for larger scale |
| A3 | DashScope embedding model is "text-embedding-v2" | Embedding Models | Model name may differ, need verification |
| A4 | LangChain text splitters support Chinese separators | Document Processing | May need custom implementation |
| A5 | DashScope API key works for both LLM and embedding | Embedding Models | May need separate API key |

## Open Questions

1. **DashScope Embedding Model Name**
   - What we know: DashScope has embedding API
   - What's unclear: Exact model identifier (text-embedding-v2? text-embedding-v1?)
   - Recommendation: Verify via DashScope documentation or API exploration in Wave 0

2. **Vector Store Persistence Location**
   - What we know: ChromaDB supports persistent storage
   - What's unclear: Where to store data relative to project structure
   - Recommendation: Use `./data/chromadb/` (consistent with existing `data/` for models)

3. **Concurrent Session Handling**
   - What we know: LiveTalking supports multiple sessions
   - What's unclear: Whether each session should have isolated knowledge base or share
   - Recommendation: Share single ChromaDB collection across sessions for efficiency; support per-session filtering via metadata

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | YES | 3.10+ | - |
| PyTorch | Existing | YES | 2.5.0 | - |
| openai | DashScope client | YES | installed | - |
| chromadb | Vector store | NO | - | Install required |
| langchain-* | Document processing | NO | - | Install required |
| pypdf | PDF loading | NO | - | Install required |
| DashScope API | Embedding + LLM | ? | - | Need API key verification |

**Missing dependencies with no fallback:**
- chromadb, langchain-text-splitters, langchain-community - Must install via pip

**Missing dependencies with fallback:**
- pypdf - Can skip PDF support initially, add later

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (recommended) |
| Config file | pytest.ini (to be created) |
| Quick run command | `pytest tests/ -x -v --tb=short` |
| Full suite command | `pytest tests/ -v --cov=rag` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TD-1 | Vector database selection validated | unit | `pytest tests/test_vector_store.py -v` | NO - Wave 0 |
| TD-2 | Embedding model integration works | unit | `pytest tests/test_embedding.py -v` | NO - Wave 0 |
| TD-3 | Chunking produces valid segments | unit | `pytest tests/test_chunking.py -v` | NO - Wave 0 |

### Validation Strategy

1. **Wave 0: Verify Technical Decisions**
   - Create proof-of-concept for each decision
   - Verify DashScope embedding API works with existing auth
   - Verify ChromaDB meets latency requirements
   - Verify Chinese text chunking works correctly

2. **Sampling Rate**
   - Per task commit: Quick tests for modified component
   - Per wave merge: Full test suite
   - Phase gate: All tests green + latency benchmark < 500ms P95

### Wave 0 Gaps

- [ ] `tests/test_vector_store.py` - ChromaDB CRUD operations
- [ ] `tests/test_embedding.py` - DashScope embedding client
- [ ] `tests/test_chunking.py` - Document chunking with Chinese
- [ ] `tests/conftest.py` - Shared fixtures (mock DashScope, temp ChromaDB)
- [ ] pytest.ini - Test configuration

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No user auth in scope |
| V3 Session Management | no | Session management exists but not modified |
| V4 Access Control | no | No access control changes |
| V5 Input Validation | yes | Validate document sources, sanitize text before embedding |
| V6 Cryptography | no | Use HTTPS for API calls |

### Known Threat Patterns for RAG Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection via documents | Tampering | Sanitize documents, limit chunk size, validate sources |
| Data exfiltration via queries | Information Disclosure | Log queries, rate limit, audit access patterns |
| Embedding API key exposure | Elevation of Privilege | Use environment variables, never commit keys |
| Document content injection | Tampering | Validate document sources, hash documents for integrity |
| Resource exhaustion (large files) | Denial of Service | Limit file size, timeout on ingestion, queue large jobs |

**Security recommendations:**
1. Never commit DASHSCOPE_API_KEY to git
2. Validate file paths to prevent directory traversal
3. Limit document file size (recommend 10MB max)
4. Sanitize text before embedding (remove potential prompt injection patterns)
5. Log all ingestion and query operations for audit

## Sources

### Primary (HIGH confidence)
- [PyPI] - chromadb package information
- [Project codebase] - llm.py, config.py, registry.py, ARCHITECTURE.md, STACK.md
- [REQUIREMENTS.md] - Phase requirements

### Secondary (MEDIUM confidence)
- [LangChain documentation] - Text splitters, document loaders
- [ChromaDB documentation] - Setup, persistence, query patterns

### Tertiary (LOW confidence)
- [Web search results] - ChromaDB vs FAISS vs Milvus comparisons
- [ASSUMED] - DashScope embedding API details

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - ChromaDB and LangChain are well-documented, but DashScope embedding details need verification
- Architecture: HIGH - Based on existing project architecture analysis
- Pitfalls: HIGH - Common RAG integration challenges well-documented

**Research date:** 2026-05-11
**Valid until:** 2026-06-11 (1 month - RAG stack evolves rapidly)
