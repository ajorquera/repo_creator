"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from click.testing import CliRunner

from repo_creator.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample configuration file."""
    config_file = tmp_path / "config.yaml"
    config = {
        "name": "test-repo",
        "description": "A test repository",
        "private": False,
        "topics": ["python", "testing"],
    }
    config_file.write_text(yaml.dump(config))
    return str(config_file)


class TestCliHelp:
    """Tests for CLI help commands."""

    def test_cli_help(self, runner):
        """Test that help command works."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Create and manage GitHub repositories" in result.output

    def test_create_help(self, runner):
        """Test that create command help works."""
        result = runner.invoke(cli, ["create", "--help"])

        assert result.exit_code == 0
        assert "Create a new repository" in result.output

    def test_update_help(self, runner):
        """Test that update command help works."""
        result = runner.invoke(cli, ["update", "--help"])

        assert result.exit_code == 0
        assert "Update an existing repository" in result.output

    def test_init_help(self, runner):
        """Test that init command help works."""
        result = runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "Initialize a new configuration file" in result.output

    def test_validate_help(self, runner):
        """Test that validate command help works."""
        result = runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0
        assert "Validate a configuration file" in result.output


class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_yaml_file(self, runner, tmp_path):
        """Test that init creates a YAML file."""
        output_file = tmp_path / "new-config.yaml"

        result = runner.invoke(cli, ["init", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        config = yaml.safe_load(output_file.read_text())
        assert "name" in config

    def test_init_with_options(self, runner, tmp_path):
        """Test init with custom options."""
        output_file = tmp_path / "custom-config.yaml"

        result = runner.invoke(
            cli,
            [
                "init",
                str(output_file),
                "--name",
                "custom-repo",
                "--description",
                "Custom description",
                "--private",
            ],
        )

        assert result.exit_code == 0
        config = yaml.safe_load(output_file.read_text())
        assert config["name"] == "custom-repo"
        assert config["description"] == "Custom description"
        assert config["private"] is True


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_valid_config(self, runner, sample_config):
        """Test validating a valid configuration."""
        result = runner.invoke(cli, ["validate", sample_config])

        assert result.exit_code == 0
        assert "Configuration file is valid" in result.output

    def test_validate_invalid_config(self, runner, tmp_path):
        """Test validating an invalid configuration."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text(yaml.dump({"description": "No name"}))

        result = runner.invoke(cli, ["validate", str(config_file)])

        assert result.exit_code != 0
        assert "Missing required field" in result.output


class TestCreateCommand:
    """Tests for the create command."""

    def test_create_dry_run(self, runner, sample_config):
        """Test create with dry-run flag."""
        result = runner.invoke(cli, ["create", sample_config, "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert "test-repo" in result.output

    @patch("repo_creator.cli.GitHubClient")
    def test_create_success(self, mock_client_class, runner, sample_config):
        """Test successful repository creation."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_authenticated_user.return_value = {"login": "testuser"}
        mock_client.repo_exists.return_value = False
        mock_client.create_repo.return_value = {
            "html_url": "https://github.com/testuser/test-repo"
        }

        result = runner.invoke(
            cli, ["create", sample_config, "--token", "fake-token"]
        )

        assert result.exit_code == 0
        assert "Created repository" in result.output
        mock_client.create_repo.assert_called_once()

    @patch("repo_creator.cli.GitHubClient")
    def test_create_repo_exists(self, mock_client_class, runner, sample_config):
        """Test create when repository already exists."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_authenticated_user.return_value = {"login": "testuser"}
        mock_client.repo_exists.return_value = True

        result = runner.invoke(
            cli, ["create", sample_config, "--token", "fake-token"]
        )

        assert result.exit_code != 0
        assert "already exists" in result.output


class TestUpdateCommand:
    """Tests for the update command."""

    def test_update_dry_run(self, runner, sample_config):
        """Test update with dry-run flag."""
        result = runner.invoke(cli, ["update", sample_config, "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    @patch("repo_creator.cli.GitHubClient")
    def test_update_success(self, mock_client_class, runner, sample_config):
        """Test successful repository update."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_authenticated_user.return_value = {"login": "testuser"}
        mock_client.repo_exists.return_value = True
        mock_client.update_repo.return_value = {
            "html_url": "https://github.com/testuser/test-repo"
        }

        result = runner.invoke(
            cli, ["update", sample_config, "--token", "fake-token"]
        )

        assert result.exit_code == 0
        assert "Updated repository" in result.output
        mock_client.update_repo.assert_called_once()

    @patch("repo_creator.cli.GitHubClient")
    def test_update_repo_not_exists(self, mock_client_class, runner, sample_config):
        """Test update when repository doesn't exist."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_authenticated_user.return_value = {"login": "testuser"}
        mock_client.repo_exists.return_value = False

        result = runner.invoke(
            cli, ["update", sample_config, "--token", "fake-token"]
        )

        assert result.exit_code != 0
        assert "does not exist" in result.output
