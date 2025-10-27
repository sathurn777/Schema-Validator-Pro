# Contributing to Schema Validator Pro

Thank you for your interest in contributing to Schema Validator Pro! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip and virtualenv
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/schema-validator-pro.git
cd schema-validator-pro
```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

This will install:
- Production dependencies
- Testing tools (pytest, pytest-cov, pytest-asyncio, pytest-benchmark)
- Code quality tools (black, flake8, mypy)
- Build tools (setuptools, wheel, twine)

### 3. Verify Installation

```bash
# Run tests to verify setup
pytest backend/tests/ -v

# Check code coverage
pytest backend/tests/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

## Running Tests

### Run All Tests

```bash
pytest backend/tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest backend/tests/ -m unit

# Integration tests
pytest backend/tests/ -m integration

# End-to-end tests
pytest backend/tests/ -m e2e

# Performance benchmarks
pytest backend/tests/ -m performance
```

### Run with Coverage

```bash
pytest backend/tests/ --cov=backend --cov-report=term --cov-report=html
```

### Run Specific Test File

```bash
pytest backend/tests/test_schema_generator.py -v
```

### Run Tests in Parallel

```bash
pytest backend/tests/ -n auto
```

## Code Style

### Python Code Style

We follow PEP 8 with some modifications. Use the provided tools to ensure consistency:

#### Format Code with Black

```bash
black backend/
```

#### Check Code with Flake8

```bash
flake8 backend/ --max-line-length=120
```

#### Type Check with MyPy

```bash
mypy backend/
```

### Code Quality Standards

- **Test Coverage**: Maintain at least 95% code coverage
- **Type Hints**: All functions must have type annotations
- **Docstrings**: All public functions and classes must have docstrings
- **No TODO/FIXME**: Resolve all TODOs before submitting PR

### Pre-commit Checks

Before committing, run:

```bash
# Format code
black backend/

# Check linting
flake8 backend/

# Type check
mypy backend/

# Run tests
pytest backend/tests/

# Check coverage
pytest backend/tests/ --cov=backend --cov-report=term
```

## Submitting Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the code style guidelines

### 3. Test Your Changes

```bash
# Run all tests
pytest backend/tests/ -v

# Check coverage
pytest backend/tests/ --cov=backend --cov-report=term

# Ensure coverage is >= 95%
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new schema type support"
```

#### Commit Message Format

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template with:
   - Description of changes
   - Related issue numbers
   - Test results
   - Screenshots (if applicable)

### Pull Request Checklist

- [ ] Tests pass locally (`pytest backend/tests/`)
- [ ] Code coverage >= 95%
- [ ] Code formatted with Black
- [ ] No linting errors (flake8)
- [ ] Type hints added (mypy passes)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventional commits

## Reporting Bugs

### Before Submitting a Bug Report

1. Check existing issues to avoid duplicates
2. Verify the bug exists in the latest version
3. Collect relevant information:
   - Python version
   - Operating system
   - Error messages and stack traces
   - Steps to reproduce

### Submit a Bug Report

Create an issue with:

- **Title**: Clear, descriptive summary
- **Description**: Detailed explanation
- **Steps to Reproduce**: Numbered list
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Additional Context**: Screenshots, logs, etc.

## Feature Requests

We welcome feature requests! Please:

1. Check existing issues for similar requests
2. Clearly describe the feature and its benefits
3. Provide use cases and examples
4. Be open to discussion and feedback

## Development Guidelines

### Adding New Schema Types

1. Add schema template to `backend/services/schema_generator.py`
2. Add validation rules to `backend/services/schema_validator.py`
3. Register in `backend/registry/schema_registry.py`
4. Add comprehensive tests (minimum 20 test cases)
5. Update documentation

### Testing Requirements

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and workflows
- **Edge Cases**: Test boundary conditions and error handling
- **Performance**: Add benchmarks for new features
- **Coverage**: Maintain >= 95% coverage

### Documentation Requirements

- Update API_REFERENCE.md for API changes
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Include usage examples

## Questions?

If you have questions:

1. Check the [README.md](README.md)
2. Review [API_REFERENCE.md](docs/API_REFERENCE.md)
3. Search existing issues
4. Create a new issue with the "question" label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Schema Validator Pro! 🎉

