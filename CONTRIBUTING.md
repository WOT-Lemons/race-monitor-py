# Contributing

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for environment and dependency management

## Development Setup

```bash
git clone https://github.com/WOT-Lemons/race-monitor-py.git
cd race-monitor-py
uv sync --group dev
```

## Running Tests

```bash
uv run --group dev pytest tests/
```

## Generating Docs

```bash
uv run --group dev pdoc src/race_monitor --output-dir docs/api
```

## Submitting Changes

1. Create a branch from `main`
2. Open a pull request — CI must pass before merge
3. Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`, `ci:`, `docs:`
