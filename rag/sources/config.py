"""Data source configuration for RAG module.

Provides YAML-based configuration management for multiple data sources.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceConfig:
    """Configuration for a single data source.

    Attributes:
        name: Unique identifier for this data source
        type: Loader type (file, sqlite, mysql, postgresql, api)
        enabled: Whether this source is active
        config: Type-specific configuration parameters
    """

    name: str
    type: str
    enabled: bool = True
    config: dict = field(default_factory=dict)


def _expand_env_vars(value: str) -> str:
    """Expand environment variables in a string.

    Supports ${VAR_NAME} and $VAR_NAME syntax.

    Args:
        value: String potentially containing env var references

    Returns:
        String with env vars expanded
    """
    # Pattern for ${VAR_NAME} syntax
    pattern = r"\$\{([^}]+)\}"

    def replace_var(match: re.Match) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    result = re.sub(pattern, replace_var, value)

    # Also handle $VAR_NAME syntax (without braces)
    # But be careful not to match already processed ${...}
    simple_pattern = r"\$([A-Za-z_][A-Za-z0-9_]*)"
    result = re.sub(simple_pattern, lambda m: os.environ.get(m.group(1), m.group(0)), result)

    return result


def _expand_config_env_vars(config: dict) -> dict:
    """Recursively expand environment variables in config dict.

    Args:
        config: Configuration dictionary

    Returns:
        New dict with env vars expanded in string values
    """
    result = {}
    for key, value in config.items():
        if isinstance(value, str):
            result[key] = _expand_env_vars(value)
        elif isinstance(value, dict):
            result[key] = _expand_config_env_vars(value)
        elif isinstance(value, list):
            result[key] = [
                _expand_env_vars(item) if isinstance(item, str)
                else _expand_config_env_vars(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def load_sources_config(path: str) -> list[SourceConfig]:
    """Load data source configurations from YAML file.

    Args:
        path: Path to YAML configuration file

    Returns:
        List of SourceConfig objects

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config file is invalid
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for configuration support. "
            "Install it with: pip install pyyaml"
        )

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    # Load YAML
    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    if not raw_config:
        return []

    # Get sources list
    sources_data = raw_config.get("sources", [])
    if not sources_data:
        return []

    # Parse each source
    configs = []
    for source_data in sources_data:
        # Validate required fields
        if "name" not in source_data:
            raise ValueError("Source configuration missing 'name' field")
        if "type" not in source_data:
            raise ValueError(f"Source '{source_data['name']}' missing 'type' field")

        # Expand env vars in config section
        expanded_config = _expand_config_env_vars(source_data.get("config", {}))

        source_config = SourceConfig(
            name=source_data["name"],
            type=source_data["type"],
            enabled=source_data.get("enabled", True),
            config=expanded_config,
        )
        configs.append(source_config)

    return configs


def save_sources_config(configs: list[SourceConfig], path: str) -> None:
    """Save data source configurations to YAML file.

    Args:
        configs: List of SourceConfig objects
        path: Path to output YAML file
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for configuration support. "
            "Install it with: pip install pyyaml"
        )

    sources_data = []
    for config in configs:
        sources_data.append({
            "name": config.name,
            "type": config.type,
            "enabled": config.enabled,
            "config": config.config,
        })

    output = {"sources": sources_data}

    # Ensure parent directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
