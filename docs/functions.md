# Functions

`pyvider.cty` provides a set of built-in functions for manipulating `CtyValue`s. These functions are available in the `pyvider.cty.functions` module.

## String Functions

*   `chomp(input_val)`: Removes a trailing newline from a string.
*   `strrev(input_val)`: Reverses a string.
*   `trimspace(input_val)`: Removes leading and trailing whitespace from a string.
*   `indent(prefix_val, input_val)`: Indents each line of a string with a prefix.
*   `substr(input_val, offset_val, length_val)`: Returns a substring of a string.
*   `trim(input_val, cutset_val)`: Removes leading and trailing characters from a string.
*   `title(input_val)`: Converts a string to title case.
*   `trimprefix(input_val, prefix_val)`: Removes a prefix from a string.
*   `trimsuffix(input_val, suffix_val)`: Removes a suffix from a string.
*   `regex(pattern_val, input_val)`: Returns `True` if a string matches a regular expression.
*   `regexall(pattern_val, input_val)`: Returns a list of all matches of a regular expression in a string.

## Numeric Functions

*   `abs_fn(input_val)`: Returns the absolute value of a number.
*   `ceil_fn(input_val)`: Returns the smallest integer greater than or equal to a number.
*   `floor_fn(input_val)`: Returns the largest integer less than or equal to a number.
*   `log_fn(num_val, base_val)`: Returns the logarithm of a number in a given base.
*   `pow_fn(num_val, power_val)`: Returns a number raised to the power of another number.
*   `signum_fn(input_val)`: Returns the sign of a number.
*   `parseint_fn(str_val, base_val)`: Parses a string to an integer in a given base.

## Collection Functions

*   `distinct(input_val)`: Removes duplicate elements from a list.
*   `flatten(input_val)`: Flattens a list of lists into a single list.
*   `sort(input_val)`: Sorts the elements of a list.
