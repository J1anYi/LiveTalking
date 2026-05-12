"""Data source management for RAG module.

Provides configuration and registry for multiple data sources.
"""

from .config import SourceConfig, load_sources_config, save_sources_config
from .registry import SourceRegistry, create_loader_from_config, setup_registry_from_config

__all__ = [
    "SourceConfig",
    "load_sources_config",
    "save_sources_config",
    "SourceRegistry",
    "create_loader_from_config",
    "setup_registry_from_config",
]
