# pyvider-cty/src/pyvider/cty/functions/__init__.py
# This file makes the 'functions' module a package.

# Optionally, you can import functions here to make them available
# directly from pyvider.cty.functions, e.g.:
from .string_functions import chomp, strrev, trimspace, indent, substr, trim, title, trimprefix, trimsuffix, regex, regexall
# from .collection_functions import distinct, flatten, sort # Placeholder
from .numeric_functions import abs_fn, ceil_fn, floor_fn, log_fn, pow_fn, signum_fn, parseint_fn

# It's common to alias functions to their typical names (e.g., abs_fn to abs)
# but this can cause conflicts with Python built-ins if not handled carefully.
# For now, keeping the _fn suffix for clarity or until a robust registration/namespacing is in place.

__all__ = [
    # String functions
    "chomp", "indent", "strrev", "substr", "trim", "title", "trimspace",
    "trimprefix", "trimsuffix", "regex", "regexall",
    # Numeric functions
    "abs_fn", "ceil_fn", "floor_fn", "log_fn", "pow_fn", "signum_fn", "parseint_fn",
    # Placeholder for collection functions
]
