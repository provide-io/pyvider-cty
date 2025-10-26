# API Reference

Welcome to the complete API reference for pyvider.cty. This section provides detailed documentation for all public classes, functions, and modules in the library.

## Module Organization

The pyvider.cty API is organized into the following modules:

### Core Modules

- **[Types](types/index.md)** - Type system implementation (primitives, collections, structural, capsule)
  - [Primitive Types](types/primitives.md) - `CtyString`, `CtyNumber`, `CtyBool`
  - [Collection Types](types/collections.md) - `CtyList`, `CtyMap`, `CtySet`
  - [Structural Types](types/structural.md) - `CtyObject`, `CtyTuple`, `CtyDynamic`
  - [Capsule Types](types/capsule.md) - `CtyCapsule`, `CtyCapsuleWithOps`

- **[Values](values.md)** - `CtyValue` class for immutable, type-safe data instances

- **[Conversion](conversion.md)** - Type conversion and unification functions
  - `convert(value, target_type)` - Convert between types
  - `unify(types)` - Find the most specific common type

### Serialization & Encoding

- **[Codec](codec.md)** - MessagePack serialization for cross-language compatibility
  - `cty_to_msgpack()` - Serialize to binary format
  - `cty_from_msgpack()` - Deserialize from binary format

- **[Functions](functions.md)** - Standard library of built-in functions
  - String manipulation, numeric operations, collection functions
  - Type conversions, encoding/decoding, date/time operations

### Advanced Features

- **[Path Navigation](path.md)** - Navigate nested structures with `CtyPath`
  - `GetAttrStep`, `IndexStep`, `KeyStep`

- **[Parser](parser.md)** - Terraform type string parsing
  - `parse_tf_type_to_ctytype()` - Parse Terraform type specifications
  - `parse_type_string_to_ctytype()` - Alias for backward compatibility

- **[Validation](validation.md)** - Recursion detection and validation utilities
  - Recursion context management
  - Cycle detection decorators

- **[Context](context.md)** - Validation depth tracking
  - Context-local state management
  - Depth limit protection

## Quick Reference

### Importing Types

```python
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool,      # Primitives
    CtyList, CtyMap, CtySet,            # Collections
    CtyObject, CtyTuple, CtyDynamic,    # Structural
    CtyCapsule, CtyCapsuleWithOps,      # Capsule
    CtyType, CtyValue,                   # Base classes
)
```

### Importing Utilities

```python
from pyvider.cty import convert, unify              # Conversion
from pyvider.cty import CtyMark                     # Marks
from pyvider.cty.codec import (                     # Serialization
    cty_to_msgpack, cty_from_msgpack
)
from pyvider.cty.functions import (                 # Functions
    jsonencode, jsondecode,
    upper, lower, concat,
    # ... and many more
)
```

### Importing Exceptions

```python
from pyvider.cty import (
    CtyValidationError,                # General validation
    CtyConversionError,                # Type conversion
    CtyAttributeValidationError,       # Object attributes
    CtyListValidationError,            # List validation
    CtyMapValidationError,             # Map validation
    CtySetValidationError,             # Set validation
    CtyTupleValidationError,           # Tuple validation
    CtyTypeMismatchError,              # Type mismatches
    CtyTypeParseError,                 # Type string parsing
)
```

## Documentation Notes

- **Auto-generated sections**: Some API sections are auto-generated from source code docstrings
- **Type hints**: All functions include complete type annotations
- **Examples**: Most API functions include usage examples
- **Related guides**: Each API section links to related user guide chapters

## Additional Resources

- **[User Guide](../user-guide/index.md)** - Comprehensive feature documentation
- **[How-To Guides](../how-to/index.md)** - Task-oriented guides
- **[Getting Started](../getting-started/index.md)** - Quick introduction
- **[Examples](../getting-started/examples.md)** - Runnable code examples

---

# PyVider CTY API

::: pyvider.cty
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
