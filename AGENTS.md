# AGENTS.md

This file provides guidance for AI assistants when working with code in this repository.

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
- `uv run pytest --run-compat` - Run the Go/Python cross-language compatibility tests directly (needs `SOUP_GO_BIN` pointed at a built `soup-go` binary; see below)
- `make compat` - Build the `soup-go` harness from a sibling `tofusoup` checkout and run the compatibility suite against it; this is the whole differential-testing story in one command, and skips cleanly (exit 0) if the sibling checkout or the Go toolchain is missing
- `uv run pytest tests/path/to/specific_test.py::test_function` - Run specific test

**Never change the tree while a suite is in flight.** No `git checkout`, `stash`, rebase or branch switch while tests are running, and especially not under `-n auto`: workers import at staggered times, so some read the old files and some the new, and the failures that produces are indistinguishable from a real nondeterministic bug. Treat any run that spanned a tree change as **void rather than as data** — discard it and re-run on a settled tree instead of investigating it. If another session shares this working directory, put one of you in a `git worktree`. (This cost one long investigation into an xdist race that never existed; see the `TestCanonicalSortKey` entry in `.provide/GO-CTY-PARITY.md`.)

### Code Quality
- `uv run ruff format src/ tests/ scripts/` - Auto-format code
- `uv run ruff check src/ tests/ scripts/` - Lint code
- `uv run ruff check src/ tests/ scripts/ --fix` - Auto-fix linting issues
- `uv run mypy src/` - Type checking
- `uv run bandit -ll -r src/` - Security analysis

### Build and Validation
- `uv build` - Build package (creates wheel in `dist/`)
- There is no single validation-pipeline script; CI runs format, lint, mypy, bandit, and the test suite as separate steps (see `.github/workflows/ci.yml`). Run `make lint`, `uv run mypy src/`, `uv run bandit -ll -r src/`, and `uv run pytest tests/` in sequence to reproduce it locally, plus `make compat` if your change touches wire format, functions, or refinements.

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
- **`tests/compatibility/`** - Cross-language compatibility tests against a live go-cty oracle (the `soup-go` harness), not checked-in fixtures
- **Markers**: `@pytest.mark.benchmark` for performance tests, `@pytest.mark.compat` for compatibility tests

### Configuration Details
- **Python Version**: Requires Python 3.11+ (uses modern type hints)
- **Build System**: setuptools with `src/` layout
- **Dependencies**: attrs, msgpack, provide-foundation
- **Dev Tools**: pytest, ruff, mypy, hypothesis, bandit

### Cross-Language Compatibility
The `tests/compatibility/` directory runs differential checks against real go-cty rather than asserting against checked-in fixtures:
- Tests marked with `@pytest.mark.compat` compare wire bytes, refinements, and function results against a live `soup-go` oracle binary
- `soup-go` is a harness built from a **sibling `tofusoup` checkout** (`../tofusoup` next to this repo) — it is not part of this repository
- Use `make compat` to build the harness and run the suite in one step (skips cleanly, exit 0, if the sibling checkout or Go toolchain is missing)
- Or run `uv run pytest --run-compat tests/compatibility/` directly, with `SOUP_GO_BIN` pointed at an already-built `soup-go` binary

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
