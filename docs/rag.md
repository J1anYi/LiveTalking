# RAG 知识库模块

## 概述

RAG (Retrieval Augmented Generation) 知识库模块为 LiveTalking 数字人提供智能知识检索功能。通过向量检索技术，使数字人在对话时能基于知识库内容回答问题，而非仅依赖通用 LLM 能力。

## 快速开始

### 环境要求

- Python 3.10+
- DASHSCOPE_API_KEY 环境变量（用于 DashScope Embedding API）

### 基本用法

**1. 启用 RAG 功能**

```bash
python app.py --rag_enabled --rag_top_k 3 --model wav2lip --avatar_id wav2lip256_avatar1
```

**2. 使用配置文件**

```bash
# 复制示例配置
cp data/rag_config.yaml.example data/rag_config.yaml

# 编辑配置文件
# ...

# 使用配置文件启动
python app.py --rag_config data/rag_config.yaml --model wav2lip --avatar_id wav2lip256_avatar1
```

### 配置优先级

配置参数按以下优先级合并（高优先级覆盖低优先级）：

```
CLI 参数 > 环境变量 > 配置文件 > 默认值
```

## 安装依赖

```bash
pip install chromadb dashscope pyyaml python-docx
```

## 配置说明

### CLI 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--rag_enabled` | 启用知识库检索 | False |
| `--rag_top_k` | 检索文档数量 | 3 |
| `--rag_persist_dir` | 向量存储路径 | ./data/chromadb |
| `--rag_collection` | 集合名称 | knowledge_base |
| `--rag_config` | 配置文件路径 | data/rag_config.yaml |

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `RAG_ENABLED` | 启用知识库 (true/false/1/0) | `true` |
| `RAG_TOP_K` | 检索数量 | `5` |
| `RAG_PERSIST_DIR` | 存储路径 | `/data/chromadb` |
| `RAG_COLLECTION` | 集合名称 | `my_knowledge` |
| `DASHSCOPE_API_KEY` | DashScope API Key | `sk-xxx` |

### YAML 配置文件

参考 `data/rag_config.yaml.example`：

```yaml
rag:
  enabled: false
  top_k: 3
  persist_dir: ./data/chromadb
  collection: knowledge_base
```

## API 参考

### 核心类

#### RAGRetriever

检索器，管理知识库的索引和检索。

```python
from rag import RAGRetriever, VectorStore, DashScopeEmbedding

# 初始化组件
store = VectorStore(persist_dir="./data/chromadb")
embedding = DashScopeEmbedding(api_key="your-api-key")
retriever = RAGRetriever(store, embedding, top_k=3)

# 检索相关文档
results = retriever.retrieve("什么是 RAG？")

# 索引新文档
retriever.ingest([
    {"text": "文档内容", "metadata": {"source": "file.txt"}}
])

# 获取文档数量
count = retriever.count()

# 清空知识库
retriever.clear()
```

**参数：**
- `vector_store`: VectorStore 实例
- `embedding_client`: Embedding 客户端（实现 EmbeddingClient Protocol）
- `top_k`: 默认检索数量，默认 3

**方法：**
- `retrieve(query, top_k=None, filter_metadata=None)`: 检索相关文档
- `ingest(documents, batch_size=100)`: 索引文档到知识库
- `count()`: 返回文档数量
- `clear()`: 清空知识库

---

#### VectorStore

向量存储，基于 ChromaDB 实现。

```python
from rag import VectorStore

# 初始化
store = VectorStore(persist_dir="./data/chromadb")

# 添加文档
store.add(
    chunks=["文本内容1", "文本内容2"],
    embeddings=[[0.1, ...], [0.2, ...]],
    metadatas=[{"source": "file1"}, {"source": "file2"}]
)

# 查询相似文档
results = store.query(
    query_embedding=[0.1, 0.2, ...],
    top_k=3,
    filter_metadata={"type": "doc"}
)

# 获取文档数量
count = store.count()

# 删除文档
store.delete(ids=["id1", "id2"])

# 清空集合
store.clear()
```

**参数：**
- `persist_dir`: 持久化目录路径
- `collection_name`: 集合名称，默认 "knowledge_base"

---

#### DashScopeEmbedding

Embedding 生成器，使用 DashScope text-embedding-v3 模型。

```python
from rag import DashScopeEmbedding

# 初始化（API Key 从 DASHSCOPE_API_KEY 环境变量读取）
embedding = DashScopeEmbedding()

# 或显式指定 API Key
embedding = DashScopeEmbedding(api_key="sk-your-api-key")

# 批量生成 Embedding
vectors = embedding.embed(["文本1", "文本2"])

# 生成查询 Embedding
query_vector = embedding.embed_query("查询文本")
```

**参数：**
- `api_key`: DashScope API Key（可选，默认从环境变量读取）
- `model`: 模型名称，默认 "text-embedding-v3"
- `dimensions`: 向量维度，默认 1024

---

#### DocumentProcessor

文档处理器，负责文本分块。

```python
from rag import DocumentProcessor

# 初始化
processor = DocumentProcessor(
    chunk_size=800,      # 分块大小
    chunk_overlap=100    # 重叠大小
)

# 处理文本
chunks = processor.process_text(
    "长文本内容...",
    metadata={"source": "document.txt"}
)

# 处理文件
chunks = processor.process_file("document.pdf")
```

**参数：**
- `chunk_size`: 分块大小（字符数），默认 800
- `chunk_overlap`: 分块重叠大小，默认 100

---

### 数据加载器

#### FileLoader

文件加载器，支持 TXT、Markdown、PDF、DOCX 格式。

```python
from rag import FileLoader

loader = FileLoader()

# 加载文件
content, metadata = loader.load("document.pdf")

# 支持的格式
# - .txt: 纯文本
# - .md: Markdown
# - .pdf: PDF 文档
# - .docx: Word 文档
```

---

#### SQLiteConnector

SQLite 数据库连接器。

```python
from rag import SQLiteConnector

connector = SQLiteConnector(
    connection_string="data/knowledge.db",
    query="SELECT title, content FROM articles WHERE published = 1",
    content_columns=["title", "content"],
    metadata_columns=["author", "created_at"]
)

# 加载数据
documents = connector.load()

# 返回格式: [(content, metadata), ...]
```

**参数：**
- `connection_string`: SQLite 数据库文件路径
- `query`: SQL 查询语句
- `content_columns`: 用于构建文档内容的列名列表
- `metadata_columns`: 添加到元数据的列名列表

---

#### APILoader

REST API 数据加载器。

```python
from rag import APILoader

loader = APILoader(
    url="https://api.example.com/knowledge",
    method="GET",
    data_path="$.data[*]",  # JSONPath 提取数据
    content_field="content",
    headers={"X-API-Key": "your-key"}
)

# 加载数据
documents = loader.load()
```

**参数：**
- `url`: API URL
- `method`: HTTP 方法（GET/POST）
- `data_path`: JSONPath 提取数据路径
- `content_field`: 内容字段名
- `headers`: 请求头
- `auth_type`: 认证类型（bearer/api_key/none）

---

### 配置管理

#### load_rag_config

加载 YAML 配置文件。

```python
from rag import load_rag_config

# 加载默认路径
config = load_rag_config()

# 加载指定路径
config = load_rag_config("path/to/config.yaml")
```

---

#### save_rag_config

保存配置到 YAML 文件。

```python
from rag import save_rag_config

config = {"enabled": True, "top_k": 5}
save_rag_config(config, "data/rag_config.yaml")
```

---

#### load_rag_config_from_env

从环境变量加载配置。

```python
from rag import load_rag_config_from_env

env_config = load_rag_config_from_env()
# 返回环境变量中设置的配置项
```

---

#### merge_rag_config

合并配置，按优先级：CLI > 环境变量 > 文件。

```python
from rag import merge_rag_config, load_rag_config_from_env, load_rag_config

merged = merge_rag_config(
    cli_config={"top_k": 5},           # CLI 参数
    env_config=load_rag_config_from_env(),  # 环境变量
    file_config=load_rag_config()      # 文件配置
)
```

---

### 工具函数

#### quick_retrieve

快速检索函数，适用于简单场景。

```python
from rag import quick_retrieve

# 使用默认配置检索
results = quick_retrieve("查询文本", top_k=3)

# 指定配置
results = quick_retrieve(
    query="查询文本",
    top_k=5,
    persist_dir="./data/chromadb",
    api_key="sk-your-api-key"
)
```

---

#### build_rag_prompt

构建 RAG prompt，将检索结果注入到 LLM 提示中。

```python
from rag import build_rag_prompt

retrieved_chunks = [
    {"text": "知识库内容1"},
    {"text": "知识库内容2"},
]

prompt = build_rag_prompt(
    query="用户问题",
    retrieved_chunks=retrieved_chunks,
    max_context_chars=2000  # 最大上下文字符数
)
```

---

#### get_default_config

获取默认配置。

```python
from rag import get_default_config

config = get_default_config()
# 返回完整的默认配置结构
```

---

## 数据源配置

### 多数据源配置 (YAML)

参考 `rag/sources/example_sources.yaml`：

```yaml
sources:
  - name: local_docs
    type: file
    enabled: true
    config:
      path: ./data/knowledge_base
      extensions: [".txt", ".md", ".pdf"]
      recursive: true

  - name: knowledge_db
    type: sqlite
    enabled: true
    config:
      connection_string: ./data/knowledge.db
      query: "SELECT title, content FROM articles"
      content_columns: [title, content]

  - name: remote_api
    type: api
    enabled: false
    config:
      url: https://api.example.com/knowledge
      method: GET
      data_path: $.data[*]
      content_field: content
```

### 加载数据源配置

```python
from rag import load_sources_config, SourceRegistry

# 加载配置
sources = load_sources_config("rag/sources/sources.yaml")

# 创建注册表
registry = SourceRegistry()
registry.register_sources(sources)

# 加载所有数据源
all_documents = registry.load_all()
```

---

## FAQ

### Q: 如何添加新的知识文档？

**A:** 将文档放入 `data/knowledge_base/` 目录，重启应用即可自动加载。支持的格式：TXT、MD、PDF、DOCX。

---

### Q: 检索结果不准确怎么办？

**A:** 尝试以下方法：
1. 增加 `--rag_top_k` 参数提高检索数量
2. 优化文档分块大小（调整 `chunk_size` 和 `chunk_overlap`）
3. 确保知识库内容与查询问题相关

---

### Q: 如何使用自己的 Embedding 模型？

**A:** 实现 `EmbeddingClient` Protocol 接口：

```python
from rag import EmbeddingClient, RAGRetriever

class MyEmbedding:
    def embed(self, texts: list[str]) -> list[list[float]]:
        # 实现批量 Embedding
        ...

    def embed_query(self, query: str) -> list[float]:
        # 实现查询 Embedding
        ...

# 使用自定义 Embedding
retriever = RAGRetriever(store, MyEmbedding())
```

---

### Q: 向量存储占用空间太大？

**A:** ChromaDB 支持增量更新，可以：
1. 定期清理不需要的文档
2. 使用 `retriever.clear()` 清空后重建
3. 删除 `persist_dir` 目录后重新索引

---

### Q: 如何禁用 RAG 功能？

**A:** 有三种方式：
1. 不传递 `--rag_enabled` 参数
2. 在配置文件中设置 `enabled: false`
3. 设置环境变量 `RAG_ENABLED=false`

---

### Q: 支持哪些数据库？

**A:** 目前支持：
- **SQLite**：内置支持，无需额外依赖
- **MySQL/PostgreSQL**：可通过扩展 `BaseDatabaseConnector` 实现

---

### Q: 检索延迟过高怎么办？

**A:** 检查以下方面：
1. 网络延迟（DashScope API 调用）
2. 向量存储位置（使用 SSD）
3. 知识库大小（考虑分多个 collection）

---

## 故障排除

### 常见错误

**1. DASHSCOPE_API_KEY 未设置**

```
错误: DashScope API key not found
```

解决：
```bash
export DASHSCOPE_API_KEY=sk-your-api-key
```

---

**2. ChromaDB 初始化失败**

```
错误: Failed to initialize ChromaDB
```

解决：
- 确保 `persist_dir` 目录有写入权限
- 检查磁盘空间是否充足

---

**3. 文档加载失败**

```
错误: Failed to load document
```

解决：
- 检查文件路径是否正确
- 确认文件编码为 UTF-8
- 验证文件格式是否支持

---

**4. Embedding API 调用失败**

```
错误: DashScope API error
```

解决：
- 验证 API Key 是否有效
- 检查网络连接
- 确认 API 配额是否充足

---

## 性能优化

### 存储优化

- 使用 SSD 存储向量数据库
- 定期清理过期文档
- 对于大规模知识库，考虑分多个 collection

### 检索优化

- 适当增加 `chunk_size` 减少索引数量
- 调整 `top_k` 平衡召回率和性能
- 使用 `filter_metadata` 过滤缩小检索范围

### 网络优化

- 考虑使用本地 Embedding 模型（需自行实现）
- 批量索引时使用较大的 `batch_size`

---

## 版本信息

- **模块版本**: 0.1.0
- **Embedding 模型**: text-embedding-v3
- **Embedding 维度**: 1024
- **ChromaDB 版本**: 1.5.9
