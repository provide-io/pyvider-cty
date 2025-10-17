# API Stability and Compatibility Policy

This document defines the API stability guarantees and versioning policy for pyvider-cty.

## Versioning Scheme

pyvider-cty follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible new features
- **PATCH**: Backwards-compatible bug fixes

### Pre-1.0 Versioning (Current: 0.0.x)

**Alpha Status (0.0.x)**
- **Stability**: Experimental
- **API Changes**: May occur in any release
- **Breaking Changes**: Allowed without major version bump
- **Recommendation**: Pin exact version in production
- **Support**: Best-effort, no LTS

**Beta Status (0.1.x - Future)**
- **Stability**: Feature-complete, stabilizing
- **API Changes**: Minimized, documented in CHANGELOG
- **Breaking Changes**: Allowed but discouraged
- **Recommendation**: Pin to minor version
- **Support**: Security fixes for latest minor version

### Post-1.0 Versioning (Future)

**Stable Releases (1.x.x)**
- **Stability**: Production-ready
- **API Changes**: Only in MINOR versions
- **Breaking Changes**: Only in MAJOR versions
- **Recommendation**: Pin to major version
- **Support**: LTS policy TBD

## API Stability Levels

### Public API (Stable)

**Includes:**
- All public classes and functions in `pyvider.cty.*`
- Documented type signatures
- Error types and exception hierarchy
- Serialization format (MessagePack/JSON)

**Guarantees (Post-1.0):**
- No breaking changes within MAJOR version
- Deprecation warnings for at least 2 MINOR versions before removal
- Clear migration guides for breaking changes

**Current Status (Alpha):**
- ⚠️ May change without notice
- Check CHANGELOG.md for all changes

### Internal API (Unstable)

**Includes:**
- Modules starting with `_` (e.g., `_utils.py`, `_version.py`)
- Functions/classes marked with `@private` or `# INTERNAL`
- Implementation details not in documentation

**Guarantees:**
- ❌ No stability guarantees
- May change in PATCH releases
- Not covered by deprecation policy

### Experimental API (Unstable)

**Includes:**
- Features marked with `@experimental` decorator
- Features in `cty.experimental` module (if any)
- Features explicitly documented as "experimental"

**Guarantees:**
- ⚠️ May change in MINOR releases
- May be removed in MINOR releases
- Documented in CHANGELOG.md

## Breaking Change Policy

### What Constitutes a Breaking Change

**Breaking changes include:**

1. **Removing public API**
   ```python
   # BREAKING
   # Before: pyvider.cty.CtyString
   # After:  [removed]
   ```

2. **Changing function signatures**
   ```python
   # BREAKING
   # Before: def validate(value: Any) -> CtyValue
   # After:  def validate(value: Any, strict: bool = True) -> CtyValue
   #         (new required parameter)
   ```

3. **Changing return types**
   ```python
   # BREAKING
   # Before: def get_type() -> CtyType[Any]
   # After:  def get_type() -> str
   ```

4. **Changing exception types**
   ```python
   # BREAKING
   # Before: raises ValueError
   # After:  raises CtyValidationError
   ```

5. **Changing serialization format**
   ```python
   # BREAKING: Incompatible MessagePack format changes
   ```

6. **Renaming modules or classes**
   ```python
   # BREAKING
   # Before: from pyvider.cty.types import CtyString
   # After:  from pyvider.cty.primitives import CtyString
   ```

### What is NOT a Breaking Change

**Safe changes include:**

1. **Adding new optional parameters**
   ```python
   # SAFE
   # Before: def validate(value: Any) -> CtyValue
   # After:  def validate(value: Any, *, strict: bool = False) -> CtyValue
   ```

2. **Adding new methods/functions**
   ```python
   # SAFE: New public function
   def new_helper_function() -> str: ...
   ```

3. **Adding new exception types** (when subclassing existing)
   ```python
   # SAFE: More specific exception
   class CtyStringValidationError(CtyValidationError): ...
   ```

4. **Relaxing input validation**
   ```python
   # SAFE: Accepts more inputs than before
   # Before: Only accepts str
   # After:  Accepts str | bytes
   ```

5. **Bug fixes** (even if they change behavior)
   ```python
   # SAFE: Fixing incorrect behavior
   ```

6. **Performance improvements**
   ```python
   # SAFE: Implementation optimization
   ```

## Deprecation Policy

### Post-1.0 Deprecation Process

1. **Announcement** (Version N)
   - Feature marked with `@deprecated` decorator
   - Deprecation warning emitted at runtime
   - Documented in CHANGELOG.md with migration guide
   - Minimum 2 MINOR versions before removal

2. **Maintenance Period** (Version N+1, N+2)
   - Feature still works but warns
   - Documentation updated with alternatives
   - Migration guide provided

3. **Removal** (Version N+3 or MAJOR)
   - Feature removed in next MAJOR version
   - Or after 2 MINOR versions (whichever is later)

### Pre-1.0 Deprecation (Current)

- ⚠️ Deprecation policy not yet enforced
- Breaking changes may occur in any release
- Check CHANGELOG.md for all changes

### Deprecation Example

```python
import warnings
from typing import TypeVar

T = TypeVar("T")

@deprecated(
    version="1.2.0",
    removal_version="2.0.0",
    alternative="use CtyType.validate() instead"
)
def validate_cty_value(value: Any, cty_type: CtyType[T]) -> CtyValue[T]:
    """DEPRECATED: Use CtyType.validate() instead.

    This function will be removed in version 2.0.0.
    Migration: cty_type.validate(value)
    """
    warnings.warn(
        "validate_cty_value() is deprecated and will be removed in 2.0.0. "
        "Use CtyType.validate() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return cty_type.validate(value)
```

## Python Version Support

### Support Policy

- **Minimum Version**: Python 3.11+
- **Tested Versions**: 3.11, 3.12, 3.13
- **Future Versions**: 3.14+ (best-effort support)

### Python Version Lifecycle

- Support latest 3 minor versions of Python
- Drop support for Python versions reaching EOL
- Python version changes require MAJOR version bump (post-1.0)

### Current Support Matrix

| Python | Status | EOL Date |
|--------|--------|----------|
| 3.11   | ✅ Supported | Oct 2027 |
| 3.12   | ✅ Supported | Oct 2028 |
| 3.13   | ✅ Supported | Oct 2029 |
| 3.14   | 🔄 Planned | Oct 2030 |

## Cross-Language Compatibility

### go-cty Compatibility

pyvider-cty maintains **serialization compatibility** with [go-cty](https://github.com/zclconf/go-cty):

**Guarantees:**
- MessagePack format compatible across versions
- JSON format compatible across versions
- Type system semantics match go-cty
- Validated via TofuSoup test suite

**Version Mapping:**
- pyvider-cty 1.x.x ↔ go-cty 1.x.x
- Serialization format changes require coordination

### TofuSoup Testing

Cross-language compatibility verified through:
- Bidirectional serialization tests (Go ↔ Python)
- Type system conformance tests
- Run via: `soup cty test`

## Dependency Policy

### Direct Dependencies

- **attrs**: Used for class definitions
- **msgpack**: Used for serialization
- **provide-foundation**: Error handling and utilities

### Dependency Updates

- Security updates: Applied immediately in PATCH releases
- Major version bumps: Require pyvider-cty MINOR version bump (post-1.0)
- Breaking dependency changes: Require pyvider-cty MAJOR version bump (post-1.0)

### Minimum Versions

- We specify minimum versions: `attrs>=25.1.0`
- Users should pin exact versions in production
- We test against latest compatible versions in CI

## Migration Guides

### Upgrading Between Versions

**Pre-1.0 (Current)**
1. Read CHANGELOG.md for breaking changes
2. Update code as needed
3. Run full test suite
4. Update pinned version

**Post-1.0 (Future)**
1. Check CHANGELOG.md for deprecations
2. Fix deprecation warnings
3. Update to new MINOR version
4. Test thoroughly
5. MAJOR version upgrades require dedicated migration planning

## Stability Checklist for 1.0.0

Before declaring 1.0.0, we will ensure:

- [ ] API surface reviewed and finalized
- [ ] 90%+ test coverage
- [ ] Cross-language compatibility validated
- [ ] Performance benchmarks established
- [ ] Documentation complete
- [ ] Security audit completed
- [ ] 6+ months of beta stability
- [ ] No known critical bugs
- [ ] Deprecation policy tested
- [ ] Migration guides prepared

## Questions?

For API stability questions:
- Open a GitHub Discussion
- Check existing issues
- Contact: code@provide.io

---

**Status**: Alpha (0.0.x) - API may change
**Last Updated**: 2025-10-17
**Next Review**: Before Beta (0.1.0)
