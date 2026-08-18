# Contributing to pyvider-cty

Thank you for your interest in contributing to pyvider-cty! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` for dependency management
- Git for version control

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/provide-io/pyvider-cty.git
   cd pyvider-cty
   ```

2. **Set up development environment**
   ```bash
   uv sync
   ```

   This automatically:
   - Creates a virtual environment in `.venv/`
   - Installs all dependencies including dev tools
   - Activates the environment

3. **Verify setup**
   ```bash
   uv run pytest tests/
   ```

## Development Workflow

### Before You Start

1. Check existing issues and pull requests
2. For major changes, open an issue first to discuss
3. Fork the repository and create a feature branch

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   # Format code
   uv run ruff format src/ tests/

   # Check linting
   uv run ruff check src/ tests/ --fix

   # Run type checking
   uv run mypy src/

   # Run tests
   uv run pytest tests/

   # Security scan
   uv run bandit -ll -r src/
   ```

   There is no single validation-pipeline script; the steps above (plus `make compat`, below, for changes touching wire format, functions, or refinements) are what CI runs.

### Code Style

- **Formatting**: Uses `ruff format` (based on Black)
- **Linting**: Uses `ruff check` with strict rules
- **Type Hints**: Required for all functions (mypy strict mode)
- **Line Length**: 111 characters maximum
- **Import Organization**: Automatic sorting with isort via ruff
- **Emojis**: Decorative emoji comments are acceptable in source files

### Type Annotations

- All functions must have complete type annotations
- Use modern Python 3.11+ syntax:
  - Use `dict`, `list`, `set` (not `Dict`, `List`, `Set`)
  - Use `|` for unions (not `Union`)
  - Use `Any` only when truly necessary
- Mypy must pass with zero errors in strict mode

### Testing

#### Writing Tests

- Place tests in `tests/` directory matching source structure
- Use descriptive test names: `test_feature_behavior_expected_result`
- Include docstrings for complex test scenarios
- Aim for 80%+ test coverage

#### Test Structure

```python
def test_feature_name() -> None:
    """Test that feature does X when Y."""
    # Arrange
    input_data = prepare_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

#### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/types/primitives/test_bool.py

# Run with coverage
uv run pytest tests/ --cov=src/pyvider/cty --cov-report=html

# Run with verbose output
uv run pytest tests/ -v

# Run specific markers (both are skipped by default; the flag opts them in)
uv run pytest tests/ -m benchmark --run-benchmarks  # Performance tests
uv run pytest tests/ -m compat --run-compat          # Cross-language compatibility
```

#### Never change the tree while a suite is in flight

Don't `git checkout`, `git stash`, rebase, or switch branches while a test run is going — especially a parallel one. Workers import at staggered times, so some pick up the old files and some the new, and the resulting failures look exactly like a nondeterministic bug in code that is actually fine. A run that spanned a tree change is **void, not data**: discard it and re-run on a settled tree rather than investigating it. This has cost this project one long investigation into an xdist race that never existed (see the `TestCanonicalSortKey` entry in `.provide/GO-CTY-PARITY.md`). If two sessions share one working directory, one of them should be in a `git worktree`.

#### Cross-Language Compatibility Suite

The tests under `tests/compatibility/` (`@pytest.mark.compat`) don't assert against checked-in fixtures — they run a live differential comparison against real go-cty through a `soup-go` oracle binary, built from a **sibling `tofusoup` checkout** (expected at `../tofusoup` next to this repository). They are skipped unless `--run-compat` is passed, and the oracle needs `SOUP_GO_BIN` pointed at a built binary.

The easiest way to run them is:

```bash
make compat
```

which builds `soup-go` from the sibling checkout and runs `pytest --run-compat tests/compatibility/` against it. If the `tofusoup` checkout or the Go toolchain isn't present, it prints a message and exits 0 rather than failing — a machine without the Go toolchain isn't expected to run this suite, but a run that checked nothing has to say so.

#### Test Coverage Requirements

- Minimum coverage: 75% (enforced in CI)
- Target coverage: 90%+ (currently at ~93%)
- All new features must include tests
- Bug fixes should include regression tests

### Documentation

- Add docstrings to all public APIs
- Update relevant guide chapters in `docs/user-guide/`
- Add examples to `examples/` for new features
- Keep README.md current

#### Building the Docs

```bash
uv run --group docs mkdocs build --strict

# Or serve locally with live reload
uv run --group docs mkdocs serve
```

#### Docstring Format

```python
def function_name(param: Type) -> ReturnType:
    """Brief one-line description.

    Detailed description if needed. Explain the purpose,
    behavior, and any important details.

    Args:
        param: Description of parameter.

    Returns:
        Description of return value.

    Raises:
        ErrorType: When and why this error is raised.

    Examples:
        >>> result = function_name(value)
        >>> print(result)
        expected_output
    """
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `perf`: Performance improvements
- `chore`: Build process, dependencies, etc.

**Examples:**
```
feat(types): add CtyDuration type
fix(codec): handle edge case in MessagePack serialization
docs(guide): update serialization examples
test(functions): add property-based tests for numeric functions
```

### Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template completely
   - Link related issues
   - Request review from maintainers

4. **PR Requirements**
   - All tests must pass
   - Coverage must meet threshold (75%+)
   - Type checking must pass (mypy strict mode)
   - Linting must pass (ruff)
   - Security scan must pass (bandit)
   - Documentation must be updated
   - Changes must be noted in CHANGELOG.md

5. **Address Review Feedback**
   - Respond to all comments
   - Make requested changes
   - Push updates to the same branch

## Project Structure

```
pyvider-cty/
├── src/pyvider/cty/          # Main package
│   ├── types/                # Type system
│   ├── values/               # Value objects
│   ├── functions/            # Built-in functions
│   ├── conversion/           # Type conversion
│   ├── exceptions/           # Error types
│   ├── codec.py              # Serialization
│   └── parser.py             # Type parsing
├── tests/                    # Test suite
├── docs/                     # Documentation
├── examples/                 # Usage examples
├── .github/workflows/        # CI/CD
└── pyproject.toml            # Project config
```

## Release Process

(For maintainers only)

1. Update the `VERSION` file (semantic version, e.g. `0.5.0`, no leading `v`)
2. Update CHANGELOG.md — curated notes, written by hand, for this release
3. Update pyproject.toml `Development Status` classifier
4. Create a GitHub Release (tag `vX.Y.Z` to match `VERSION`) — `.github/workflows/release.yml` triggers on `release: published`, not on a tag push, so the release doesn't start until the GitHub Release is actually published. `workflow_dispatch` is available for a dry run.
5. GitHub Actions handles the rest: build, TestPyPI publish and verify, PyPI publish, SBOM, and artifact signing.

CHANGELOG.md's "Earlier releases" section covers everything before 0.4.0 and
is frozen — it is grouped commit subjects from a period when no changelog was
kept, and that history does not change. New releases get a curated entry at
the top of the file, written by hand.

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing documentation in `docs/user-guide/`

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to pyvider-cty!
