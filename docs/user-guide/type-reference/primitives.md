# Primitive Types

Primitive types are the most basic building blocks of the `pyvider.cty` type system. They represent simple, single values.

There are three primitive types in `pyvider.cty`:

*   `CtyString`: Represents a string of text.
*   `CtyNumber`: Represents a number (integer or float).
*   `CtyBool`: Represents a boolean value (`True` or `False`).

## `CtyString`

The `CtyString` type represents a string of text. You can create a `CtyString` type and use it to validate raw Python strings:

```python
from pyvider.cty import CtyString

string_type = CtyString()

# Validate a valid string
cty_string = string_type.validate("hello")
assert cty_string.raw_value == "hello"

# Validate an invalid value (will raise a ValidationError)
try:
    string_type.validate(123)
except Exception as e:
    print(f"Validation failed: {e}")
```

## `CtyNumber`

The `CtyNumber` type represents a number. It can be an integer or a float.

```python
from pyvider.cty import CtyNumber

number_type = CtyNumber()

# Validate a valid integer
cty_int = number_type.validate(123)
assert cty_int.raw_value == 123

# Validate a valid float
cty_float = number_type.validate(3.14)
assert cty_float.raw_value == 3.14

# Validate an invalid value (will raise a ValidationError)
try:
    number_type.validate("hello")
except Exception as e:
    print(f"Validation failed: {e}")
```

## `CtyBool`

The `CtyBool` type represents a boolean value (`True` or `False`).

```python
from pyvider.cty import CtyBool

bool_type = CtyBool()

# Validate a valid boolean
cty_true = bool_type.validate(True)
assert cty_true.raw_value is True

# Validate an invalid value (will raise a ValidationError)
try:
    bool_type.validate(1)
except Exception as e:
    print(f"Validation failed: {e}")
```

## See Also

- **[Understanding Types](../core-concepts/types.md)** - Core type system concepts
- **[Collection Types](collections.md)** - List, Map, and Set types
- **[Structural Types](structural.md)** - Object and Tuple types
- **[String Functions](../advanced/functions.md)** - Built-in string manipulation functions
- **[Numeric Functions](../advanced/functions.md)** - Built-in numeric operations
