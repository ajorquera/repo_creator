# Repo Creator

Create and manage GitHub repositories from configuration files. Define your repository settings once and create or update repos in seconds.

## Features

- 📄 Create repositories from YAML or JSON configuration files
- 🔄 Update existing repositories with new settings
- 📤 Export existing repository settings to configuration files
- ✅ Validate configuration files before applying changes
- 🏢 Support for personal and organization repositories
- 🧪 Dry-run mode to preview changes

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize a configuration file

```bash
repo-creator init my-repo.yaml --name my-awesome-repo --description "My project" --private
```

This creates a configuration file with default values:

```yaml
name: my-awesome-repo
description: My project
private: true
topics: []
default_branch: main
has_issues: true
has_wiki: true
has_projects: true
auto_init: true
```

### 2. Create a repository

Set your GitHub token:

```bash
export GITHUB_TOKEN=your_github_token
```

Then create the repository:

```bash
repo-creator create my-repo.yaml
```

Use `--dry-run` to preview changes without creating the repository:

```bash
repo-creator create my-repo.yaml --dry-run
```

### 3. Update an existing repository

Modify your configuration file and apply changes:

```bash
repo-creator update my-repo.yaml
```

### 4. Export existing repository settings

Export settings from an existing repository:

```bash
repo-creator export my-existing-repo --output config.yaml
```

## CLI Commands

### `repo-creator init`

Initialize a new configuration file with default values.

```bash
repo-creator init OUTPUT_FILE [OPTIONS]

Options:
  -n, --name TEXT        Repository name
  -d, --description TEXT Repository description
  --private / --public   Make the repository private (default: public)
```

### `repo-creator create`

Create a new repository from a configuration file.

```bash
repo-creator create CONFIG_FILE [OPTIONS]

Options:
  -o, --org TEXT   Organization name (for org repositories)
  -t, --token TEXT GitHub personal access token
  --dry-run        Preview changes without creating
```

### `repo-creator update`

Update an existing repository from a configuration file.

```bash
repo-creator update CONFIG_FILE [OPTIONS]

Options:
  -o, --owner TEXT Repository owner
  -t, --token TEXT GitHub personal access token
  --dry-run        Preview changes without applying
```

### `repo-creator validate`

Validate a configuration file.

```bash
repo-creator validate CONFIG_FILE
```

### `repo-creator export`

Export an existing repository's settings to a configuration file.

```bash
repo-creator export REPO_NAME [OPTIONS]

Options:
  -o, --owner TEXT  Repository owner
  -f, --output TEXT Output file path
  -t, --token TEXT  GitHub personal access token
```

## Configuration Options

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Repository name |
| `description` | string | No | Repository description |
| `private` | boolean | No | Whether the repository is private (default: false) |
| `topics` | list | No | Repository topics/tags |
| `default_branch` | string | No | Default branch name (default: main) |
| `has_issues` | boolean | No | Enable issues (default: true) |
| `has_wiki` | boolean | No | Enable wiki (default: true) |
| `has_projects` | boolean | No | Enable projects (default: true) |
| `auto_init` | boolean | No | Initialize with README (default: true) |

## Example Configuration

```yaml
name: my-python-project
description: A Python project for data processing
private: false
topics:
  - python
  - data-processing
  - automation
default_branch: main
has_issues: true
has_wiki: true
has_projects: true
auto_init: true
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token with repo permissions |

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running Tests with Coverage

```bash
pytest tests/ --cov=repo_creator --cov-report=term-missing
```

## License

MIT
