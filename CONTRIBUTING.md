# Contributing to Agentic Core Observability

Thank you for your interest in contributing! This guide covers the workflow
for submitting changes.

## Development Setup

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r src/requirements.txt
   pip install pytest pytest-cov ruff
   ```

3. Verify your environment:

   ```bash
   python -m tests.test_connection
   ```

## Branching Strategy

- Create a feature branch from `main`: `git checkout -b feature/your-feature`
- Use descriptive branch names: `fix/loop-detection-edge-case`,
  `docs/add-api-reference`, `feat/add-metric-export`

## Before Submitting a PR

1. Run the test suite: `pytest tests/ -v`
2. Run the linter: `ruff check src/ tests/`
3. Ensure your changes do not break existing tests.
4. Add tests for any new functionality.
5. Update documentation if behavior changes.

## PR Guidelines

- Keep PRs focused — one issue per PR.
- Write a clear description referencing the issue number.
- Include before/after screenshots or logs if applicable.

## Code Style

- Python 3.12+ type hints on all public functions.
- Docstrings on all public classes and functions.
- Follow existing logging patterns using the `logging` module.

## Questions?

Open a discussion or issue on the repository if anything is unclear.
