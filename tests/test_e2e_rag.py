"""End-to-end integration tests for RAG module."""

import pytest
import tempfile
import os
import gc
from unittest.mock import patch, MagicMock


class TestRAGEndToEnd:
    """End-to-end tests for RAG full pipeline."""

    @pytest.mark.integration
    def test_rag_full_pipeline_real_api(self):
        """Test RAG full pipeline with real DashScope API.

        Requires DASHSCOPE_API_KEY environment variable.
        """
        from rag import (
            DashScopeEmbedding,
            VectorStore,
            DocumentProcessor,
            RAGRetriever,
            FileLoader,
            build_rag_prompt,
        )

        # Skip if API key not set
        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not api_key:
            pytest.skip("DASHSCOPE_API_KEY not set, skipping integration test")

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create test document
            doc_path = os.path.join(tmpdir, "test.txt")
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write("RAG 是 Retrieval Augmented Generation 的缩写。")
                f.write("它结合了检索和生成技术，使 LLM 能够基于外部知识库回答问题。")

            # 2. Load document
            loader = FileLoader()
            content, metadata = loader.load(doc_path)

            # 3. Chunk document
            processor = DocumentProcessor(chunk_size=200, chunk_overlap=50)
            chunks = processor.process_text(content, metadata=metadata)

            # 4. Initialize Embedding and VectorStore
            embedding = DashScopeEmbedding(api_key=api_key)
            store = VectorStore(persist_dir=os.path.join(tmpdir, "chromadb"))
            retriever = RAGRetriever(store, embedding, top_k=3)

            # 5. Ingest documents
            count = retriever.ingest(chunks)
            assert count > 0

            # 6. Retrieve
            results = retriever.retrieve("什么是 RAG？")
            assert results is not None
            assert len(results) > 0

            # 7. Build prompt
            prompt = build_rag_prompt("什么是 RAG？", results)
            assert "RAG" in prompt

    def test_rag_full_pipeline_mocked(self):
        """Test RAG full pipeline with mocked API."""
        from rag import (
            DashScopeEmbedding,
            VectorStore,
            DocumentProcessor,
            RAGRetriever,
            FileLoader,
            build_rag_prompt,
        )

        tmpdir = tempfile.mkdtemp()
        try:
            # Create test document
            doc_path = os.path.join(tmpdir, "test.txt")
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write("RAG 是 Retrieval Augmented Generation 的缩写。")

            # Load and process
            loader = FileLoader()
            content, metadata = loader.load(doc_path)

            processor = DocumentProcessor(chunk_size=200, chunk_overlap=50)
            chunks = processor.process_text(content, metadata=metadata)
            assert len(chunks) > 0, "Chunks should not be empty"

            # Initialize with mocked embedding
            embedding = DashScopeEmbedding(api_key="test-key")
            embedding.embed = MagicMock(return_value=[[0.1] * 1024 for _ in range(len(chunks))])
            embedding.embed_query = MagicMock(return_value=[0.1] * 1024)

            store = VectorStore(persist_dir=os.path.join(tmpdir, "chromadb"))
            retriever = RAGRetriever(store, embedding, top_k=3)

            count = retriever.ingest(chunks)
            assert count > 0

            # Retrieve
            results = retriever.retrieve("什么是 RAG？")
            assert results is not None

            # Build prompt
            prompt = build_rag_prompt("什么是 RAG？", results)
            assert "RAG" in prompt
        finally:
            # Clean up ChromaDB connections
            gc.collect()
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_rag_persistence_across_sessions(self):
        """Test that knowledge base persists across sessions."""
        from rag import VectorStore, DashScopeEmbedding, RAGRetriever

        tmpdir = tempfile.mkdtemp()
        try:
            # Session 1: Create knowledge base
            store1 = VectorStore(persist_dir=tmpdir)
            embedding = DashScopeEmbedding(api_key="test-key")
            embedding.embed = MagicMock(return_value=[[0.5] * 1024])
            retriever1 = RAGRetriever(store1, embedding)
            retriever1.ingest([{"text": "测试文档内容", "metadata": {"source": "test"}}])

            count1 = store1.count()
            assert count1 > 0

            # Session 2: Verify persistence
            store2 = VectorStore(persist_dir=tmpdir)
            assert store2.count() == count1
        finally:
            gc.collect()
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_rag_with_filter_metadata(self):
        """Test retrieval with metadata filtering."""
        from rag import VectorStore, DashScopeEmbedding, RAGRetriever

        tmpdir = tempfile.mkdtemp()
        try:
            store = VectorStore(persist_dir=tmpdir)
            embedding = DashScopeEmbedding(api_key="test-key")

            # Mock embeddings for 3 documents
            embedding.embed = MagicMock(return_value=[
                [0.1] * 1024,  # doc1
                [0.2] * 1024,  # doc2
                [0.3] * 1024,  # doc3
            ])
            embedding.embed_query = MagicMock(return_value=[0.1] * 1024)

            retriever = RAGRetriever(store, embedding, top_k=10)

            # Ingest documents with different types
            retriever.ingest([
                {"text": "技术文档", "metadata": {"type": "tech"}},
                {"text": "用户手册", "metadata": {"type": "manual"}},
                {"text": "API 参考", "metadata": {"type": "tech"}},
            ])

            # Retrieve with filter
            results = retriever.retrieve("文档", filter_metadata={"type": "tech"})

            # All results should have type=tech
            for r in results:
                assert r.get("metadata", {}).get("type") == "tech"
        finally:
            gc.collect()
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestLLMIntegration:
    """Tests for LLM and RAG integration."""

    def test_llm_rag_context_injection(self):
        """Test that RAG context is injected into LLM prompt."""
        from rag import build_rag_prompt

        chunks = [
            {"text": "知识库内容：RAG 是检索增强生成。"},
            {"text": "它结合了检索和生成技术。"},
        ]

        prompt = build_rag_prompt("什么是 RAG？", chunks)

        # Verify prompt structure
        assert "知识库内容" in prompt
        assert "什么是 RAG？" in prompt
        assert "KB content" in prompt
        assert "Answer concisely" in prompt

    def test_llm_rag_context_truncation(self):
        """Test that RAG context is truncated when too long."""
        from rag import build_rag_prompt

        # Create chunks that will definitely exceed limit
        chunks = [
            {"text": "X" * 1000},  # First chunk
            {"text": "Y" * 1000},  # Second chunk
            {"text": "Z" * 1000},  # Third chunk - should be truncated
        ]

        # Limit to 2000 chars - should only include first two chunks
        prompt = build_rag_prompt("Query", chunks, max_context_chars=2000)

        # Should include first two chunks
        assert "X" in prompt
        assert "Y" in prompt
        # Third chunk should be truncated (Z character shouldn't appear in KB content)
        # Note: Z might appear in other parts of prompt, so check for the pattern
        assert "[KB]: Z" not in prompt

    def test_llm_disabled_rag_no_retrieval(self):
        """Test that RAG is not called when disabled."""
        from rag import get_default_config

        config = get_default_config()
        assert config["enabled"] is False

    def test_llm_empty_retrieval_handles_gracefully(self):
        """Test graceful handling of empty retrieval results."""
        from rag import build_rag_prompt

        # Empty retrieval
        prompt = build_rag_prompt("问题", [])

        # Should still have query
        assert "问题" in prompt


class TestConfigSystem:
    """Tests for configuration system."""

    def test_config_priority_cli_over_env(self, monkeypatch):
        """Test CLI config overrides environment variables."""
        from rag.config_loader import merge_rag_config, load_rag_config_from_env

        # Set environment variable
        monkeypatch.setenv("RAG_TOP_K", "3")

        # CLI parameter
        cli_config = {"top_k": 10}
        env_config = load_rag_config_from_env()
        file_config = {}

        merged = merge_rag_config(cli_config, env_config, file_config)

        assert merged["top_k"] == 10  # CLI wins

    def test_config_priority_env_over_file(self, monkeypatch):
        """Test env config overrides file config."""
        from rag.config_loader import merge_rag_config, load_rag_config_from_env

        # Set environment variable
        monkeypatch.setenv("RAG_TOP_K", "5")

        cli_config = {}
        env_config = load_rag_config_from_env()
        file_config = {"top_k": 3}

        merged = merge_rag_config(cli_config, env_config, file_config)

        assert merged["top_k"] == 5  # Env wins

    def test_config_yaml_loading(self):
        """Test loading config from YAML file."""
        from rag.config_loader import load_rag_config, save_rag_config

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config file
            config = {"enabled": True, "top_k": 5}
            config_path = os.path.join(tmpdir, "rag_config.yaml")
            save_rag_config(config, config_path)

            # Load config
            loaded = load_rag_config(config_path)

            assert loaded["enabled"] is True
            assert loaded["top_k"] == 5

    def test_config_full_workflow(self, monkeypatch):
        """Test full configuration workflow."""
        from rag.config_loader import (
            load_rag_config,
            save_rag_config,
            load_rag_config_from_env,
            merge_rag_config,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create file config
            file_config = {"enabled": True, "top_k": 3, "collection": "test"}
            config_path = os.path.join(tmpdir, "config.yaml")
            save_rag_config(file_config, config_path)

            # 2. Set environment variables
            monkeypatch.setenv("RAG_TOP_K", "5")

            # 3. CLI override
            cli_config = {"top_k": 10}

            # 4. Merge all
            loaded_file = load_rag_config(config_path)
            env_config = load_rag_config_from_env()
            merged = merge_rag_config(cli_config, env_config, loaded_file)

            # Verify priority: CLI > env > file
            assert merged["top_k"] == 10  # CLI wins
            assert merged["enabled"] is True  # From file
            assert merged["collection"] == "test"  # From file
