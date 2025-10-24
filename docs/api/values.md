# CTY Values

The `pyvider.cty.values` module defines the `CtyValue` class, which represents immutable, type-safe data instances in the cty system.

Key concepts:
- **Immutability** - Once created, `CtyValue` instances cannot be modified. All operations return new values.
- **Type safety** - Every value has an associated `CtyType` that governs its structure and operations
- **Special values** - Support for null values (`CtyValue.null(type)`) and unknown values (`CtyValue.unknown(type)`)
- **Marks** - Ability to attach metadata to values without modifying the value itself
- **Raw value access** - Use the `.raw_value` property to access the underlying Python value

**Creating Values**: You should always create values through type validation (`my_type.validate(data)`) rather than constructing `CtyValue` directly. The validation process ensures type safety and proper initialization.

**Accessing Data**: Values support Python's standard access patterns - use `value['attr']` for object attributes, `value[index]` for list/tuple elements, and iteration (`for item in list_value`) for collections.

For detailed value documentation, see: **[User Guide: Working with Values](../user-guide/core-concepts/values.md)**

---

::: pyvider.cty.values
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
