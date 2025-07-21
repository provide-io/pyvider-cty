# Chapter 11: Functions

`pyvider.cty` provides a rich set of built-in functions for manipulating `cty` values. These functions are type-safe, meaning that they will only work with the correct types of values.

## Calling Functions

You can call a `cty` function by using its corresponding Python function from the `pyvider.cty.functions` module.

For example, to call the `add` function, you would use the `cty_add` function:

```python
from pyvider.cty import CtyNumber
from pyvider.cty.functions import cty_add

num1 = CtyNumber(10)
num2 = CtyNumber(20)

result = cty_add(num1, num2)

assert result.raw_value == 30
```

## Categories of Functions

The built-in functions in `pyvider.cty` can be divided into several categories:

### Numeric Functions

*   `cty_add`: Adds two numbers.
*   `cty_subtract`: Subtracts one number from another.
*   `cty_multiply`: Multiplies two numbers.
*   `cty_divide`: Divides one number by another.
*   `cty_modulo`: Computes the remainder of a division.
*   `cty_power`: Raises a number to a power.
*   `cty_negate`: Negates a number.

### String Functions

*   `cty_concat`: Concatenates two or more strings.
*   `cty_length`: Returns the length of a string.
*   `cty_slice`: Extracts a slice of a string.
*   `cty_upper`: Converts a string to uppercase.
*   `cty_lower`: Converts a string to lowercase.

### Collection Functions

*   `cty_length`: Returns the number of elements in a list, set, or map.
*   `cty_slice`: Extracts a slice of a list.
*   `cty_concat`: Concatenates two or more lists.
*   `cty_contains`: Checks if a list or set contains a specific element.
*   `cty_keys`: Returns a list of the keys in a map.
*   `cty_values`: Returns a list of the values in a map.

### Type Conversion Functions

*   `cty_to_string`: Converts a value to a string.
*   `cty_to_number`: Converts a value to a number.
*   `cty_to_bool`: Converts a value to a boolean.

This is just a selection of the available functions. For a complete list, please refer to the API reference.
