# Structural Types

Structural types define complex data structures with heterogeneous elements, where different positions or attributes can have different types. Unlike collections, structural types allow mixing different types within the same structure.

The structural types are:
- **`CtyObject`** - A structure with named attributes, each having its own type (similar to a typed dictionary). `optional_attributes` controls which attribute *keys* may be omitted entirely — omitting a key that is not declared optional still raises `CtyAttributeValidationError`. Every attribute, optional or not, accepts an explicit `None` for its value: nullability is a property of the value, not of the object type, so `CtyObject.validate()` does not enforce "must not be null" for any attribute. A caller that needs to reject an explicit null for a required field (as opposed to a missing key) has to check for that itself.
- **`CtyTuple`** - A fixed-length sequence where each position has a specific type (similar to a typed tuple). The number of elements and their types are defined at schema creation.
- **`CtyDynamic`** - A special type that can represent any value, with the actual type determined at runtime. Useful for scenarios where the type structure isn't known until runtime.

Structural types are ideal for modeling complex domain objects, API responses, and configuration schemas where different fields have different meanings and types.

See also: **[User Guide: Structural Types](../../user-guide/type-reference/structural.md)** for detailed usage examples.

---

::: pyvider.cty.types.structural
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
