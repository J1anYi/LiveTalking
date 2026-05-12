# RAG 配置设计

**设计日期:** 2026-05-11
**Phase:** 01-research-design
**状态:** 设计完成

## 概述

本文档定义 RAG 模块的配置接口，包括 CLI 参数、配置文件和环境变量。

## CLI 参数 (CLI Arguments)

在 `config.py` 中添加以下参数：

```python
# === RAG Knowledge Base ===
parser.add_argument('--rag-enabled', action='store_true', default=False,
                    help="Enable RAG knowledge base")
parser.add_argument('--rag-persist-dir', type=str, default='./data/chromadb',
                    help="Directory for vector database persistence")
parser.add_argument('--rag-collection', type=str, default='knowledge_base',
                    help="ChromaDB collection name")
parser.add_argument('--rag-embedding-model', type=str, default='text-embedding-v3',
                    help="DashScope embedding model name")
parser.add_argument('--rag-chunk-size', type=int, default=800,
                    help="Document chunk size in characters")
parser.add_argument('--rag-chunk-overlap', type=int, default=100,
                    help="Chunk overlap in characters")
parser.add_argument('--rag-top-k', type=int, default=3,
                    help="Number of documents to retrieve")
parser.add_argument('--rag-timeout', type=int, default=300,
                    help="Retrieval timeout in milliseconds")
parser.add_argument('--rag-kb-path', type=str, default='./data/knowledge_base',
                    help="Path to knowledge base documents")
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--rag-enabled` | bool | False | 是否启用 RAG |
| `--rag-persist-dir` | str | `./data/chromadb` | ChromaDB 持久化目录 |
| `--rag-collection` | str | `knowledge_base` | ChromaDB 集合名称 |
| `--rag-embedding-model` | str | `text-embedding-v3` | Embedding 模型 |
| `--rag-chunk-size` | int | 800 | 文档块大小 |
| `--rag-chunk-overlap` | int | 100 | 块重叠大小 |
| `--rag-top-k` | int | 3 | 检索数量 |
| `--rag-timeout` | int | 300 | 检索超时(ms) |
| `--rag-kb-path` | str | `./data/knowledge_base` | 知识库路径 |

---

## 配置文件模式 (Configuration File Schema)

YAML 配置文件格式（可选，用于高级配置）：

```yaml
# config.yaml
rag:
  enabled: true
  
  # 向量存储配置
  persist_dir: "./data/chromadb"
  collection_name: "knowledge_base"
  
  # Embedding 配置
  embedding:
    model: "text-embedding-v3"    # 验证结果
    dimensions: 1024              # 验证结果
    api_key_env: "DASHSCOPE_API_KEY"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    timeout: 30.0
  
  # 文档分块配置
  chunking:
    chunk_size: 800               # 验证结果
    chunk_overlap: 100            # 验证结果
    separators:
      - "\n\n"
      - "\n"
      - "。"
      - "！"
      - "？"
      - "；"
      - "，"
      - " "
  
  # 检索配置
  retrieval:
    top_k: 3
    timeout_ms: 300
    min_similarity: 0.0
  
  # 知识库配置
  knowledge_base:
    path: "./data/knowledge_base"
    file_extensions:
      - ".txt"
      - ".md"
      - ".pdf"
    recursive: true
```

---

## 环境变量 (Environment Variables)

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DASHSCOPE_API_KEY` | 是 | - | DashScope API Key |
| `RAG_PERSIST_DIR` | 否 | `./data/chromadb` | 覆盖持久化目录 |
| `RAG_COLLECTION` | 否 | `knowledge_base` | 覆盖集合名称 |
| `RAG_EMBEDDING_MODEL` | 否 | `text-embedding-v3` | 覆盖 Embedding 模型 |

### 设置示例

```bash
# .env 文件
DASHSCOPE_API_KEY=your-api-key-here
RAG_PERSIST_DIR=/custom/path/chromadb
```

---

## 默认值说明 (Default Values Rationale)

| 参数 | 默认值 | 原因 |
|------|--------|------|
| `rag_enabled` | False | 默认禁用，保持向后兼容 |
| `persist_dir` | `./data/chromadb` | 与现有 data/ 目录结构一致 |
| `collection_name` | `knowledge_base` | 语义清晰，通用场景适用 |
| `embedding_model` | `text-embedding-v3` | 验证通过，最新 DashScope 模型 |
| `embedding_dimensions` | 1024 | text-embedding-v3 的实际维度 |
| `chunk_size` | 800 | 平检索精度和 LLM 上下文消耗 |
| `chunk_overlap` | 100 | 约 12.5% 重叠，保持上下文连续性 |
| `top_k` | 3 | 平衡信息量和上下文长度 |
| `timeout_ms` | 300 | 远低于 500ms 目标，留有余量 |

---

## 配置优先级 (Configuration Priority)

配置读取顺序（高到低）：

1. **CLI 参数** - 最高优先级
2. **环境变量** - 次高优先级
3. **配置文件** - YAML/JSON 配置
4. **默认值** - 最低优先级

### 实现示例

```python
def get_rag_config(opt) -> dict:
    """获取 RAG 配置，按优先级合并。"""
    import os
    
    # 1. 从默认值开始
    config = {
        "enabled": False,
        "persist_dir": "./data/chromadb",
        "collection_name": "knowledge_base",
        "embedding_model": "text-embedding-v3",
        "chunk_size": 800,
        "chunk_overlap": 100,
        "top_k": 3,
        "timeout_ms": 300,
        "kb_path": "./data/knowledge_base",
    }
    
    # 2. 从配置文件覆盖（如果存在）
    config_file = load_yaml_config("config.yaml")
    if config_file and "rag" in config_file:
        config = deep_merge(config, config_file["rag"])
    
    # 3. 从环境变量覆盖
    if os.getenv("RAG_PERSIST_DIR"):
        config["persist_dir"] = os.getenv("RAG_PERSIST_DIR")
    if os.getenv("RAG_COLLECTION"):
        config["collection_name"] = os.getenv("RAG_COLLECTION")
    if os.getenv("RAG_EMBEDDING_MODEL"):
        config["embedding_model"] = os.getenv("RAG_EMBEDDING_MODEL")
    
    # 4. 从 CLI 参数覆盖
    if hasattr(opt, "rag_enabled") and opt.rag_enabled:
        config["enabled"] = True
    if hasattr(opt, "rag_persist_dir"):
        config["persist_dir"] = opt.rag_persist_dir
    if hasattr(opt, "rag_collection"):
        config["collection_name"] = opt.rag_collection
    # ... 其他参数
    
    return config
```

---

## 迁移路径 (Migration Path)

### 从无 RAG 到 RAG

**Step 1: 添加 CLI 参数**

```python
# config.py - 添加 RAG 参数（见上方）
```

**Step 2: 修改 llm.py**

```python
# llm.py
def llm_response(message, avatar_session, datainfo={}):
    # 检查 RAG 是否启用
    rag_retriever = getattr(avatar_session, 'rag_retriever', None)
    
    if rag_retriever:
        # 尝试 RAG 检索
        results = rag_retriever.retrieve(message)
        if results:
            message = build_rag_prompt(message, results)
    
    # 现有逻辑...
```

**Step 3: 启动时初始化**

```python
# app.py 或 session_manager.py
def init_rag(opt):
    if not opt.rag_enabled:
        return None
    
    from rag import DashScopeEmbedding, VectorStore, RAGRetriever
    
    embedding = DashScopeEmbedding(model=opt.rag_embedding_model)
    store = VectorStore(
        persist_dir=opt.rag_persist_dir,
        collection_name=opt.rag_collection
    )
    return RAGRetriever(store, embedding, top_k=opt.rag_top_k)
```

### 启用 RAG

```bash
# 方式 1: CLI 参数
python app.py --rag-enabled --rag-kb-path ./docs

# 方式 2: 环境变量 + 启用
export RAG_PERSIST_DIR=/data/chromadb
python app.py --rag-enabled
```

---

## 验证结果引用

以下值来自 `01-VERIFICATION.md`：

| 配置项 | 验证值 | 来源 |
|--------|--------|------|
| Embedding 模型 | text-embedding-v3 | DashScope API 验证 |
| Embedding 维度 | 1024 | API 响应验证 |
| ChromaDB 版本 | 1.5.9 | pip show chromadb |
| chunk_size | 800 | 测试验证 |
| chunk_overlap | 100 | 测试验证 |
| Query P50 | 0.59 ms | 性能测试 |
| Query P95 | 2.2 ms | 性能测试 |

---

*配置设计: 2026-05-11*
