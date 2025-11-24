# CTY Path

The `pyvider.cty.path` module provides type-safe navigation through nested data structures using path expressions.

Key components:
- **`CtyPath`** - Represents a path through a nested structure as a sequence of steps
- **`GetAttrStep`** - Navigate to an object attribute by name
- **`IndexStep`** - Navigate to a list/tuple element by numeric index
- **`KeyStep`** - Navigate to a map element by string key

Paths are primarily used for error reporting (providing clear indication of where validation failed) and programmatic navigation through complex structures. They enable precise identification of data locations like `root.users[2].address.city`.

**Use Cases**:
- Error messages showing exact location of validation failures
- Programmatic traversal of nested configurations
- Building tools that need to reference specific parts of a structure

For detailed path navigation documentation, see: **[User Guide: Path Navigation](../user-guide/advanced/path-navigation.md)**

---

::: pyvider.cty.path
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
