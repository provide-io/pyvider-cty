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

The standard library is extensive. Below is a categorized overview of some of the most common functions.

### Numeric Functions
- `add`, `subtract`, `multiply`, `divide`, `modulo`, `pow_fn`
- `abs_fn`, `ceil_fn`, `floor_fn`, `int_fn`
- `log_fn`, `signum_fn`, `parseint_fn`

### String Functions
- `upper`, `lower`, `title`, `strrev`
- `chomp`, `indent`, `trim`, `trimspace`, `trimprefix`, `trimsuffix`
- `join`, `split`, `replace`, `substr`
- `regex`, `regexall`, `regexreplace`

### Collection Functions
- `length`, `slice`, `concat`, `contains`, `reverse`
- `distinct`, `flatten`, `sort`
- `keys`, `values` (for maps and objects)
- `lookup`, `merge`, `zipmap` (for maps)
- `element`, `chunklist`, `setproduct`

### Comparison Functions
- `equal`, `not_equal`
- `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`
- `max_fn`, `min_fn`

### Type Conversion Functions
- `to_string`, `to_number`, `to_bool`

### Encoding Functions
- `jsonencode`, `jsondecode`, `csvdecode`

### Date/Time Functions
- `formatdate`, `timeadd`

### Structural and Logical Functions
- `coalesce`, `coalescelist`

For a complete list and function signatures, please refer to the source code in `src/pyvider/cty/functions/`.
