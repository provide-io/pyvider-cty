# pyvider-cty/src/pyvider/cty/functions/__init__.py
# This file makes the 'functions' module a package.

# Optionally, you can import functions here to make them available
# directly from pyvider.cty.functions, e.g.:
from .collection_functions import distinct, flatten, sort
from .numeric_functions import (
    add,
    abs_fn,
    ceil_fn,
    floor_fn,
    log_fn,
    parseint_fn,
    pow_fn,
    signum_fn,
)
from .string_functions import (
    chomp,
    indent,
    regex,
    regexall,
    strrev,
    substr,
    title,
    trim,
    trimprefix,
    trimspace,
    trimsuffix,
)

# It's common to alias functions to their typical names (e.g., abs_fn to abs)
# but this can cause conflicts with Python built-ins if not handled carefully.
# For now, keeping the _fn suffix for clarity or until a robust registration/namespacing is in place.

__all__ = [
    # Numeric functions
    "add",
    "abs_fn",
    "ceil_fn",
    # String functions
    "chomp",
    "floor_fn",
    "indent",
    "log_fn",
    "parseint_fn",
    "pow_fn",
    "regex",
    "regexall",
    "signum_fn",
    "strrev",
    "substr",
    "title",
    "trim",
    "trimprefix",
    "trimspace",
    "trimsuffix",
    "distinct",
    "flatten",
    "sort",
]
