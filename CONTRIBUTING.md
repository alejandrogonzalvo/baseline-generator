# Contributing to Baseline Generator

Thank you for your interest in contributing to Baseline Generator! This guide will help you understand our development process and standards.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/baseline-generator.git
   cd baseline-generator
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Run tests**:
   ```bash
   poetry run pytest
   ```

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated semantic versioning and changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature (triggers minor version bump)
- **fix**: A bug fix (triggers patch version bump)
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance (triggers patch version bump)
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Examples

```bash
# Feature addition (minor version bump: 1.0.0 -> 1.1.0)
feat: add support for YAML baselines
feat(cli): add --verbose flag for detailed output

# Bug fix (patch version bump: 1.0.0 -> 1.0.1)
fix: handle empty JSON files gracefully
fix(generator): resolve path traversal issue

# Breaking change (major version bump: 1.0.0 -> 2.0.0)
feat!: change API to use async/await

# With body and footer
feat: add baseline comparison caching

Add in-memory caching for baseline comparisons to improve performance
when running multiple tests against the same baseline.

Closes #123
```

### Breaking Changes

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:

```bash
feat!: remove deprecated generate_baseline_sync method

BREAKING CHANGE: The synchronous generate_baseline_sync method has been removed. Use generate_baseline instead.
```

## Code Quality Standards

Before submitting a pull request, ensure your code meets our quality standards:

```bash
# Type checking
poetry run mypy baseline_generator

# Code formatting
poetry run black baseline_generator tests

# Import sorting
poetry run isort baseline_generator tests

# Run all tests
poetry run pytest

# Run all checks together
poetry run pytest && poetry run mypy baseline_generator && poetry run black --check baseline_generator tests && poetry run isort --check-only baseline_generator tests
```

## Release Process

Releases are automated based on conventional commits:

1. **Automatic Releases**: When commits are pushed to `main`, the release workflow:
   - Analyzes commit messages since the last release
   - Determines the next version using semantic versioning
   - Updates `pyproject.toml` and `CHANGELOG.md`
   - Creates a GitHub release
   - Publishes to PyPI

2. **Version Bumps**:
   - `feat:` → Minor version bump (1.0.0 → 1.1.0)
   - `fix:` or `perf:` → Patch version bump (1.0.0 → 1.0.1)
   - `feat!:` or `BREAKING CHANGE:` → Major version bump (1.0.0 → 2.0.0)

3. **Manual Releases**: For emergency releases, use the "Manual Publish to PyPI" workflow in GitHub Actions.

## Pull Request Guidelines

1. **Fork and Branch**: Create a feature branch from `main`
2. **Conventional Commits**: Use conventional commit format
3. **Tests**: Add tests for new functionality
4. **Documentation**: Update README and docstrings as needed
5. **Quality Checks**: Ensure all CI checks pass

## Testing

- Write tests for all new functionality
- Maintain 100% coverage on core functionality
- Use descriptive test names and docstrings
- Test both success and error cases

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Include examples in docstrings where helpful
- Update CHANGELOG.md entries will be generated automatically

## Questions?

Feel free to open an issue for questions about contributing or to discuss new features! 