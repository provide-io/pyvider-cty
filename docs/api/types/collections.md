# Collection Types

Collection types represent containers that hold multiple elements of a homogeneous type. All elements in a collection must conform to the same `element_type` specification.

The three collection types are:
- **`CtyList`** - Ordered collection that preserves element order and allows duplicates
- **`CtySet`** - Unordered collection of unique elements (automatically de-duplicates equal *known* elements)
- **`CtyMap`** - Key-value mapping where keys are always strings and values are of a specified type

Collections recursively validate all their elements during validation, ensuring type safety throughout nested structures. Collections are also iterable, allowing you to use standard Python iteration patterns (`for element in list_value`).

A `CtySet`'s internal payload is a tuple in go-cty's canonical sort order, not a Python `frozenset` — this is what lets a set hold elements that are themselves collections (a nested list, map or another set), which an unhashable-by-default Python container could not otherwise sit inside a `frozenset`. De-duplication only merges elements that are *known* and equal to each other: two unknown elements are distinct values that might resolve differently later, so a set can hold more than one unknown, and a set element's marks are hoisted onto the set itself during validation rather than staying on the element.

See also: **[User Guide: Collection Types](../../user-guide/type-reference/collections.md)** for detailed usage examples.

---

::: pyvider.cty.types.collections
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
