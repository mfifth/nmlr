# Contributing to NMLR

Thank you for your interest in contributing to NMLR! This document outlines the process for contributing.

## Setup

1. Fork and clone the repository.
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy environment: `cp .env.example .env` and add API keys if needed.
5. Install dev tools: `pip install -r requirements-dev.txt && pre-commit install`

## Running Tests

Tests are network-free: `pytest -q`

## Code Style

- Use `ruff` for linting and `black` for formatting.
- Pre-commit hooks will enforce this.
- Commit messages: Use imperative mood, e.g., "Add feature X".

## Pull Request Checklist

- [ ] Tests pass locally.
- [ ] No secrets or API keys committed.
- [ ] Documentation updated.
- [ ] Pre-commit passes.
- [ ] Artifacts (if any) are optional.

## Adding Benchmark Items

Edit `experiments/ambiguous_logic/data.jsonl` with new JSON lines: `{"id": "Q6", "prompt": "...", "gold": "..."}`
