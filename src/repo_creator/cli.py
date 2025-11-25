"""Command-line interface for repo-creator."""

import click

from repo_creator import __version__
from repo_creator.config import (
    ConfigError,
    get_default_config,
    load_config,
    save_config,
    validate_config,
)
from repo_creator.github_client import GitHubClient, GitHubError


@click.group()
@click.version_option(version=__version__)
def cli():
    """Create and manage GitHub repositories from configuration files.

    This tool allows you to define repository settings in a YAML or JSON file
    and create or update repositories quickly and consistently.
    """
    pass


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--org",
    "-o",
    help="Organization name (if creating in an organization)",
)
@click.option(
    "--token",
    "-t",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def create(config_file: str, org: str | None, token: str | None, dry_run: bool):
    """Create a new repository from a configuration file.

    CONFIG_FILE is the path to a YAML or JSON configuration file.
    """
    try:
        config = load_config(config_file)
        validate_config(config)
    except ConfigError as e:
        raise click.ClickException(str(e))

    click.echo(f"Creating repository: {config['name']}")

    if dry_run:
        click.echo("Dry run mode - no changes will be made")
        click.echo(f"Configuration: {config}")
        return

    try:
        client = GitHubClient(token)
        user = client.get_authenticated_user()
        owner = org or user["login"]

        if client.repo_exists(owner, config["name"]):
            raise click.ClickException(
                f"Repository {owner}/{config['name']} already exists. "
                "Use 'repo-creator update' to modify it."
            )

        repo = client.create_repo(config, org=org)
        click.echo(f"Created repository: {repo['html_url']}")

        if config.get("topics"):
            client.set_topics(owner, config["name"], config["topics"])
            click.echo(f"Set topics: {', '.join(config['topics'])}")

    except GitHubError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--owner",
    "-o",
    help="Repository owner (defaults to authenticated user)",
)
@click.option(
    "--token",
    "-t",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def update(config_file: str, owner: str | None, token: str | None, dry_run: bool):
    """Update an existing repository from a configuration file.

    CONFIG_FILE is the path to a YAML or JSON configuration file.
    """
    try:
        config = load_config(config_file)
        validate_config(config)
    except ConfigError as e:
        raise click.ClickException(str(e))

    click.echo(f"Updating repository: {config['name']}")

    if dry_run:
        click.echo("Dry run mode - no changes will be made")
        click.echo(f"Configuration: {config}")
        return

    try:
        client = GitHubClient(token)
        user = client.get_authenticated_user()
        repo_owner = owner or user["login"]

        if not client.repo_exists(repo_owner, config["name"]):
            raise click.ClickException(
                f"Repository {repo_owner}/{config['name']} does not exist. "
                "Use 'repo-creator create' to create it first."
            )

        repo = client.update_repo(repo_owner, config["name"], config)
        click.echo(f"Updated repository: {repo['html_url']}")

        if config.get("topics"):
            client.set_topics(repo_owner, config["name"], config["topics"])
            click.echo(f"Set topics: {', '.join(config['topics'])}")

    except GitHubError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("output_file", type=click.Path())
@click.option(
    "--name",
    "-n",
    default="my-repo",
    help="Repository name",
)
@click.option(
    "--description",
    "-d",
    default="",
    help="Repository description",
)
@click.option(
    "--private/--public",
    default=False,
    help="Make the repository private (default: public)",
)
def init(output_file: str, name: str, description: str, private: bool):
    """Initialize a new configuration file with default values.

    OUTPUT_FILE is the path where the configuration file will be saved.
    """
    config = get_default_config()
    config["name"] = name
    if description:
        config["description"] = description
    config["private"] = private

    try:
        save_config(config, output_file)
        click.echo(f"Created configuration file: {output_file}")
        click.echo("Edit the file to customize your repository settings.")
    except ConfigError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file: str):
    """Validate a configuration file.

    CONFIG_FILE is the path to a YAML or JSON configuration file.
    """
    try:
        config = load_config(config_file)
        validate_config(config)
        click.echo(f"Configuration file is valid: {config_file}")
        click.echo(f"Repository name: {config['name']}")
        if config.get("description"):
            click.echo(f"Description: {config['description']}")
        click.echo(f"Private: {config.get('private', False)}")
        if config.get("topics"):
            click.echo(f"Topics: {', '.join(config['topics'])}")
    except ConfigError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("repo_name")
@click.option(
    "--owner",
    "-o",
    help="Repository owner (defaults to authenticated user)",
)
@click.option(
    "--output",
    "-f",
    type=click.Path(),
    help="Output file path (default: <repo_name>.yaml)",
)
@click.option(
    "--token",
    "-t",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
)
def export(repo_name: str, owner: str | None, output: str | None, token: str | None):
    """Export an existing repository's settings to a configuration file.

    REPO_NAME is the name of the repository to export.
    """
    try:
        client = GitHubClient(token)
        user = client.get_authenticated_user()
        repo_owner = owner or user["login"]

        repo = client.get_repo(repo_owner, repo_name)

        config = {
            "name": repo["name"],
            "description": repo.get("description") or "",
            "private": repo["private"],
            "default_branch": repo["default_branch"],
            "has_issues": repo["has_issues"],
            "has_wiki": repo["has_wiki"],
            "has_projects": repo["has_projects"],
        }

        # Get topics
        topics_data = client.get_topics(repo_owner, repo_name)
        if topics_data.get("names"):
            config["topics"] = topics_data["names"]

        output_file = output or f"{repo_name}.yaml"
        save_config(config, output_file)
        click.echo(f"Exported repository configuration to: {output_file}")

    except (GitHubError, ConfigError) as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
