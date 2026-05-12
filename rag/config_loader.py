"""RAG Configuration Loader for LiveTalking.

Provides YAML-based configuration loading for RAG knowledge base settings.
Supports environment variable override and configuration file management.
"""

import os
from pathlib import Path
from typing import Any

import yaml

from utils.logger import logger


# Default RAG configuration values
DEFAULT_RAG_CONFIG: dict[str, Any] = {
    "enabled": False,
    "top_k": 3,
    "persist_dir": "./data/chromadb",
    "collection": "knowledge_base",
}


def get_default_rag_config() -> dict[str, Any]:
    """Return a copy of the default RAG configuration.

    Returns:
        Dictionary with default configuration values.
    """
    return DEFAULT_RAG_CONFIG.copy()


def load_rag_config(filepath: str | None = None) -> dict[str, Any]:
    """Load RAG configuration from a YAML file.

    Args:
        filepath: Path to the YAML configuration file.
                  Defaults to "data/rag_config.yaml".

    Returns:
        Merged configuration dictionary (defaults + file values).
        Returns empty dict merge if file doesn't exist.
    """
    if filepath is None:
        filepath = "data/rag_config.yaml"

    config = get_default_rag_config()

    path = Path(filepath)
    if not path.exists():
        logger.debug(f"RAG config file not found: {filepath}, using defaults")
        return config

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            logger.debug(f"RAG config file is empty: {filepath}")
            return config

        # Extract "rag:" section if present
        rag_section = data.get("rag", data)

        if isinstance(rag_section, dict):
            # Merge with defaults (file values override defaults)
            config.update(rag_section)
            logger.info(f"Loaded RAG config from {filepath}")

        return config

    except yaml.YAMLError as e:
        logger.warning(f"Failed to parse RAG config file: {e}")
        return config
    except Exception as e:
        logger.warning(f"Failed to load RAG config file: {e}")
        return config


def save_rag_config(config: dict[str, Any], filepath: str) -> None:
    """Save RAG configuration to a YAML file.

    Args:
        config: Configuration dictionary to save.
        filepath: Path to the output YAML file.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump({"rag": config}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logger.info(f"Saved RAG config to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save RAG config: {e}")
        raise


def load_rag_config_from_env() -> dict[str, Any]:
    """Load RAG configuration from environment variables.

    Environment variables:
        RAG_ENABLED: "true", "1", "yes" → True; "false", "0", "no" → False
        RAG_TOP_K: Integer value for top_k
        RAG_PERSIST_DIR: String path for persist directory
        RAG_COLLECTION: String collection name

    Returns:
        Dict with only the environment variables that are set.
    """
    config: dict[str, Any] = {}

    # RAG_ENABLED - boolean conversion
    enabled = os.environ.get("RAG_ENABLED")
    if enabled is not None:
        config["enabled"] = enabled.lower() in ("true", "1", "yes")

    # RAG_TOP_K - integer conversion
    top_k = os.environ.get("RAG_TOP_K")
    if top_k is not None:
        try:
            config["top_k"] = int(top_k)
        except ValueError:
            logger.warning(f"Invalid RAG_TOP_K value: {top_k}, ignoring")

    # RAG_PERSIST_DIR - string
    persist_dir = os.environ.get("RAG_PERSIST_DIR")
    if persist_dir is not None:
        config["persist_dir"] = persist_dir.strip()

    # RAG_COLLECTION - string
    collection = os.environ.get("RAG_COLLECTION")
    if collection is not None:
        config["collection"] = collection.strip()

    return config


def merge_rag_config(cli_config: dict[str, Any], env_config: dict[str, Any], file_config: dict[str, Any]) -> dict[str, Any]:
    """Merge RAG configuration with priority: CLI > env > file.

    Args:
        cli_config: Configuration from CLI arguments
        env_config: Configuration from environment variables
        file_config: Configuration from YAML file

    Returns:
        Merged configuration dict
    """
    # Start with defaults
    result = get_default_rag_config()

    # Apply file config (lowest priority)
    for key, value in file_config.items():
        if value is not None:
            result[key] = value

    # Apply env config (medium priority)
    for key, value in env_config.items():
        if value is not None:
            result[key] = value

    # Apply CLI config (highest priority)
    for key, value in cli_config.items():
        if value is not None:
            result[key] = value

    return result
