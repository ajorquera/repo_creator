"""Tests for the configuration module."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from repo_creator.config import (
    ConfigError,
    get_default_config,
    load_config,
    save_config,
    validate_config,
)


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_load_yaml_config(self, tmp_path):
        """Test loading a YAML configuration file."""
        config_file = tmp_path / "config.yaml"
        config_data = {"name": "test-repo", "private": True}
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))

        assert result == config_data

    def test_load_json_config(self, tmp_path):
        """Test loading a JSON configuration file."""
        config_file = tmp_path / "config.json"
        config_data = {"name": "test-repo", "private": False}
        config_file.write_text(json.dumps(config_data))

        result = load_config(str(config_file))

        assert result == config_data

    def test_load_config_file_not_found(self):
        """Test that ConfigError is raised for missing file."""
        with pytest.raises(ConfigError, match="not found"):
            load_config("/nonexistent/path/config.yaml")

    def test_load_invalid_yaml(self, tmp_path):
        """Test that ConfigError is raised for invalid YAML."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigError, match="parse"):
            load_config(str(config_file))

    def test_load_config_not_dict(self, tmp_path):
        """Test that ConfigError is raised when config is not a dict."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("- item1\n- item2")

        with pytest.raises(ConfigError, match="must be a dictionary"):
            load_config(str(config_file))


class TestValidateConfig:
    """Tests for the validate_config function."""

    def test_valid_minimal_config(self):
        """Test validation with minimal valid config."""
        config = {"name": "test-repo"}
        validate_config(config)  # Should not raise

    def test_valid_full_config(self):
        """Test validation with full valid config."""
        config = {
            "name": "test-repo",
            "description": "A test repository",
            "private": True,
            "topics": ["python", "testing"],
            "default_branch": "main",
        }
        validate_config(config)  # Should not raise

    def test_missing_name(self):
        """Test that ConfigError is raised when name is missing."""
        config = {"description": "No name"}

        with pytest.raises(ConfigError, match="Missing required field: name"):
            validate_config(config)

    def test_empty_name(self):
        """Test that ConfigError is raised when name is empty."""
        config = {"name": "   "}

        with pytest.raises(ConfigError, match="non-empty string"):
            validate_config(config)

    def test_invalid_private_type(self):
        """Test that ConfigError is raised when private is not boolean."""
        config = {"name": "test-repo", "private": "yes"}

        with pytest.raises(ConfigError, match="'private' must be a boolean"):
            validate_config(config)

    def test_invalid_topics_type(self):
        """Test that ConfigError is raised when topics is not a list."""
        config = {"name": "test-repo", "topics": "python"}

        with pytest.raises(ConfigError, match="'topics' must be a list"):
            validate_config(config)

    def test_invalid_topic_item(self):
        """Test that ConfigError is raised when topic item is not a string."""
        config = {"name": "test-repo", "topics": ["python", 123]}

        with pytest.raises(ConfigError, match="Each topic must be a string"):
            validate_config(config)


class TestGetDefaultConfig:
    """Tests for the get_default_config function."""

    def test_default_config_structure(self):
        """Test that default config has expected structure."""
        config = get_default_config()

        assert "name" in config
        assert "description" in config
        assert "private" in config
        assert isinstance(config["private"], bool)


class TestSaveConfig:
    """Tests for the save_config function."""

    def test_save_yaml_config(self, tmp_path):
        """Test saving a YAML configuration file."""
        config_file = tmp_path / "output.yaml"
        config = {"name": "test-repo", "private": True}

        save_config(config, str(config_file))

        assert config_file.exists()
        loaded = yaml.safe_load(config_file.read_text())
        assert loaded == config

    def test_save_json_config(self, tmp_path):
        """Test saving a JSON configuration file."""
        config_file = tmp_path / "output.json"
        config = {"name": "test-repo", "private": False}

        save_config(config, str(config_file))

        assert config_file.exists()
        loaded = json.loads(config_file.read_text())
        assert loaded == config
