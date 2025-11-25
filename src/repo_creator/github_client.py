"""GitHub API client for repository management."""

import os
from typing import Any

import requests


class GitHubError(Exception):
    """Exception raised for GitHub API errors."""

    pass


class GitHubClient:
    """Client for interacting with the GitHub API."""

    API_BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        """Initialize the GitHub client.

        Args:
            token: GitHub personal access token. If not provided,
                   will try to read from GITHUB_TOKEN environment variable.

        Raises:
            GitHubError: If no token is available.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise GitHubError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass token as argument."
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any] | list[Any]:
        """Make a request to the GitHub API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            endpoint: API endpoint (without base URL).
            **kwargs: Additional arguments to pass to requests.

        Returns:
            Response data as dictionary or list.

        Raises:
            GitHubError: If the request fails.
        """
        url = f"{self.API_BASE_URL}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as e:
            raise GitHubError(f"Request failed: {e}")

        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except (ValueError, KeyError):
                message = response.text
            raise GitHubError(f"GitHub API error ({response.status_code}): {message}")

        if response.status_code == 204:
            return {}

        try:
            return response.json()
        except ValueError:
            return {}

    def get_authenticated_user(self) -> dict[str, Any]:
        """Get the authenticated user's information.

        Returns:
            Dictionary with user information.
        """
        return self._request("GET", "/user")

    def get_repo(self, owner: str, name: str) -> dict[str, Any]:
        """Get repository information.

        Args:
            owner: Repository owner (username or organization).
            name: Repository name.

        Returns:
            Dictionary with repository information.

        Raises:
            GitHubError: If the repository doesn't exist or can't be accessed.
        """
        return self._request("GET", f"/repos/{owner}/{name}")

    def repo_exists(self, owner: str, name: str) -> bool:
        """Check if a repository exists.

        Args:
            owner: Repository owner.
            name: Repository name.

        Returns:
            True if the repository exists, False otherwise.
        """
        try:
            self.get_repo(owner, name)
            return True
        except GitHubError:
            return False

    def create_repo(self, config: dict[str, Any], org: str | None = None) -> dict[str, Any]:
        """Create a new repository.

        Args:
            config: Repository configuration.
            org: Organization name (if creating in an org).

        Returns:
            Dictionary with created repository information.

        Raises:
            GitHubError: If repository creation fails.
        """
        # Map config to GitHub API fields
        data = {
            "name": config["name"],
            "description": config.get("description", ""),
            "private": config.get("private", False),
            "has_issues": config.get("has_issues", True),
            "has_wiki": config.get("has_wiki", True),
            "has_projects": config.get("has_projects", True),
            "auto_init": config.get("auto_init", False),
        }

        if config.get("default_branch"):
            data["default_branch"] = config["default_branch"]

        endpoint = f"/orgs/{org}/repos" if org else "/user/repos"
        return self._request("POST", endpoint, json=data)

    def update_repo(
        self, owner: str, name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing repository.

        Args:
            owner: Repository owner.
            name: Repository name.
            config: Repository configuration updates.

        Returns:
            Dictionary with updated repository information.

        Raises:
            GitHubError: If repository update fails.
        """
        # Map config to GitHub API fields
        data = {}

        if "description" in config:
            data["description"] = config["description"]
        if "private" in config:
            data["private"] = config["private"]
        if "has_issues" in config:
            data["has_issues"] = config["has_issues"]
        if "has_wiki" in config:
            data["has_wiki"] = config["has_wiki"]
        if "has_projects" in config:
            data["has_projects"] = config["has_projects"]
        if "default_branch" in config:
            data["default_branch"] = config["default_branch"]

        if not data:
            return self.get_repo(owner, name)

        return self._request("PATCH", f"/repos/{owner}/{name}", json=data)

    def set_topics(self, owner: str, name: str, topics: list[str]) -> dict[str, Any]:
        """Set repository topics.

        Args:
            owner: Repository owner.
            name: Repository name.
            topics: List of topic names.

        Returns:
            Dictionary with updated topics.

        Raises:
            GitHubError: If setting topics fails.
        """
        return self._request(
            "PUT",
            f"/repos/{owner}/{name}/topics",
            json={"names": topics},
        )

    def delete_repo(self, owner: str, name: str) -> None:
        """Delete a repository.

        Args:
            owner: Repository owner.
            name: Repository name.

        Raises:
            GitHubError: If repository deletion fails.
        """
        self._request("DELETE", f"/repos/{owner}/{name}")
