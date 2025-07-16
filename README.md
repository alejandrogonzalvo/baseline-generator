# Baseline Generator

[![PyPI version](https://img.shields.io/pypi/v/baseline-generator.svg)](https://pypi.org/project/baseline-generator/)
[![Python Version](https://img.shields.io/pypi/pyversions/baseline-generator)](https://pypi.org/project/baseline-generator/)
[![Downloads](https://img.shields.io/pypi/dm/baseline-generator.svg)](https://pypi.org/project/baseline-generator/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Tests](https://img.shields.io/github/actions/workflow/status/alejandrogonzalvo/baseline-generator/tests.yml?branch=main&label=tests)](https://github.com/alejandrogonzalvo/baseline-generator/actions)

A Python package for generating and managing JSON test baselines with ease.

## Features
- 🏗️ **Generate baselines** - Create new baseline files with data validation
- ✅ **Test against baselines** - Compare test data with baselines and get detailed difference reports
- 🎯 **CLI Tool** - Command-line interface for easy baseline management

## Installation

```bash
# Clone the repository
git clone https://github.com/alejandrogonzalvogonzalvo/baseline-generator.git
cd baseline-generator

# Install with Poetry
poetry install
```

## Usage

### Python API

```python
from baseline_generator import BaselineGenerator, BaselineComparisonError, BaselineNotFoundError

# Initialize with default test folder
generator = BaselineGenerator()

# Or specify a custom test folder
generator = BaselineGenerator("my_test_folder")

# Generate a new baseline
test_data = {"expected": "result", "values": [1, 2, 3]}
generator.generate_baseline("new_baseline", test_data)

# Overwrite existing baseline
generator.generate_baseline("existing_baseline", test_data, overwrite=True)

# Test data against a baseline
try:
    generator.test_against_baseline("my_baseline", test_data)
    print("✓ Test passed - data matches baseline")
except BaselineComparisonError as e:
    print(f"❌ Test failed: {e.message}")
    for diff in e.differences:
        print(f"  - {diff}")
except BaselineNotFoundError as e:
    print(f"⚠️  Baseline created: {e.message}")
```

### Command Line Interface

```bash
# Check if a baseline exists
baseline-generator check my_baseline

# Generate a baseline from JSON file
baseline-generator generate my_baseline data.json

# Load and display a baseline
baseline-generator load my_baseline

# Test data against a baseline
baseline-generator test my_baseline test_data.json

# Use custom test folder
baseline-generator --test-folder custom_tests check my_baseline

# Overwrite existing baseline
baseline-generator generate my_baseline data.json --overwrite

# Don't auto-create missing baselines during testing
baseline-generator test my_baseline test_data.json --no-create
```

## Testing Against Baselines

The core functionality of this package is testing data against established baselines:

### Automatic Baseline Creation

When testing against a non-existent baseline, it will automatically be created:

```bash
$ poetry run baseline-generator test new_test test_data.json
Warning: Baseline 'new_test.json' did not exist and was created.
Review the generated baseline and re-run the test.
```

### Detailed Difference Reporting

When data doesn't match the baseline, you get detailed difference reports:

```bash
$ poetry run baseline-generator test api_test modified_data.json
❌ Test data does not match baseline 'api_test.json'

Differences found:
  1. api_response.data.users: List length mismatch - baseline: 2, test: 3
  2. api_response.data.users[1].name: Value mismatch - baseline: 'Bob', test: 'Charlie'
  3. api_response.data.total_count: Value mismatch - baseline: 2, test: 3
  4. api_response.metadata.timestamp: Value mismatch - baseline: '2024-01-01T10:00:00Z', test: '2024-01-01T11:00:00Z'
  5. api_response.metadata.version: Value mismatch - baseline: '1.0.0', test: '1.1.0'

Total differences: 5
```

### Difference Types Detected

- **Value mismatches**: Different primitive values
- **Type mismatches**: Different data types (string vs number, etc.)
- **Missing keys**: Keys present in baseline but missing in test data
- **Extra keys**: Keys in test data not present in baseline
- **List length mismatches**: Different array lengths
- **Nested structure differences**: Deep comparison of complex objects

## Development

### Code Quality Tools

This project enforces high code quality standards:

```bash
# Run tests
poetry run pytest

# Type checking
poetry run mypy baseline_generator

# Code formatting
poetry run black baseline_generator tests

# Import sorting
poetry run isort baseline_generator tests

# All checks together
poetry run pytest && poetry run mypy baseline_generator && poetry run black --check baseline_generator tests && poetry run isort --check-only baseline_generator tests
```

### CI/CD and Publishing

- **Automated Releases** (`.github/workflows/release.yml`):
  - Triggered on pushes to main branch
  - Automatically determines semantic version bumps
  - Generates changelog entries
  - Creates GitHub releases
  - Publishes to PyPI

### Configuration

The project uses `pyproject.toml` for all tool configuration:

- **Poetry**: Dependency management and packaging
- **mypy**: Strict type checking with enforced type hints
- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting (Black-compatible)
- **pytest**: Testing with coverage reporting
- **Coverage**: HTML and terminal coverage reports

## Requirements

- Python 3.12
- Poetry for dependency management

## License

MIT License
