# Primitive Types

Primitive types are the fundamental building blocks of the pyvider.cty type system. They represent single, atomic values that cannot be decomposed into simpler types.

The three primitive types are:
- **`CtyString`** - Represents text values with Unicode support (NFC normalization)
- **`CtyNumber`** - Represents numeric values (integers and decimals) with arbitrary precision using Python's `Decimal` type
- **`CtyBool`** - Represents boolean values (`True` or `False`)

Primitive types perform strict validation - they do not perform automatic type coercion. For example, `CtyNumber().validate("123")` will raise a validation error because the input is a string, not a number. Use the conversion functions if you need flexible type transformation.

See also: **[User Guide: Primitive Types](../../user-guide/type-reference/primitives.md)** for detailed usage examples.

---

::: pyvider.cty.types.primitives
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
