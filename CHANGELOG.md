# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial baseline generator functionality
- CLI interface for baseline management
- Test against baseline functionality with detailed diff reporting
- Comprehensive test suite with 100% coverage on core functionality
- Type safety with mypy enforcement
- Code quality tools (Black, isort)
- GitHub Actions CI/CD workflows
- Automated semantic versioning based on conventional commits

### Features
- Check baseline existence
- Load baselines from JSON files
- Generate new baseline files
- Test data against baselines with automatic creation when missing
- Detailed difference reporting for failed comparisons
- Support for nested data structures and arrays
- Custom exceptions for different error scenarios

## [0.1.0] - 2024-01-01

### Added
- Initial project structure with Poetry
- Basic BaselineGenerator class
- Command-line interface
- Documentation and README 