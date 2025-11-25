"""Tests for the GitHub client module."""

import pytest
from unittest.mock import MagicMock, patch

from repo_creator.github_client import GitHubClient, GitHubError


class TestGitHubClientInit:
    """Tests for GitHubClient initialization."""

    def test_init_with_token(self):
        """Test client initialization with a token."""
        client = GitHubClient(token="test-token")
        assert client.token == "test-token"

    def test_init_with_env_token(self, monkeypatch):
        """Test client initialization with environment variable."""
        monkeypatch.setenv("GITHUB_TOKEN", "env-token")
        client = GitHubClient()
        assert client.token == "env-token"

    def test_init_without_token(self, monkeypatch):
        """Test that GitHubError is raised without token."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with pytest.raises(GitHubError, match="GitHub token is required"):
            GitHubClient()


class TestGitHubClientRequests:
    """Tests for GitHubClient request methods."""

    @pytest.fixture
    def client(self):
        """Create a client with a mock token."""
        return GitHubClient(token="test-token")

    @patch("requests.Session.request")
    def test_get_authenticated_user(self, mock_request, client):
        """Test getting authenticated user."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser", "id": 123}
        mock_request.return_value = mock_response

        result = client.get_authenticated_user()

        assert result["login"] == "testuser"
        mock_request.assert_called_once()

    @patch("requests.Session.request")
    def test_get_repo(self, mock_request, client):
        """Test getting repository information."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "test-repo", "private": False}
        mock_request.return_value = mock_response

        result = client.get_repo("owner", "test-repo")

        assert result["name"] == "test-repo"

    @patch("requests.Session.request")
    def test_repo_exists_true(self, mock_request, client):
        """Test repo_exists returns True when repo exists."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "test-repo"}
        mock_request.return_value = mock_response

        assert client.repo_exists("owner", "test-repo") is True

    @patch("requests.Session.request")
    def test_repo_exists_false(self, mock_request, client):
        """Test repo_exists returns False when repo doesn't exist."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_request.return_value = mock_response

        assert client.repo_exists("owner", "nonexistent") is False

    @patch("requests.Session.request")
    def test_create_repo(self, mock_request, client):
        """Test creating a repository."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "name": "new-repo",
            "html_url": "https://github.com/user/new-repo",
        }
        mock_request.return_value = mock_response

        config = {"name": "new-repo", "description": "A new repo", "private": False}
        result = client.create_repo(config)

        assert result["name"] == "new-repo"
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert "/user/repos" in call_args[0][1]

    @patch("requests.Session.request")
    def test_create_repo_in_org(self, mock_request, client):
        """Test creating a repository in an organization."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"name": "new-repo"}
        mock_request.return_value = mock_response

        config = {"name": "new-repo"}
        client.create_repo(config, org="test-org")

        call_args = mock_request.call_args
        assert "/orgs/test-org/repos" in call_args[0][1]

    @patch("requests.Session.request")
    def test_update_repo(self, mock_request, client):
        """Test updating a repository."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "test-repo", "private": True}
        mock_request.return_value = mock_response

        config = {"private": True, "description": "Updated"}
        result = client.update_repo("owner", "test-repo", config)

        assert result["name"] == "test-repo"
        call_args = mock_request.call_args
        assert call_args[0][0] == "PATCH"

    @patch("requests.Session.request")
    def test_set_topics(self, mock_request, client):
        """Test setting repository topics."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"names": ["python", "cli"]}
        mock_request.return_value = mock_response

        result = client.set_topics("owner", "test-repo", ["python", "cli"])

        assert result["names"] == ["python", "cli"]
        call_args = mock_request.call_args
        assert call_args[0][0] == "PUT"
        assert "topics" in call_args[0][1]

    @patch("requests.Session.request")
    def test_api_error_handling(self, mock_request, client):
        """Test API error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"message": "Forbidden"}
        mock_response.text = "Forbidden"
        mock_request.return_value = mock_response

        with pytest.raises(GitHubError, match="Forbidden"):
            client.get_authenticated_user()
