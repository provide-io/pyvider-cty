# pyvider-cty/src/pyvider/cty/functions/__init__.py
# This file makes the 'functions' module a package.

# Optionally, you can import functions here to make them available
# directly from pyvider.cty.functions, e.g.:
from .collection_functions import (
    concat,
    contains,
    distinct,
    flatten,
    keys,
    length,
    slice,
    sort,
    values,
)
from .conversion_functions import to_bool, to_number, to_string
from .numeric_functions import (
    abs_fn,
    add,
    ceil_fn,
    divide,
    floor_fn,
    log_fn,
    modulo,
    multiply,
    negate,
    parseint_fn,
    pow_fn,
    signum_fn,
    subtract,
)
from .string_functions import (
    chomp,
    indent,
    lower,
    regex,
    regexall,
    strrev,
    substr,
    title,
    trim,
    trimprefix,
    trimspace,
    trimsuffix,
    upper,
)

# It's common to alias functions to their typical names (e.g., abs_fn to abs)
# but this can cause conflicts with Python built-ins if not handled carefully.
# For now, keeping the _fn suffix for clarity or until a robust registration/namespacing is in place.

__all__ = [
    "abs_fn",
    # Numeric functions
    "add",
    "ceil_fn",
    # String functions
    "chomp",
    "concat",
    "contains",
    "distinct",
    "divide",
    "flatten",
    "floor_fn",
    "indent",
    "keys",
    "length",
    "log_fn",
    "lower",
    "modulo",
    "multiply",
    "negate",
    "parseint_fn",
    "pow_fn",
    "regex",
    "regexall",
    "signum_fn",
    "slice",
    "sort",
    "strrev",
    "substr",
    "subtract",
    "title",
    "to_bool",
    "to_number",
    "to_string",
    "trim",
    "trimprefix",
    "trimspace",
    "trimsuffix",
    "upper",
    "values",
]
