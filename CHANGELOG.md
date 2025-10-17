# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive type checking with mypy (strict mode) and ty checker
- Full test suite with 922 passing tests
- Cross-language compatibility with go-cty via MessagePack serialization
- TofuSoup integration for cross-language testing
- Property-based testing with Hypothesis
- Performance benchmarking infrastructure
- CI/CD pipeline with GitHub Actions
- Comprehensive documentation (17-chapter guide)
- 14 working examples covering all major features

### Changed
- Improved type safety with explicit casts for mypy/ty compatibility
- Enhanced error messages with structured context
- Standardized file headers and SPDX license identifiers

### Fixed
- All type checker errors (0 mypy errors, 0 ty errors in 56 files)
- All linting issues (ruff passing)
- All security issues (bandit clean scan)

## [0.0.1000] - 2025-10-17

### Project Status
- **Development Status**: Alpha
- **Test Coverage**: 51%
- **Type Safety**: 100% (0 errors)
- **Security**: Clean (bandit scan passed)

### Core Features

#### Type System
- **Primitive Types**: `CtyString`, `CtyNumber`, `CtyBool`
- **Collection Types**: `CtyList`, `CtySet`, `CtyMap`
- **Structural Types**: `CtyObject`, `CtyTuple`, `CtyDynamic`
- **Advanced Types**: `CtyCapsule`, `CtyCapsuleWithOps`

#### Value Operations
- Null and Unknown value handling
- Refined unknown values with bounds/constraints
- Value marks for metadata attachment
- Immutable value semantics

#### Serialization
- JSON encoding/decoding
- MessagePack encoding/decoding
- Cross-language compatibility with go-cty
- Type preservation in serialization

#### Functions
- **Collection**: `distinct`, `flatten`, `sort`, `concat`, `contains`, `keys`, `values`, `length`, `slice`, `reverse`, `compact`, `chunklist`, `merge`, `lookup`, `setproduct`, `zipmap`
- **String**: `upper`, `lower`, `trim`, `trimprefix`, `trimsuffix`, `split`, `join`, `replace`, `substr`, `regex`, `regexall`
- **Numeric**: `abs`, `ceil`, `floor`, `log`, `pow`, `signum`, `min`, `max`, `parseint`
- **Comparison**: `equal`, `not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`
- **Conversion**: `tobool`, `tostring`, `tonumber`, `tolist`, `toset`, `tomap`
- **Datetime**: `formatdate`, `timeadd`, `timestamp`
- **Encoding**: `base64encode`, `base64decode`, `jsonencode`, `jsondecode`

#### Path Navigation
- Type-safe path navigation with `CtyPath`
- Attribute access via `GetAttrStep`
- Index access via `IndexStep`
- Map key access via `KeyStep`

#### Validation & Errors
- Rich exception hierarchy
- Detailed error context with paths
- Validation error propagation
- Error boundary integration

### Infrastructure
- **Build System**: setuptools with `src/` layout
- **Dependency Management**: uv with lockfile
- **Testing**: pytest with coverage tracking
- **Code Quality**: ruff (formatter + linter)
- **Type Checking**: mypy (strict) + ty checker
- **Security**: bandit scanning
- **CI/CD**: GitHub Actions (quality, tests, security, build)
- **Documentation**: Comprehensive guide + API docs

### Dependencies
- Python ≥ 3.11
- attrs ≥ 25.1.0
- msgpack ≥ 1.1.0
- provide-foundation ≥ 0.0.0

---

## Version History Format

Starting with the next release, we will use the following categories:

### Added
For new features and capabilities.

### Changed
For changes in existing functionality.

### Deprecated
For soon-to-be removed features (with migration path).

### Removed
For removed features.

### Fixed
For bug fixes.

### Security
For security fixes and improvements.

---

[Unreleased]: https://github.com/provide-io/pyvider-cty/compare/v0.0.1000...HEAD
[0.0.1000]: https://github.com/provide-io/pyvider-cty/releases/tag/v0.0.1000
