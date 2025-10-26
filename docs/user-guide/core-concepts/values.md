# Working with Values

In `pyvider.cty`, a "value" is an instance of a `cty` type. Values are the lifeblood of the `cty` system, as they hold the actual data that you work with.

## The `CtyValue` Class

All `pyvider.cty` values are instances of the `CtyValue` class. This class provides the common interface for all values, including methods for accessing the raw data and performing type-safe operations.

### Accessing the Raw Value

You can access the underlying, native Python representation of a `cty` value using the `.raw_value` property:

```python
from pyvider.cty import CtyString

string_val = CtyString().validate("hello")
raw_string = string_val.raw_value

assert raw_string == "hello"
```

### Immutability

One of the key features of `cty` values is that they are **immutable**. This means that once a value is created, it cannot be changed. This has several advantages:

*   **Predictability**: It makes your code more predictable, as you can be sure that a value will not change unexpectedly.
*   **Safety**: It helps to prevent bugs caused by unintended side effects.
*   **Concurrency**: It makes it easier to write concurrent code, as you don't have to worry about race conditions when accessing values.

## Special Values: Null and Unknown

In addition to regular values, `pyvider.cty` has two special kinds of values:

1.  **Null Values**: A null value represents the explicit absence of a value.
2.  **Unknown Values**: An unknown value represents a value that is not yet known but will be populated later.

You can create these using the class methods on `CtyValue`:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue

# 1. Define a user profile type.
profile_type = CtyObject(
    attribute_types={
        "username": CtyString(),
        "age": CtyNumber(),
    },
)

# 2. Create an unknown value of the profile type.
# This represents a value that will be known later (e.g., after an API call).
unknown_value = CtyValue.unknown(profile_type)

# 3. Create a null value of the profile type.
# This represents an explicit absence of a value.
null_value = CtyValue.null(profile_type)

# 4. Check the state of each value.
print(f"Unknown Value: Is Unknown? {unknown_value.is_unknown}, Is Null? {unknown_value.is_null}")
print(f"Null Value:    Is Unknown? {null_value.is_unknown}, Is Null? {null_value.is_null}")

# Accessing properties of a null or unknown value would raise an error.
try:
    _ = null_value["username"]
except TypeError as e:
    print(f"Attempting to access null value property failed as expected: {e}")
```

### Refined Unknown Values

`pyvider.cty` supports **refined unknowns**, which are unknown values that carry additional refinement information. This feature is particularly useful in scenarios like Terraform planning, where you know that a value will be computed later but can provide constraints about what that value will be.

Refined unknowns allow you to specify partial information about an unknown value, such as:
- Range constraints for numbers
- String prefix/suffix constraints
- Collection length constraints

```python
from pyvider.cty.values import UnknownValue, RefinedUnknownValue
from pyvider.cty import CtyNumber, CtyString

# Create a basic unknown value
basic_unknown = UnknownValue(CtyNumber())
print(f"Basic unknown: {basic_unknown.is_unknown}")  # True

# Create a refined unknown value (advanced usage)
# Note: RefinedUnknownValue is typically used internally by the type system
# or in advanced scenarios like Terraform provider development
refined_unknown = RefinedUnknownValue(
    vtype=CtyNumber(),
    refinement=None  # Refinement constraints (implementation-specific)
)
```

**When to use refined unknowns:**
- **Terraform providers**: During the plan phase when values will be known during apply
- **Validation**: When you need to validate that constraints will be satisfied even though the actual value is unknown
- **Type propagation**: In function implementations where unknowns need to propagate with refinements

**Note**: Most users will work with regular unknown values via `CtyValue.unknown()`. Refined unknowns are an advanced feature primarily used in infrastructure-as-code scenarios and by library implementers.

## Immutable Updates with Helper Methods

Since `CtyValue` objects are immutable, you create modified versions instead of changing them in-place. `pyvider.cty` provides convenient helper methods on collection values for this purpose.

```python
from pyvider.cty import CtyMap, CtyNumber

# 1. Define a map type and create an initial CtyValue.
config_type = CtyMap(element_type=CtyNumber())
config_val = config_type.validate({"timeout": 30})

# 2. Use .with_key() to add/update an element, returning a NEW value.
new_config_val = config_val.with_key("batch_size", 500).with_key("timeout", 60)

# 3. Use .without_key() to remove an element, returning a NEW value.
final_config_val = new_config_val.without_key("timeout")

print(f"Original: {config_val.raw_value}")
print(f"Updated:  {new_config_val.raw_value}")
print(f"Final:    {final_config_val.raw_value}")
```

Similar methods like `.append()` and `.with_element_at()` exist for `CtyList` values.
