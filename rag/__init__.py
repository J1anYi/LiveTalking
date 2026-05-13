"""RAG module for LiveTalking knowledge base.

Verification results:
    - Embedding model: text-embedding-v3
    - Embedding dimensions: 1024
    - ChromaDB version: 1.5.9
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from avatars.base_avatar import BaseAvatar

# Import implemented classes
from .embeddings import DashScopeEmbedding
from .vector_store import VectorStore
from .document_processor import DocumentProcessor
from .retriever import RAGRetriever
from .loaders import FileLoader, APILoader
from .loaders import BaseDatabaseConnector, SQLiteConnector
from .sources import SourceConfig, SourceRegistry, load_sources_config
from .config_loader import load_rag_config, save_rag_config, get_default_rag_config, load_rag_config_from_env, merge_rag_config


@runtime_checkable
class EmbeddingClient(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, query: str) -> list[float]: ...


@runtime_checkable
class VectorStoreProtocol(Protocol):
    def add(self, chunks: list[str], embeddings: list[list[float]],
            metadatas: list[dict] | None = None) -> None: ...
    def query(self, query_embedding: list[float], top_k: int = 3,
              filter_metadata: dict | None = None) -> list[dict]: ...
    def delete(self, ids: list[str]) -> None: ...
    def count(self) -> int: ...


@runtime_checkable
class DocumentLoader(Protocol):
    def load(self) -> list[tuple[str, dict]]: ...


__all__ = [
    "DashScopeEmbedding", "VectorStore", "DocumentProcessor", "RAGRetriever",
    "FileLoader", "APILoader", "BaseDatabaseConnector", "SQLiteConnector",
    "SourceConfig", "SourceRegistry", "load_sources_config",
    "EmbeddingClient", "VectorStoreProtocol", "DocumentLoader",
    "build_rag_prompt", "quick_retrieve", "get_default_config",
    "load_rag_config", "save_rag_config", "get_default_rag_config", "load_rag_config_from_env", "merge_rag_config",
]


def get_default_config() -> dict:
    return {
        "enabled": False,
        "persist_dir": "./data/chromadb",
        "collection_name": "knowledge_base",
        "embedding": {"model": "text-embedding-v3", "dimensions": 1024},
        "chunking": {"chunk_size": 800, "chunk_overlap": 100},
        "retrieval": {"top_k": 3, "timeout_ms": 300},
        "knowledge_base": {"path": "./data/knowledge_base"},
    }


def build_rag_prompt(query: str, retrieved_chunks: list[dict],
                     max_context_chars: int = 2000) -> str:
    """构建 RAG-only 模式的 prompt（纯知识库回答）"""
    context_parts = []
    total_chars = 0
    for chunk in retrieved_chunks:
        text = chunk.get("text", "")
        if total_chars + len(text) > max_context_chars:
            break
        context_parts.append(f"- {text}")
        total_chars += len(text)
    NL = chr(10)
    context = NL.join(context_parts)
    return f"你是一个知识助手，请根据以下知识库内容回答问题，不要添加知识库以外的内容。{NL}{NL}知识库内容：{NL}{context}{NL}{NL}问题：{query}{NL}{NL}请用简短、口语化的方式回答："


def quick_retrieve(query: str, top_k: int = 3, persist_dir: str = "./data/chromadb",
                   api_key: str | None = None) -> list[dict] | None:
    """Quick retrieval function for simple use cases.

    Args:
        query: Query text
        top_k: Number of results
        persist_dir: Vector store persistence directory
        api_key: DashScope API key (defaults to DASHSCOPE_API_KEY env var)

    Returns:
        Retrieved documents or None
    """
    try:
        store = VectorStore(persist_dir=persist_dir)
        if store.count() == 0:
            return None

        embedding = DashScopeEmbedding(api_key=api_key)
        retriever = RAGRetriever(store, embedding, top_k=top_k)

        return retriever.retrieve(query)
    except Exception:
        return None


__version__ = "0.1.0"
