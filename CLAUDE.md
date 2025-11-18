# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Setup

Always use `uv sync` to activate the development environment. This uses `uv` for virtual environment management and creates environments in `.venv/`. The environment setup is platform-aware and handles Python version compatibility automatically.

## Common Commands

### Environment and Dependencies
- `uv sync` - Setup development environment (required first step)
- `uv sync --all-groups` - Install/update all dependencies including dev tools

### Testing
- `uv run pytest tests/` - Run all tests
- `uv run pytest tests/ -x --tb=short` - Run tests with early exit and short traceback
- `uv run pytest --run-benchmarks` - Run performance benchmark tests
- `uv run pytest --run-compat` - Run Go/Python cross-language compatibility tests
- `uv run pytest tests/path/to/specific_test.py::test_function` - Run specific test

### Code Quality
- `uv run ruff format src/ tests/` - Auto-format code
- `uv run ruff check src/ tests/` - Lint code
- `uv run ruff check src/ tests/ --fix` - Auto-fix linting issues
- `uv run mypy src/` - Type checking
- `uv run bandit -ll -r src/` - Security analysis

### Build and Validation
- `uv build` - Build package (creates wheel in `dist/`)
- `./validate-pipeline.sh` - Run complete validation pipeline (tests, linting, type checking, build)

### Pre-commit Hooks
- `pre-commit install` - Install git pre-commit hooks
- `pre-commit run --all-files` - Run all hooks on all files

## Architecture Overview

### Core Package Structure
- **`src/pyvider/cty/`** - Main package implementing go-cty type system in Python
- **`types/`** - Type system implementation (primitives, collections, structural, capsule)
- **`values/`** - Value objects and validation
- **`conversion/`** - Type conversion and unification logic
- **`functions/`** - Standard library functions (collection, string, numeric, etc.)
- **`exceptions/`** - Custom exception hierarchy
- **`codec.py`** - JSON/MessagePack serialization
- **`parser.py`** - Terraform type string parsing

### Type System Hierarchy
- **Primitives**: `CtyString`, `CtyNumber`, `CtyBool`
- **Collections**: `CtyList`, `CtyMap`, `CtySet`
- **Structural**: `CtyObject`, `CtyTuple`
- **Dynamic**: `CtyDynamic` (type determined at runtime)
- **Capsule**: `CtyCapsule`, `CtyCapsuleWithOps` (opaque data containers)

### Key Design Patterns
- **Immutable Values**: All `CtyValue` instances are immutable
- **Marks System**: Attach metadata to values without modification via `CtyMark`
- **Path Navigation**: Type-safe access to nested data structures
- **Cross-Language Compatibility**: JSON/MessagePack interop with go-cty

### Testing Structure
- **`tests/types/`** - Type system unit tests
- **`tests/compatibility/`** - Cross-language compatibility tests with Go
- **`tests/fixtures/`** - Test data and fixtures (auto-generated from Go)
- **Markers**: `@pytest.mark.benchmark` for performance tests, `@pytest.mark.compat` for compatibility tests

### Configuration Details
- **Python Version**: Requires Python 3.11+ (uses modern type hints)
- **Build System**: setuptools with `src/` layout
- **Dependencies**: attrs, msgpack, provide-foundation
- **Dev Tools**: pytest, ruff, mypy, hypothesis, bandit

### Cross-Language Compatibility
The `compatibility/` directory contains Go and Python implementations for testing interoperability:
- Go fixture generator creates test data consumed by Python tests
- Tests marked with `@pytest.mark.compat` verify serialization compatibility
- Use `--run-compat` flag to run cross-language tests (requires Go runtime)

### Performance and Benchmarks
- Performance tests marked with `@pytest.mark.benchmark`
- Use `--run-benchmarks` flag to run performance tests
- Benchmarking infrastructure built into test suite

## Code Style Requirements
- Modern Python 3.11+ typing: use `dict`, `list`, `set` (lowercase native types)
- Use union operator `|` for type unions
- Use `from __future__ import annotations` for forward reference support and unquoted types (enables cleaner type hints without string quotes); avoid other `__future__` imports
- No hardcoded defaults anywhere in the codebase
- Follow ruff formatting and linting rules
- Strict mypy type checking enabled
- After an update to a Python file, you will run `uv run ruff format` on it, and `uv run ruff check --fix` and any other pertinent code quality tools in order to prevent problems up front.