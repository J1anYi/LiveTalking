# RAG 模块架构设计

**设计日期:** 2026-05-11
**Phase:** 01-research-design
**状态:** 设计完成

## 概述 (Overview)

RAG（检索增强生成）模块为 LiveTalking 数字人项目提供知识库功能，使数字人在对话时能基于知识库内容回答问题。

**目的:** 通过向量检索为 LLM 提供上下文增强，实现基于知识库的精准回答。

**集成点:** `llm.py` 模块 - 在 LLM 调用前注入检索到的知识上下文。

**依赖:**
| 依赖库 | 版本 | 用途 |
|--------|------|------|
| chromadb | 1.5.9+ | 向量数据库 |
| langchain-text-splitters | 1.1.2+ | 文档分块 |
| openai | 已安装 | DashScope API 客户端 |

## 目录结构 (Directory Structure)

```
rag/
├── __init__.py              # 公共 API 导出和类型定义
├── embeddings.py            # DashScope Embedding 客户端
├── vector_store.py          # ChromaDB 向量存储封装
├── document_processor.py    # 文档分块和索引处理
├── retriever.py             # 相似度检索服务
└── loaders/                 # 数据源连接器
    ├── __init__.py
    ├── file_loader.py       # PDF/TXT/MD/DOCX 文件加载
    ├── db_loader.py         # SQLite/MySQL/PostgreSQL 数据库加载
    └── api_loader.py        # REST API 数据获取
```

## 核心组件 (Core Components)

### 1. DashScopeEmbedding (`embeddings.py`)

**职责:** 调用 DashScope Embedding API 生成文本向量。

**关键方法:**
```python
class DashScopeEmbedding:
    def __init__(self, model: str = "text-embedding-v3") -> None: ...
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, query: str) -> list[float]: ...
```

**依赖:**
- `openai` (OpenAI 客户端模式)
- `os.getenv("DASHSCOPE_API_KEY")`

**线程模型:** 同步调用（API 请求）

**验证结果:**
- 模型: text-embedding-v3
- 向量维度: 1024

---

### 2. VectorStore (`vector_store.py`)

**职责:** 封装 ChromaDB 向量数据库，提供文档存储和检索功能。

**关键方法:**
```python
class VectorStore:
    def __init__(self, persist_dir: str = "./data/chromadb",
                 collection_name: str = "knowledge_base") -> None: ...
    def add(self, chunks: list[str], embeddings: list[list[float]],
            metadatas: list[dict] | None = None) -> None: ...
    def query(self, query_embedding: list[float], top_k: int = 3,
              filter_metadata: dict | None = None) -> list[dict]: ...
    def delete(self, ids: list[str]) -> None: ...
    def count(self) -> int: ...
```

**依赖:**
- `chromadb.PersistentClient`

**线程模型:** 同步调用

**验证结果:**
- ChromaDB 版本: 1.5.9
- Query P50 延迟: 0.59 ms
- Query P95 延迟: 2.2 ms

---

### 3. DocumentProcessor (`document_processor.py`)

**职责:** 文档加载和分块处理。

**关键方法:**
```python
class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100) -> None: ...
    def process_text(self, text: str, metadata: dict | None = None) -> list[dict]: ...
    def process_file(self, file_path: str) -> list[dict]: ...
```

**依赖:**
- `langchain_text_splitters.RecursiveCharacterTextSplitter`

**线程模型:** 同步调用（CPU 密集型）

**验证结果:**
- chunk_size: 800
- chunk_overlap: 100
- 中文分隔符: `["

", "
", "。", "！", "？", "；", "，", " "]`

---

### 4. RAGRetriever (`retriever.py`)

**职责:** 协调 Embedding 和 VectorStore，提供端到端的检索服务。

**关键方法:**
```python
class RAGRetriever:
    def __init__(self, vector_store: VectorStore,
                 embedding_client: DashScopeEmbedding,
                 top_k: int = 3, timeout_ms: int = 300) -> None: ...
    def retrieve(self, query: str) -> list[dict] | None: ...
    def ingest(self, documents: list[dict]) -> None: ...
```

**依赖:**
- `VectorStore`
- `DashScopeEmbedding`

**线程模型:** 同步调用，支持超时

---

### 5. FileLoader (`loaders/file_loader.py`)

**职责:** 从本地文件加载文档。

**支持格式:**
- `.txt` - 纯文本
- `.md` - Markdown
- `.pdf` - PDF 文档 (需要 pypdf)
- `.docx` - Word 文档 (需要 python-docx)

**关键方法:**
```python
class FileLoader:
    def __init__(self, supported_extensions: list[str] | None = None) -> None: ...
    def load(self, file_path: str) -> str: ...
    def load_directory(self, dir_path: str) -> list[tuple[str, dict]]: ...
```

---

### 6. DBLoader (`loaders/db_loader.py`)

**职责:** 从数据库加载文档。

**支持数据库:**
- SQLite
- MySQL
- PostgreSQL

**关键方法:**
```python
class DBLoader:
    def __init__(self, connection_string: str, query: str) -> None: ...
    def load(self) -> list[tuple[str, dict]]: ...
```

---

### 7. APILoader (`loaders/api_loader.py`)

**职责:** 从 REST API 获取文档。

**关键方法:**
```python
class APILoader:
    def __init__(self, endpoint: str, headers: dict | None = None) -> None: ...
    def fetch(self, params: dict | None = None) -> list[tuple[str, dict]]: ...
```

## 集成点 (Integration Points)

### 1. 扩展 registry.py

在现有注册表中添加 "rag" 类别:

```python
# registry.py 修改
_REGISTRY: Dict[str, Dict[str, Type]] = {
    "stt": {},
    "llm": {},
    "tts": {},
    "avatar": {},
    "output": {},
    "rag": {},          # 新增: RAG 检索器
    "embedding": {},    # 新增: Embedding 提供者
}
```

### 2. 修改 llm.py 集成

```python
# llm.py 集成模式
def llm_response(message, avatar_session: BaseAvatar, datainfo: dict = {}):
    # 获取 RAG 组件（如果可用）
    rag_retriever = getattr(avatar_session, "rag_retriever", None)

    if rag_retriever:
        # 检索相关上下文
        context = rag_retriever.retrieve(message)
        if context:
            message = build_rag_prompt(message, context)

    # 现有 LLM 流式调用逻辑...
```

### 3. 配置流程 (config.py)

通过 CLI 参数配置 RAG:

```python
# config.py 新增参数
parser.add_argument("--rag-enabled", action="store_true", default=False)
parser.add_argument("--rag-persist-dir", type=str, default="./data/chromadb")
# ... 更多参数见 CONFIG_DESIGN.md
```

## 数据流 (Data Flow)

文档摄入流程:
  FileLoader/DBLoader/APILoader -> DocumentProcessor -> DashScopeEmbedding -> VectorStore

查询检索流程:
  User Query -> RAGRetriever -> DashScopeEmbedding -> VectorStore -> Context Builder -> LLM Stream

## 线程模型 (Threading Model)

### 文档摄入 (Document Ingestion)
- 执行方式: 后台线程
- 原因: CPU 密集型 + 网络 I/O，可离线执行

### 查询检索 (Query Retrieval)
- 执行方式: 同步调用（在 LLM 线程中）
- 目标: 检索延迟 < 300ms，不影响流式输出

## 错误处理 (Error Handling)

### 优雅降级策略
如果 RAG 失败，回退到直接 LLM 调用。

### 超时处理
- 检索超时: 300ms
- Embedding API 超时: 500ms

## 配置模式 (Configuration Schema)

```yaml
rag:
  enabled: true
  persist_dir: "./data/chromadb"
  collection_name: "knowledge_base"
  embedding:
    model: "text-embedding-v3"
    dimensions: 1024
  chunking:
    chunk_size: 800
    chunk_overlap: 100
  retrieval:
    top_k: 3
    timeout_ms: 300
  knowledge_base:
    path: "./data/knowledge_base"
```

## 性能基准 (Performance Benchmarks)

| 操作 | 目标 | 验证结果 | 状态 |
|------|------|----------|------|
| 向量查询 P50 | < 10ms | 0.59 ms | PASS |
| 向量查询 P95 | < 10ms | 2.2 ms | PASS |
| 总检索延迟 | < 300ms | < 5ms | PASS |

---

*架构设计: 2026-05-11*
