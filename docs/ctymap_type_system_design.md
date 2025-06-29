# CtyMap Type System Design

This document outlines the design and intended behavior for the `CtyMap` type within the `pyvider.cty` library, emphasizing compatibility with `go-cty` principles and a good Developer Experience (DX). It also covers necessary behaviors of `CtyString` and `CtyDynamic` where they interact with `CtyMap`.

## Core Principles

1.  **Go-Cty Compatibility:** Strive for behavior that mirrors `go-cty` where it makes sense in a Pythonic context. This is especially true for type conversion rules for primitive types when they are *values*.
2.  **Developer Experience (DX):**
    *   Type checking should be predictable.
    *   Error messages should be clear and actionable.
    *   Common use cases should feel natural.
3.  **Robustness & Reliability:** The type system should be sound and prevent unexpected errors or data corruption.

## `CtyString.validate(value)` Behavior

This method is crucial as it's used by `CtyMap` for both key and value validation if their type is `CtyString`.

1.  **Raw `None` Input:**
    *   `CtyString().validate(None)` shall return `CtyValue.null(CtyString())`.
    *   **Rationale:** `go-cty` converts null values to the null representation of the target type.

2.  **`CtyValue` Input:**
    *   `is_unknown`: Returns `CtyValue.unknown(CtyString())`.
    *   `is_null` (e.g., `CtyValue.null(CtyNumber())`): Returns `CtyValue.null(CtyString())`.
    *   `type` is `CtyString`: Returns the input `CtyValue` as-is.
    *   `type` is `CtyDynamic`:
        *   If `value.value` (the inner Python value) is `None`, returns `CtyValue.null(CtyString())`.
        *   Otherwise, attempts `str(inner_py_value)` where `inner_py_value` is the deeply unwrapped Python value from the dynamic `CtyValue`. If successful, returns `CtyValue(CtyString, result_str)`.
        *   If `str()` conversion fails, raises `CtyStringValidationError`.
    *   `type` is `CtyNumber` or `CtyBool` (i.e., other primitive types):
        *   Attempts `str(value.value)` (the underlying Python value of the primitive `CtyValue`).
        *   If successful, returns `CtyValue(CtyString, result_str)`.
        *   If `str()` conversion fails (unlikely for standard primitives), raises `CtyStringValidationError`.
    *   `type` is any other non-primitive, non-dynamic type (e.g., `CtyList`, `CtyMap`, `CtyObject`, `CtyCapsule`): Raises `CtyStringValidationError` (e.g., "Cannot convert CtyValue of type CtyList to CtyString.").

3.  **Raw Python `str` Input:**
    *   Returns `CtyValue(CtyString, input_str)`.

4.  **Raw Python Primitive Inputs (`int`, `float`, `bool`):**
    *   Converts the raw primitive to its string representation using `str()`.
    *   Returns `CtyValue(CtyString, converted_str)`.
    *   **Rationale:** Aligns with `go-cty`'s permissive conversion of primitive types to strings when a string context is expected (e.g., for attribute values).

5.  **Other Raw Python Types (lists, dicts, custom objects, etc.):**
    *   Raises `CtyStringValidationError` (e.g., "Value of type list cannot be converted to a string.").

## `CtyMap.usable_as(other_type)` Behavior

Determines if a map of type `SelfMap = map(K1, V1)` can be used where a map of type `OtherMap = map(K2, V2)` is expected.

1.  If `other_type` is `CtyDynamic`, returns `True`.
2.  If `other_type` is not a `CtyMap`, returns `False`.
3.  **Key Usability (`key_usable`):**
    *   If `OtherMap.key_type` is `CtyDynamic`, `key_usable` is `True`. (A map with any key type can be assigned to a map expecting dynamic keys).
    *   Else if `SelfMap.key_type` is `CtyDynamic` (and `OtherMap.key_type` is concrete): `key_usable` is `False`.
        *   **Rationale (DX & Safety):** A map that *allows* dynamic (i.e., any type of) keys cannot be safely used where a map *requires* a specific concrete key type (e.g., string keys). This prevents runtime errors if the dynamic-keyed map contains keys not compatible with the concrete key type. This aligns with stricter interpretations of type compatibility for collection keys.
    *   Else (both `SelfMap.key_type` and `OtherMap.key_type` are concrete): `key_usable` is `SelfMap.key_type.usable_as(OtherMap.key_type)`.
4.  **Value Usability (`value_usable`):**
    *   `value_usable` is `SelfMap.value_type.usable_as(OtherMap.value_type)`.
        *   **Note:** This means `map(K, CtyString).usable_as(map(K, CtyDynamic))` is `True`.
        *   And `map(K, CtyDynamic).usable_as(map(K, CtyString))` is also `True` (because `CtyDynamic` is usable as `CtyString`).
5.  **Result:** Returns `key_usable and value_usable`.

## `CtyMap.validate(value_to_validate)` Behavior

1.  **Input `value_to_validate` is `None`:**
    *   Returns `CtyValue.null(self)`.

2.  **Input `value_to_validate` is a `CtyValue`:**
    *   If `is_null`: Returns `CtyValue.null(self)`.
    *   If `is_unknown`: Returns `CtyValue.unknown(self)`.
    *   If `value_to_validate.type` is a `CtyMap`:
        *   If `self.equal(value_to_validate.type)`: Returns `value_to_validate` as-is (optimization).
        *   If `not value_to_validate.type.usable_as(self)` (using the refined `usable_as` logic above): Raises `CtyMapValidationError` indicating incompatible map types.
        *   Otherwise (types are usable but not identical), unbox `value_to_validate.value` and proceed with element-wise validation of the underlying Python dictionary.
    *   If `value_to_validate.type` is not `CtyMap`: Raises `CtyMapValidationError` (e.g., "Input CtyValue has type string, expected compatible map type.").

3.  **Input `value_to_validate` is a raw Python `dict`:**
    *   Proceeds to element-wise key/value validation.

4.  **Input `value_to_validate` is any other raw Python type (not `None`, not `dict`):**
    *   Raises `CtyMapValidationError` (e.g., "Input must be a dictionary, got list.").

5.  **Element-wise Key Validation (for each `k, v` in the (potentially unboxed) input dictionary):**
    *   `map_key_str_for_error = repr(k)` (for use in error messages).
    *   **If `self.key_type` is `CtyString`:**
        *   If `k` is a raw Python `str`: `validated_key = CtyString().validate(k)`.
        *   If `k` is a `CtyValue` whose `type` is `CtyString`: `validated_key = CtyString().validate(k)`.
        *   If `k` is any other raw Python type (e.g., `int`, `bool`) or a `CtyValue` wrapping a non-`CtyString` type: Raise `CtyStringValidationError(f"Map key must be a string, got raw {type(k).__name__}.")` which will be caught and wrapped by `CtyMapValidationError`.
            *   **Rationale (DX):** For maps declared with string keys, non-string keys are a common error. This provides a direct and clear error message at the map level rather than relying on potentially permissive downstream conversions by `CtyString.validate()` that might mask the original intent or error.
    *   **Else if `self.key_type` is `CtyDynamic`:**
        *   If `k` is a raw Python `str`, `int`, `float`, or `bool`: Convert `k` to its corresponding concrete `CtyValue` (e.g., `CtyString().validate(k)`) and then pass this `CtyValue` to `CtyDynamic().validate()`. This ensures `CtyDynamic` receives a `CtyValue` as it expects for non-None inputs.
        *   If `k` is already a `CtyValue`: `validated_key = CtyDynamic().validate(k)`.
        *   If `k` is other raw type: Raise `CtyValidationError` (e.g. "Raw key type ... not auto-promotable...").
    *   **Else (`self.key_type` is another concrete primitive like `CtyNumber`):**
        *   `validated_key = self.key_type.validate(k)`. (This means `CtyNumber().validate("123")` would convert for a number-keyed map, which is `go-cty` like for *values*, but for *keys* this behavior might need review for strictness if desired. For now, this relies on the primitive type's own validation permissiveness).
    *   **Post Key Validation:**
        *   If `validated_key.is_null` or `validated_key.is_unknown`: Add error `f"Invalid key {map_key_str_for_error}: Map keys cannot be null or unknown."` and continue to the next item.
        *   `map_key_str_internal = str(validated_key.value)` for internal storage.

6.  **Element-wise Value Validation (if key validation passed):**
    *   `validated_value = self.value_type.validate(v)`.
        *   This means if `self.value_type` is `CtyString`, it will use the permissive `CtyString.validate()` logic defined above (e.g., raw `int` `123` becomes `CtyValue(CtyString, "123")`).
    *   Store `map_key_str_internal -> validated_value` and `map_key_str_internal -> validated_key_cty_value` (for original key CtyValue with marks).

7.  **Error Aggregation:**
    *   If any errors were collected (from key or value validation), sort them for deterministic output.
    *   Raise a single `CtyMapValidationError` with a message like "Map validation failed:\n - [error1]\n - [error2]".

## Summary of Key DX/Compatibility Driven Decisions:

*   **`CtyString.validate()`:** Permissive for converting primitives and nulls to string/null-string values. This aligns with `go-cty` for general value contexts.
*   **`CtyMap` with `key_type=CtyString`:** Enforces that keys are provided as actual strings (or `CtyValue(CtyString)`), not just types convertible to string. This enhances DX and predictability for map keying.
*   **`CtyMap` with `key_type=CtyDynamic`:** Raw primitive keys are first promoted to their concrete `CtyValue` before being passed to `CtyDynamic.validate()`.
*   **`CtyMap.usable_as`:** A map with dynamic keys is NOT considered usable as a map requiring concrete keys, for type safety.

This design attempts to provide a `go-cty`-like experience for value flexibility while maintaining reasonable strictness and clarity for map key handling and type compatibility checks.
