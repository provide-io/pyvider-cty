# Capsule Types

Capsule types allow you to encapsulate opaque Python objects within the cty type system. They are useful for wrapping foreign data types that cannot be represented by the standard cty types, such as file handles, database connections, or other external resources.

The capsule types are:
- **`CtyCapsule`** - Base capsule type for wrapping arbitrary Python objects with type checking
- **`CtyCapsuleWithOps`** - Extended capsule type that supports custom operations on encapsulated data
- **`BytesCapsule`** - Pre-defined capsule type for wrapping raw bytes data

Capsule types provide type safety by validating that encapsulated objects match the expected Python type. They preserve the opaque nature of the data while allowing it to participate in the cty type system for validation, serialization, and other operations.

See also: **[User Guide: Capsule Types](../../user-guide/type-reference/capsule.md)** for detailed usage examples.

---

::: pyvider.cty.types.capsule
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
