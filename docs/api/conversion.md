# CTY Conversion

The `pyvider.cty.conversion` module provides type conversion and unification capabilities for transforming values between different cty types.

Key functions:
- **`convert(value, target_type)`** - Convert a `CtyValue` to a different type when possible (e.g., number to string, string to number)
- **`unify(types)`** - Find the most specific type that can represent all given types (type unification)

**Conversion vs Validation**: Conversion is more flexible than validation - it attempts to transform values between compatible types, while validation strictly checks conformance to a type schema. For example, `convert(CtyString().validate("123"), CtyNumber())` succeeds and returns the number 123, while `CtyNumber().validate("123")` fails because the input is not already a number.

Type conversion is essential for building flexible APIs that accept multiple input formats and for implementing polymorphic functions that work across different types.

For detailed conversion documentation, see: **[User Guide: Type Conversion](../user-guide/core-concepts/conversion.md)**

---

::: pyvider.cty.conversion
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
