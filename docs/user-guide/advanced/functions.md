# Chapter 11: Functions

`pyvider.cty` provides a rich, built-in standard library of functions for manipulating `cty` values. These functions are type-safe and operate on `CtyValue` instances, returning new `CtyValue` instances.

## Calling Functions

You can call a `cty` function by importing it from the `pyvider.cty.functions` module.

```python
from pyvider.cty import CtyNumber
from pyvider.cty.functions import add, abs_fn

num1 = CtyNumber().validate(10)
num2 = CtyNumber().validate(-20)

# Add two numbers
sum_val = add(num1, num2)
assert sum_val.raw_value == -10

# Get the absolute value
abs_val = abs_fn(num2)
assert abs_val.raw_value == 20
```

## Overview of Available Functions

The standard library is extensive. Below is a categorized overview with function descriptions.

### Numeric Functions

| Function | Description |
|----------|-------------|
| `add` | Add two numbers |
| `subtract` | Subtract second number from first |
| `multiply` | Multiply two numbers |
| `divide` | Divide first number by second |
| `modulo` | Calculate modulo (remainder) of division |
| `pow_fn` | Raise first number to power of second |
| `abs_fn` | Return absolute value of a number |
| `ceil_fn` | Round number up to nearest integer |
| `floor_fn` | Round number down to nearest integer |
| `int_fn` | Convert number to integer (truncate decimals) |
| `log_fn` | Calculate natural logarithm |
| `signum_fn` | Return sign of number (-1, 0, or 1) |
| `parseint_fn` | Parse string as integer in given base |
| `negate` | Negate a number (multiply by -1) |
| `max_fn` | Return maximum of two numbers |
| `min_fn` | Return minimum of two numbers |

### String Functions

| Function | Description |
|----------|-------------|
| `upper` | Convert string to uppercase |
| `lower` | Convert string to lowercase |
| `title` | Convert string to title case |
| `strrev` | Reverse a string |
| `chomp` | Remove trailing newline from string |
| `indent` | Add indentation to each line |
| `trim` | Remove leading and trailing whitespace |
| `trimspace` | Remove all leading/trailing whitespace |
| `trimprefix` | Remove prefix from string if present |
| `trimsuffix` | Remove suffix from string if present |
| `join` | Join list of strings with separator |
| `split` | Split string by separator into list |
| `replace` | Replace occurrences of substring |
| `substr` | Extract substring by position and length |
| `strlen` | Return the length of a string, in grapheme clusters |
| `format_fn` | Render a printf-style template (go-cty's dialect) |
| `formatlist` | Render a printf-style template once per element of its list arguments |
| `regex` | Match string against regular expression |
| `regexall` | Find all regex matches in string |
| `regexreplace` | Replace regex matches in string |

`regex` and `regexall` take the pattern first and the subject string second — `regex(pattern, string)`, matching go-cty rather than Python's `re` module. Both arguments are strings, so a call written with the arguments the other way round still type-checks; it just matches against the wrong thing. `regex` returns the capture groups rather than the whole match — a tuple for unnamed groups, an object for named ones, or the whole match itself when the pattern has no groups — and raises if the pattern does not match rather than returning an empty string:

```python
from pyvider.cty import CtyString
from pyvider.cty.functions import regex

email = CtyString().validate("bob@example.com")
pattern = CtyString().validate(r"(\w+)@([\w.]+)")
user, domain = regex(pattern, email).value
assert user.value == "bob"
assert domain.value == "example.com"
```

All three regex functions run on Python's `re`, which backtracks, rather than go-cty's RE2, which is linear-time. A pattern like `(a+)+$` against a long non-matching string can take exponential time, and `re` has no timeout to cap it. This is accepted on the assumption that patterns come from provider configuration written by the operator running Terraform — the same trust as every other expression in that configuration. If your code evaluates patterns from a less trusted source (a remote API, end-user input), bound them yourself with an allow-list or a process-level timeout; the library does not. The [go-cty comparison](../../reference/go-cty-comparison.md) lists the other ways `re` and RE2 differ.

`indent` takes a *number of spaces*, not a prefix string, and only indents lines after the first — it exists to line a multi-line value up under something already on the line above it, not to indent a block uniformly.

### Collection Functions

| Function | Description |
|----------|-------------|
| `length` | Return number of elements in a collection; refuses a string, use `strlen` for that |
| `slice` | Extract subset of list elements |
| `concat` | Concatenate multiple lists |
| `contains` | Check if collection contains value |
| `reverse` | Reverse order of list elements |
| `distinct` | Remove duplicate elements from list |
| `flatten` | Flatten nested sequences into a single tuple, recursing through every level |
| `sort` | Sort list elements |
| `keys` | Get keys from map or object |
| `values` | Get values from map or object |
| `lookup` | Look up value in map by key with default |
| `merge` | Merge multiple maps into one |
| `zipmap` | Create map from list of keys and list of values |
| `element` | Get element at specific index (with wraparound) |
| `chunklist` | Split list into chunks of specified size |
| `setproduct` | Calculate Cartesian product of sets |
| `compact` | Remove null/empty values from list |
| `coalescelist` | Return first non-empty list |
| `index` | Find index of value in list |
| `hasindex` | Check if collection has element at index |
| `range_fn` | Generate a list of numbers over a range, like Python's `range` |

### Set Functions

| Function | Description |
|----------|-------------|
| `setunion` | Union of two or more sets |
| `setintersection` | Intersection of two or more sets |
| `setsubtract` | Elements in the first set but not the second |
| `setsymmetricdifference` | Elements in exactly one of two or more sets |
| `sethaselement` | Check if a set contains a value |

### Boolean Functions

| Function | Description |
|----------|-------------|
| `and_fn` | Logical AND of two booleans |
| `or_fn` | Logical OR of two booleans |
| `not_fn` | Logical negation of a boolean |

### Comparison Functions

| Function | Description |
|----------|-------------|
| `equal` | Test if two values are equal |
| `not_equal` | Test if two values are not equal |
| `greater_than` | Test if first > second |
| `less_than` | Test if first < second |
| `greater_than_or_equal_to` | Test if first >= second |
| `less_than_or_equal_to` | Test if first <= second |

### Type Conversion Functions

| Function | Description |
|----------|-------------|
| `to_string` | Convert value to string |
| `to_number` | Convert value to number |
| `to_bool` | Convert value to boolean |

### Encoding Functions

| Function | Description |
|----------|-------------|
| `jsonencode` | Encode value as JSON string |
| `jsondecode` | Decode JSON string to value |
| `csvdecode` | Decode CSV string to a list of objects, one per row, with every column typed as a string |

### Date/Time Functions

| Function | Description |
|----------|-------------|
| `formatdate` | Format timestamp string using format spec |
| `timeadd` | Add duration to timestamp |

### Bytes Functions

| Function | Description |
|----------|-------------|
| `byteslen` | Return length of bytes value |
| `bytesslice` | Extract slice of bytes |

### Structural Functions

| Function | Description |
|----------|-------------|
| `coalesce` | Return first non-null value from arguments |
| `assertnotnull` | Return the value unchanged, or raise if it is null |

For complete API documentation with detailed signatures and examples, see the **[Functions API Reference](../../api/functions.md)**.
