# RAG 公共 API 设计

**设计日期:** 2026-05-11
**Phase:** 01-research-design
**状态:** 设计完成

## 概述

本文档定义 RAG 模块的所有公共 API 接口，包括完整的函数签名、参数类型、返回值类型和使用示例。

## 公共 API (Public API)

### 1. DashScopeEmbedding (`embeddings.py`)

DashScope Embedding API 客户端，用于生成文本向量。

```python
class DashScopeEmbedding:
    """DashScope Embedding API 客户端。
    
    使用 OpenAI 兼容模式调用 DashScope Embedding API。
    
    验证结果:
        - 模型: text-embedding-v3
        - 维度: 1024
    """
    
    def __init__(
        self,
        model: str = "text-embedding-v3",
        api_key: str | None = None,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout: float = 30.0,
    ) -> None:
        """初始化 Embedding 客户端。
        
        Args:
            model: Embedding 模型名称，默认 text-embedding-v3
            api_key: DashScope API Key，默认从 DASHSCOPE_API_KEY 环境变量读取
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
            
        Raises:
            ValueError: 如果未提供 api_key 且环境变量未设置
        """
        ...
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """批量生成文本向量。
        
        Args:
            texts: 文本列表，最多 20 个文本
            
        Returns:
            向量列表，每个向量包含 1024 个浮点数
            
        Raises:
            ValueError: 如果 texts 为空或超过 20 个
            RuntimeError: 如果 API 调用失败
            
        Example:
            >>> client = DashScopeEmbedding()
            >>> vectors = client.embed(["文本1", "文本2"])
            >>> len(vectors)  # 2
            >>> len(vectors[0])  # 1024
        """
        ...
    
    def embed_query(self, query: str) -> list[float]:
        """生成单个查询向量。
        
        Args:
            query: 查询文本
            
        Returns:
            查询向量，包含 1024 个浮点数
        """
        ...
    
    @property
    def dimensions(self) -> int:
        """返回向量维度。"""
        return 1024
```

---

### 2. VectorStore (`vector_store.py`)

ChromaDB 向量存储封装，提供文档持久化和相似度检索。

```python
class VectorStore:
    """ChromaDB 向量存储封装。
    
    验证结果:
        - ChromaDB 版本: 1.5.9
        - Query P50: 0.59 ms
        - Query P95: 2.2 ms
    """
    
    def __init__(
        self,
        persist_dir: str = "./data/chromadb",
        collection_name: str = "knowledge_base",
        distance_metric: str = "cosine",
    ) -> None:
        """初始化向量存储。
        
        Args:
            persist_dir: 持久化目录
            collection_name: 集合名称
            distance_metric: 距离度量，可选 "cosine", "l2", "ip"
        """
        ...
    
    def add(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """添加文档到向量存储。
        
        Args:
            chunks: 文档块列表
            embeddings: 对应的向量列表（1024 维）
            metadatas: 元数据列表，每个元素可包含 source, page, type 等
            ids: 文档 ID 列表，如不提供则自动生成
            
        Returns:
            添加的文档 ID 列表
        """
        ...
    
    def query(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        filter_metadata: dict | None = None,
    ) -> list[dict]:
        """查询相似文档。
        
        Args:
            query_embedding: 查询向量（1024 维）
            top_k: 返回的最相似文档数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            文档列表，按相似度降序排列，每个文档包含:
            - "text": str - 文档文本
            - "metadata": dict - 元数据
            - "distance": float - 距离（越小越相似）
        """
        ...
    
    def delete(self, ids: list[str]) -> None:
        """删除指定文档。"""
        ...
    
    def count(self) -> int:
        """返回文档总数。"""
        ...
```

---

### 3. DocumentProcessor (`document_processor.py`)

文档加载和分块处理器。

```python
class DocumentProcessor:
    """文档加载和分块处理器。
    
    验证结果:
        - chunk_size: 800
        - chunk_overlap: 100
    """
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        separators: list[str] | None = None,
    ) -> None:
        """初始化处理器。
        
        Args:
            chunk_size: 块大小（字符数）
            chunk_overlap: 块重叠（字符数）
            separators: 分隔符列表，默认为中文优化分隔符
        """
        ...
    
    def process_text(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[dict]:
        """分割文本为块。
        
        Returns:
            块列表，每个块包含: {"text": str, "metadata": dict}
        """
        ...
    
    def process_file(self, file_path: str) -> list[dict]:
        """加载并分割文件。
        
        支持格式: .txt, .md, .pdf, .docx
        """
        ...
```

---

### 4. RAGRetriever (`retriever.py`)

端到端 RAG 检索服务。

```python
class RAGRetriever:
    """RAG 检索服务。"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_client: DashScopeEmbedding,
        top_k: int = 3,
        timeout_ms: int = 300,
        min_similarity: float = 0.0,
    ) -> None:
        """初始化检索器。"""
        ...
    
    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter_metadata: dict | None = None,
    ) -> list[dict] | None:
        """检索相关文档。
        
        Returns:
            检索结果列表，或 None（如果超时或出错）
        """
        ...
    
    def ingest(
        self,
        documents: list[dict],
        batch_size: int = 20,
    ) -> int:
        """摄入文档到知识库。
        
        Returns:
            添加的文档数量
        """
        ...
```

---

### 5. FileLoader (`loaders/file_loader.py`)

```python
class FileLoader:
    """本地文件加载器。"""
    
    def __init__(
        self,
        supported_extensions: list[str] | None = None,
        encoding: str = "utf-8",
    ) -> None:
        """初始化文件加载器。"""
        ...
    
    def load(self, file_path: str) -> tuple[str, dict]:
        """加载单个文件。"""
        ...
    
    def load_directory(
        self,
        dir_path: str,
        recursive: bool = True,
    ) -> list[tuple[str, dict]]:
        """加载目录中的所有文件。"""
        ...
```

## LLM 集成 API

### build_rag_prompt

```python
def build_rag_prompt(
    query: str,
    retrieved_chunks: list[dict],
    max_context_chars: int = 2000,
    system_prompt: str | None = None,
) -> str:
    """构建 RAG 增强提示。
    
    Example:
        >>> chunks = retriever.retrieve("用户问题")
        >>> prompt = build_rag_prompt("用户问题", chunks)
    """
    ...
```

### llm_response_with_rag

```python
def llm_response_with_rag(
    message: str,
    avatar_session: "BaseAvatar",
    datainfo: dict = {},
    rag_retriever: RAGRetriever | None = None,
    rag_enabled: bool = True,
) -> None:
    """LLM 响应，可选使用 RAG 上下文。"""
    ...
```

## 集成示例

```python
# 1. 初始化组件
from rag import DashScopeEmbedding, VectorStore, RAGRetriever, build_rag_prompt

embedding = DashScopeEmbedding(model="text-embedding-v3")
store = VectorStore(persist_dir="./data/chromadb")
retriever = RAGRetriever(store, embedding, top_k=3)

# 2. 摄入文档
retriever.ingest([{"text": "RAG 是检索增强生成..."}])

# 3. 查询检索
results = retriever.retrieve("什么是 RAG?")

# 4. 构建 LLM 提示
if results:
    prompt = build_rag_prompt("什么是 RAG?", results)
```

## 错误处理

| 错误类型 | 触发条件 | 处理策略 |
|----------|----------|----------|
| `ValueError` | 参数无效 | 抛出异常 |
| `RuntimeError` | API 调用失败 | 记录日志，返回 None |
| `TimeoutError` | 操作超时 | 记录警告，返回 None |

---

*API 设计: 2026-05-11*
