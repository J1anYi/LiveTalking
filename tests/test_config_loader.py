"""Unit tests for RAG config_loader module."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


class TestGetDefaultRagConfig:
    """Tests for get_default_rag_config function."""

    def test_get_default_rag_config_returns_copy(self):
        """Verify returned dict is a copy, not the original."""
        from rag.config_loader import get_default_rag_config, DEFAULT_RAG_CONFIG

        config = get_default_rag_config()

        # Modify the returned config
        config["enabled"] = True
        config["top_k"] = 100

        # Original defaults should be unchanged
        assert DEFAULT_RAG_CONFIG["enabled"] is False
        assert DEFAULT_RAG_CONFIG["top_k"] == 3

    def test_get_default_rag_config_has_required_keys(self):
        """Verify default config contains all required keys."""
        from rag.config_loader import get_default_rag_config

        config = get_default_rag_config()

        assert "enabled" in config
        assert "top_k" in config
        assert "persist_dir" in config
        assert "collection" in config


class TestLoadRagConfig:
    """Tests for load_rag_config function."""

    def test_load_rag_config_returns_defaults_when_file_not_exists(self):
        """File not found returns default config."""
        from rag.config_loader import load_rag_config

        config = load_rag_config("/nonexistent/path/config.yaml")

        assert config["enabled"] is False
        assert config["top_k"] == 3

    def test_load_rag_config_loads_yaml_file(self):
        """Load config from YAML file."""
        from rag.config_loader import load_rag_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "rag_config.yaml")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("""
rag:
  enabled: true
  top_k: 5
  persist_dir: /custom/path
  collection: my_collection
""")

            config = load_rag_config(config_path)

            assert config["enabled"] is True
            assert config["top_k"] == 5
            assert config["persist_dir"] == "/custom/path"
            assert config["collection"] == "my_collection"

    def test_load_rag_config_handles_empty_file(self):
        """Empty file returns default config."""
        from rag.config_loader import load_rag_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "empty.yaml")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("")

            config = load_rag_config(config_path)

            assert config["enabled"] is False
            assert config["top_k"] == 3

    def test_load_rag_config_handles_invalid_yaml(self):
        """Invalid YAML returns default config without raising."""
        from rag.config_loader import load_rag_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "invalid.yaml")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("invalid: yaml: content: [")

            config = load_rag_config(config_path)

            # Should return defaults, not raise
            assert config["enabled"] is False
            assert config["top_k"] == 3


class TestSaveRagConfig:
    """Tests for save_rag_config function."""

    def test_save_rag_config_creates_file(self):
        """Save config creates YAML file."""
        from rag.config_loader import save_rag_config, load_rag_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "saved_config.yaml")

            config = {
                "enabled": True,
                "top_k": 10,
                "persist_dir": "/test/path",
                "collection": "test_collection",
            }

            save_rag_config(config, config_path)

            # Verify file was created
            assert os.path.exists(config_path)

            # Verify content can be loaded back
            loaded = load_rag_config(config_path)
            assert loaded["enabled"] is True
            assert loaded["top_k"] == 10

    def test_save_rag_config_creates_parent_directory(self):
        """Parent directory is created if it doesn't exist."""
        from rag.config_loader import save_rag_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "subdir", "nested", "config.yaml")

            config = {"enabled": True, "top_k": 5}

            save_rag_config(config, config_path)

            assert os.path.exists(config_path)


class TestLoadRagConfigFromEnv:
    """Tests for load_rag_config_from_env function."""

    def test_load_rag_config_from_env_reads_enabled(self, monkeypatch):
        """Read RAG_ENABLED from environment."""
        from rag.config_loader import load_rag_config_from_env

        monkeypatch.setenv("RAG_ENABLED", "true")
        config = load_rag_config_from_env()

        assert config["enabled"] is True

    def test_load_rag_config_from_env_reads_top_k(self, monkeypatch):
        """Read RAG_TOP_K from environment."""
        from rag.config_loader import load_rag_config_from_env

        monkeypatch.setenv("RAG_TOP_K", "5")
        config = load_rag_config_from_env()

        assert config["top_k"] == 5

    def test_load_rag_config_from_env_reads_persist_dir(self, monkeypatch):
        """Read RAG_PERSIST_DIR from environment."""
        from rag.config_loader import load_rag_config_from_env

        monkeypatch.setenv("RAG_PERSIST_DIR", "/custom/path")
        config = load_rag_config_from_env()

        assert config["persist_dir"] == "/custom/path"

    def test_load_rag_config_from_env_returns_empty_when_no_env(self, monkeypatch):
        """No env vars set returns empty dict."""
        from rag.config_loader import load_rag_config_from_env

        # Clear all RAG env vars
        for key in ["RAG_ENABLED", "RAG_TOP_K", "RAG_PERSIST_DIR", "RAG_COLLECTION"]:
            monkeypatch.delenv(key, raising=False)

        config = load_rag_config_from_env()

        assert config == {}


class TestMergeRagConfig:
    """Tests for merge_rag_config function."""

    def test_merge_rag_config_priority_cli_over_env(self, monkeypatch):
        """CLI config overrides environment variables."""
        from rag.config_loader import merge_rag_config, load_rag_config_from_env

        monkeypatch.setenv("RAG_TOP_K", "3")

        cli_config = {"top_k": 10}
        env_config = load_rag_config_from_env()
        file_config = {}

        merged = merge_rag_config(cli_config, env_config, file_config)

        assert merged["top_k"] == 10  # CLI wins

    def test_merge_rag_config_priority_env_over_file(self, monkeypatch):
        """Env config overrides file config."""
        from rag.config_loader import merge_rag_config, load_rag_config_from_env

        monkeypatch.setenv("RAG_TOP_K", "5")

        cli_config = {}
        env_config = load_rag_config_from_env()
        file_config = {"top_k": 3}

        merged = merge_rag_config(cli_config, env_config, file_config)

        assert merged["top_k"] == 5  # Env wins

    def test_merge_rag_config_uses_defaults_for_missing_keys(self):
        """Missing keys use default values."""
        from rag.config_loader import merge_rag_config

        cli_config = {}
        env_config = {}
        file_config = {}

        merged = merge_rag_config(cli_config, env_config, file_config)

        assert merged["enabled"] is False  # Default
        assert merged["top_k"] == 3  # Default
        assert merged["persist_dir"] == "./data/chromadb"  # Default
        assert merged["collection"] == "knowledge_base"  # Default

    def test_merge_rag_config_handles_none_values(self):
        """None values don't override."""
        from rag.config_loader import merge_rag_config

        cli_config = {"top_k": None}
        env_config = {"enabled": None}
        file_config = {"persist_dir": None}

        merged = merge_rag_config(cli_config, env_config, file_config)

        # None values should not override defaults
        assert merged["top_k"] == 3  # Default
        assert merged["enabled"] is False  # Default
        assert merged["persist_dir"] == "./data/chromadb"  # Default
