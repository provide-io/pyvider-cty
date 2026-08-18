# Primitive Types

Primitive types are the fundamental building blocks of the pyvider.cty type system. They represent single, atomic values that cannot be decomposed into simpler types.

The three primitive types are:
- **`CtyString`** - Represents text values with Unicode support (NFC normalization)
- **`CtyNumber`** - Represents numeric values (integers and decimals) with arbitrary precision using Python's `Decimal` type
- **`CtyBool`** - Represents boolean values (`True` or `False`)

Primitive types accept a wire-friendly string form for `CtyNumber` and `CtyBool` — `CtyNumber().validate("123")` succeeds and returns the number `123`, and `CtyBool().validate("true")` succeeds and returns `True` — but they do not coerce across genuinely different shapes: `CtyNumber().validate([1, 2])` and `CtyString().validate(42)` both raise a validation error. Use the conversion functions if you need to transform an already-validated value from one type to another, such as turning a validated number into a string.

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
