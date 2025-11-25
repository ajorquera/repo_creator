"""Configuration file handling for repo-creator."""

import json
import os
from pathlib import Path
from typing import Any

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


def load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from a YAML or JSON file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Dictionary containing the configuration.

    Raises:
        ConfigError: If the file cannot be read or parsed.
    """
    path = Path(config_path)

    if not path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        content = path.read_text()
    except OSError as e:
        raise ConfigError(f"Failed to read configuration file: {e}")

    suffix = path.suffix.lower()
    try:
        if suffix in (".yaml", ".yml"):
            config = yaml.safe_load(content)
        elif suffix == ".json":
            config = json.loads(content)
        else:
            # Try YAML first, then JSON
            try:
                config = yaml.safe_load(content)
            except yaml.YAMLError:
                config = json.loads(content)
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ConfigError(f"Failed to parse configuration file: {e}")

    if not isinstance(config, dict):
        raise ConfigError("Configuration must be a dictionary")

    return config


def validate_config(config: dict[str, Any]) -> None:
    """Validate the configuration structure.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ConfigError: If the configuration is invalid.
    """
    required_fields = ["name"]

    for field in required_fields:
        if field not in config:
            raise ConfigError(f"Missing required field: {field}")

    if not isinstance(config.get("name"), str) or not config["name"].strip():
        raise ConfigError("Repository name must be a non-empty string")

    # Validate optional fields
    if "private" in config and not isinstance(config["private"], bool):
        raise ConfigError("'private' must be a boolean")

    if "description" in config and not isinstance(config["description"], str):
        raise ConfigError("'description' must be a string")

    if "topics" in config:
        if not isinstance(config["topics"], list):
            raise ConfigError("'topics' must be a list")
        for topic in config["topics"]:
            if not isinstance(topic, str):
                raise ConfigError("Each topic must be a string")

    if "default_branch" in config and not isinstance(config["default_branch"], str):
        raise ConfigError("'default_branch' must be a string")


def get_default_config() -> dict[str, Any]:
    """Return a default configuration template.

    Returns:
        Dictionary with default configuration values.
    """
    return {
        "name": "my-repo",
        "description": "Repository created by repo-creator",
        "private": False,
        "topics": [],
        "default_branch": "main",
        "has_issues": True,
        "has_wiki": True,
        "has_projects": True,
        "auto_init": True,
    }


def save_config(config: dict[str, Any], config_path: str) -> None:
    """Save configuration to a file.

    Args:
        config: Configuration dictionary to save.
        config_path: Path to save the configuration file.

    Raises:
        ConfigError: If the file cannot be written.
    """
    path = Path(config_path)

    try:
        suffix = path.suffix.lower()
        if suffix == ".json":
            content = json.dumps(config, indent=2)
        else:
            content = yaml.dump(config, default_flow_style=False, sort_keys=False)

        path.write_text(content)
    except OSError as e:
        raise ConfigError(f"Failed to write configuration file: {e}")
