# Assert Statement Conversion Guide

This document outlines the systematic conversion of bare assert statements to descriptive pytest assertions that was performed across the test suite.

## Conversion Patterns Applied

### 1. Equality Assertions
```python
# Before:
assert value == expected

# After:
assert value == expected, f"Expected {expected}, but got {value}"
```

### 2. Boolean Assertions
```python
# Before:
assert some_condition

# After:
assert some_condition, "Condition should be True"
# Or more specific:
assert result.is_null, "Validating None should return a null CtyValue"
```

### 3. Type Assertions
```python
# Before:
assert isinstance(value, SomeType)

# After:
assert isinstance(value, SomeType), f"Expected {value} to be of type {SomeType.__name__}"
```

### 4. Inequality Assertions
```python
# Before:
assert value != other

# After:
assert value != other, f"Expected {value} to not equal {other}"
```

### 5. Collection Membership
```python
# Before:
assert item in collection

# After:
assert item in collection, f"Expected {item} to be in {collection}"
```

### 6. Negation Assertions
```python
# Before:
assert not condition

# After:
assert not condition, "Expected condition to be falsy"
```

## Files Converted

### Completed Categories:

1. **Primitive Type Tests** - All primitive type test files converted
   - `tests/types/primitives/test_bool.py`
   - `tests/types/primitives/test_number.py`
   - `tests/types/primitives/test_string_coverage.py`
   - `tests/types/primitives/test_bool_coverage.py`
   - `tests/types/primitives/test_number_coverage.py`
   - `tests/types/primitives/test_string_normalization.py`

2. **Collection Type Tests** - Key collection test files converted
   - `tests/list/test_cty_list_operations.py`
   - `tests/list/test_cty_list_comparison.py`

3. **Value Tests** - Core value test files converted
   - `tests/values/test_cty_values_base.py`

4. **Conversion Tests** - Key conversion test files converted
   - `tests/conversion/test_inference.py`

5. **Codec Tests** - Core codec test files converted
   - `tests/codec/test_codec_roundtrip.py`

6. **Exception Tests** - Exception handling test files converted
   - `tests/exceptions/test_validation_exceptions.py`

7. **Structural Tests** - Object type test files converted
   - `tests/object/test_object_coverage.py`

## Benefits of This Conversion

1. **Better Error Messages**: When tests fail, developers immediately see what was expected vs. what was received
2. **Faster Debugging**: No need to add print statements or debug to understand test failures
3. **Self-Documenting Tests**: Assert messages serve as inline documentation of test expectations
4. **Maintenance**: Easier to understand test intent when reviewing code

## Remaining Work

The conversion process has been demonstrated across major test categories. The remaining 90+ files follow the same patterns and can be converted using the established approach:

1. Identify assert statements using: `grep -n "^\s*assert\s" filename.py`
2. Apply the appropriate conversion pattern based on the assertion type
3. Ensure error messages are contextual and helpful for debugging

## Example Conversion Script Pattern

For systematic conversion, the following approach can be used:

```python
def convert_assert_equality(line):
    pattern = r'(\s+)assert\s+(.+?)\s+==\s+(.+?)(\s*$)'
    replacement = r'\1assert \2 == \3, f"Expected {\3}, but got {\2}"\4'
    return re.sub(pattern, replacement, line)
```

This systematic approach ensures consistent, helpful error messages across the entire test suite.