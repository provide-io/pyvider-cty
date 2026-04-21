# CTY Types

The `pyvider.cty.types` module provides the core type system for defining and validating data structures. Types act as schemas that describe the shape, structure, and constraints of your data.

All types inherit from the `CtyType` base class and provide a `validate()` method that converts raw Python data into immutable, type-safe `CtyValue` instances. The type system includes primitives (String, Number, Bool), collections (List, Map, Set), structural types (Object, Tuple), and special types (Dynamic, Capsule).

For detailed information about each type category, see:
- **[Primitive Types](primitives.md)** - String, Number, Bool
- **[Collection Types](collections.md)** - List, Map, Set
- **[Structural Types](structural.md)** - Object, Tuple, Dynamic
- **[Capsule Types](capsule.md)** - Opaque data containers

---

::: pyvider.cty.types
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
