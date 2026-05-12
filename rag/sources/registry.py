"""Data source registry for RAG module.

Provides dynamic registration and loading of data sources.
"""

from typing import TYPE_CHECKING

from .config import SourceConfig

if TYPE_CHECKING:
    from rag.loaders import FileLoader, APILoader, BaseDatabaseConnector


class SourceRegistry:
    """Registry for managing multiple data source loaders.

    Provides dynamic registration and unified loading of documents
    from multiple configured sources.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._loaders: dict[str, "DocumentLoader"] = {}
        self._configs: dict[str, SourceConfig] = {}

    def register(
        self,
        name: str,
        loader: "DocumentLoader",
        config: SourceConfig | None = None,
    ) -> None:
        """Register a data source loader.

        Args:
            name: Unique name for this source
            loader: DocumentLoader instance
            config: Optional SourceConfig for this loader
        """
        self._loaders[name] = loader
        if config:
            self._configs[name] = config

    def unregister(self, name: str) -> None:
        """Unregister a data source.

        Args:
            name: Name of source to unregister
        """
        self._loaders.pop(name, None)
        self._configs.pop(name, None)

    def get(self, name: str) -> "DocumentLoader | None":
        """Get a registered loader by name.

        Args:
            name: Source name

        Returns:
            DocumentLoader instance or None if not found
        """
        return self._loaders.get(name)

    def get_config(self, name: str) -> SourceConfig | None:
        """Get configuration for a registered source.

        Args:
            name: Source name

        Returns:
            SourceConfig or None if not found
        """
        return self._configs.get(name)

    def list_sources(self) -> list[str]:
        """List all registered source names.

        Returns:
            List of source names
        """
        return list(self._loaders.keys())

    def load_all(self) -> list[tuple[str, dict]]:
        """Load documents from all registered sources.

        Returns:
            List of (content, metadata) tuples from all sources
        """
        results = []
        for name, loader in self._loaders.items():
            try:
                docs = loader.load()
                # Add source name to metadata
                for content, metadata in docs:
                    metadata["source_name"] = name
                    results.append((content, metadata))
            except Exception:
                # Skip failed sources
                continue
        return results

    def load_from_source(self, name: str) -> list[tuple[str, dict]]:
        """Load documents from a specific source.

        Args:
            name: Source name

        Returns:
            List of (content, metadata) tuples

        Raises:
            KeyError: If source not registered
        """
        loader = self._loaders.get(name)
        if loader is None:
            raise KeyError(f"Source not registered: {name}")

        docs = loader.load()
        results = []
        for content, metadata in docs:
            metadata["source_name"] = name
            results.append((content, metadata))
        return results


def create_loader_from_config(config: SourceConfig) -> "DocumentLoader":
    """Create a DocumentLoader from SourceConfig.

    Factory function that instantiates the appropriate loader
    based on the source type.

    Args:
        config: Source configuration

    Returns:
        DocumentLoader instance

    Raises:
        ValueError: If source type is not supported
        ImportError: If required dependencies are missing
    """
    source_type = config.type.lower()
    cfg = config.config

    if source_type == "file":
        from rag.loaders import FileLoader

        path = cfg.get("path", ".")
        extensions = cfg.get("extensions", None)
        encoding = cfg.get("encoding", "utf-8")

        loader = FileLoader(
            supported_extensions=extensions,
            encoding=encoding,
        )
        # Store path for later use
        loader._source_path = path
        loader._recursive = cfg.get("recursive", True)
        return loader

    elif source_type == "sqlite":
        from rag.loaders import SQLiteConnector

        connection_string = cfg.get("connection_string", "")
        query = cfg.get("query", "")
        query_params = cfg.get("query_params")
        content_columns = cfg.get("content_columns")
        metadata_columns = cfg.get("metadata_columns")

        return SQLiteConnector(
            connection_string=connection_string,
            query=query,
            query_params=query_params,
            content_columns=content_columns,
            metadata_columns=metadata_columns,
        )

    elif source_type in ("mysql", "postgresql"):
        raise ValueError(
            f"Database type '{source_type}' is not yet implemented. "
            "Only SQLite is currently supported."
        )

    elif source_type == "api":
        from rag.loaders import APILoader

        url = cfg.get("url", "")
        method = cfg.get("method", "GET")
        headers = cfg.get("headers")
        body = cfg.get("body")
        data_path = cfg.get("data_path")
        auth = cfg.get("auth")
        timeout = cfg.get("timeout", 30)

        return APILoader(
            url=url,
            method=method,
            headers=headers,
            body=body,
            data_path=data_path,
            auth=auth,
            timeout=timeout,
        )

    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def setup_registry_from_config(
    config_path: str,
    enabled_only: bool = True,
) -> SourceRegistry:
    """Set up registry from YAML configuration file.

    Convenience function that loads config and creates all loaders.

    Args:
        config_path: Path to YAML configuration file
        enabled_only: If True, only register enabled sources

    Returns:
        Configured SourceRegistry instance
    """
    configs = load_sources_config(config_path)
    registry = SourceRegistry()

    for config in configs:
        # Skip disabled sources if enabled_only
        if enabled_only and not config.enabled:
            continue

        try:
            loader = create_loader_from_config(config)
            registry.register(config.name, loader, config)
        except Exception:
            # Skip sources that fail to initialize
            continue

    return registry
