# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Documentation**: Corrected marks API documentation across all docs to use `CtyMark` objects instead of strings
  - Updated `docs/user-guide/advanced/marks.md` to show correct `CtyMark` usage with `.mark()` and `.with_marks()`
  - Fixed `docs/reference/go-cty-comparison.md` marks section to use `unmark()` instead of non-existent methods
  - Corrected `docs/how-to/migrate-from-go-cty.md` and `docs/user-guide/advanced/terraform-interop.md`
  - Updated `examples/advanced/marks.py` to demonstrate correct API
- **Documentation**: Added explanatory note about `CtyList.raw_value` returning tuples for immutability
- **Documentation**: Updated CONTRIBUTING.md emoji policy to reflect actual practice (decorative emojis acceptable)
- **Documentation**: Updated coverage target language to show 94% achievement

### Changed
- Updated CHANGELOG.md to accurately reflect implemented functions
- Fixed function naming to match actual exports (e.g., `min_fn` instead of `min`)
- Removed non-existent base64 encoding functions from documentation

## [0.0.1000] - 2025-10-17

### Project Status
- **Development Status**: Alpha
- **Test Coverage**: 94%
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
- **Collection**: `distinct`, `flatten`, `sort`, `concat`, `contains`, `keys`, `values`, `length`, `slice`, `reverse`, `compact`, `chunklist`, `merge`, `lookup`, `setproduct`, `zipmap`, `element`, `hasindex`, `index`, `coalesce`, `coalescelist`
- **String**: `upper`, `lower`, `trim`, `trimprefix`, `trimsuffix`, `trimspace`, `split`, `join`, `replace`, `substr`, `regex`, `regexall`, `regexreplace`, `chomp`, `indent`, `title`, `strrev`
- **Bytes**: `byteslen`, `bytesslice`
- **Numeric**: `abs_fn`, `ceil_fn`, `floor_fn`, `log_fn`, `pow_fn`, `signum_fn`, `min_fn`, `max_fn`, `parseint_fn`, `add`, `subtract`, `multiply`, `divide`, `modulo`, `negate`, `int_fn`
- **Comparison**: `equal`, `not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`
- **Conversion**: `to_bool`, `to_string`, `to_number`
- **Datetime**: `formatdate`, `timeadd`
- **Encoding**: `jsonencode`, `jsondecode`, `csvdecode`

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
